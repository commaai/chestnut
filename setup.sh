#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"
export UV_CACHE_DIR="$PWD/.cache/uv"
export TORCH_HOME="$PWD/.cache/torch"
export UV_HTTP_TIMEOUT=200 UV_HTTP_RETRIES=5
mkdir -p .cache

as_root=()
if [ "$EUID" -ne 0 ]; then as_root=(sudo); fi
for directory in .cache .venv models frames; do
  if [ -d "$directory" ] && [ -n "$(find "$directory" ! -user "$(id -un)" -print -quit)" ]; then
    "${as_root[@]}" chown -R "$(id -u):$(id -g)" "$directory"
  fi
done
download() { curl --retry 5 --retry-delay 5 --retry-all-errors -fLsS "$1" -o "$2"; }

case "$(uname -s):$(uname -m)" in
  Linux:x86_64|Linux:aarch64)
    getconf GNU_LIBC_VERSION >/dev/null || { echo 'glibc Linux is required.' >&2; exit 1; }
    ;;
  Darwin:arm64)
    [ "$(sw_vers -productVersion | cut -d. -f1)" -ge 14 ] || { echo 'macOS 14+ is required.' >&2; exit 1; }
    command -v brew >/dev/null || { echo 'Install Homebrew and rerun setup.' >&2; exit 1; }
    brew list --versions llvm@21 libusb >/dev/null 2>&1 || brew install llvm@21 libusb
    export PATH="/opt/homebrew/opt/llvm@21/bin:$PATH"
    ;;
  *) echo 'Use x86_64/aarch64 Linux or Apple Silicon macOS 14+.' >&2; exit 1 ;;
esac

if [ "$(uname -s)" = Linux ] && { ! command -v clang >/dev/null || ! command -v curl >/dev/null ||
   ! command -v awk >/dev/null || ! command -v tar >/dev/null || ! command -v gzip >/dev/null ||
   ! ldconfig -p 2>/dev/null | grep -E 'libLLVM(-|\.so\.)(19|20|21)' >/dev/null ||
   ! ldconfig -p 2>/dev/null | grep -F 'libusb-1.0.so' >/dev/null; }; then
  if command -v apt-get >/dev/null; then
    "${as_root[@]}" apt-get update
    llvm_package=
    for version in 21 20 19; do
      if apt-cache show "libllvm$version" >/dev/null 2>&1; then llvm_package="libllvm$version"; break; fi
    done
    if [ -z "$llvm_package" ]; then
      # Ubuntu 22.04 and Debian 12 need upstream LLVM for the GPU compiler.
      . /etc/os-release
      codename="${UBUNTU_CODENAME:-${VERSION_CODENAME:-}}"
      case "$codename" in
        jammy|bookworm) ;;
        *) echo 'Install LLVM 19–21 and rerun setup.' >&2; exit 1 ;;
      esac
      "${as_root[@]}" apt-get install -y --no-install-recommends ca-certificates curl
      download https://apt.llvm.org/llvm-snapshot.gpg.key .cache/llvm.asc
      "${as_root[@]}" install -Dm644 .cache/llvm.asc /etc/apt/keyrings/chestnut-llvm.asc
      echo "deb [signed-by=/etc/apt/keyrings/chestnut-llvm.asc] https://apt.llvm.org/$codename/ llvm-toolchain-$codename-20 main" |
        "${as_root[@]}" tee /etc/apt/sources.list.d/chestnut-llvm.list >/dev/null
      "${as_root[@]}" apt-get update
      llvm_package=libllvm20
    fi
    "${as_root[@]}" apt-get install -y --no-install-recommends ca-certificates curl clang "$llvm_package" libusb-1.0-0 gawk tar gzip
  elif command -v dnf >/dev/null; then
    "${as_root[@]}" dnf install -y ca-certificates clang llvm-libs libusb1 curl gawk tar gzip
  elif command -v pacman >/dev/null; then
    "${as_root[@]}" pacman -Syu --needed --noconfirm ca-certificates clang llvm20-libs libusb curl gawk tar gzip
  elif command -v zypper >/dev/null; then
    "${as_root[@]}" zypper --non-interactive refresh
    "${as_root[@]}" zypper --non-interactive install ca-certificates clang libLLVM20 libusb-1_0-0 curl gawk tar gzip
  else
    echo 'Install clang, curl, LLVM 19–21, and libusb with your package manager.' >&2
    exit 1
  fi
fi

if [ -d /etc/udev/rules.d ] && command -v udevadm >/dev/null && command -v findmnt >/dev/null &&
   [[ ",$(findmnt -n -o OPTIONS -T /etc/udev/rules.d)," != *,ro,* ]]; then
  rules='SUBSYSTEM=="usb", ATTR{idVendor}=="3801", ATTR{idProduct}=="0001", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="add1", ATTR{idProduct}=="0001", MODE="0666"'
  if [ "$(cat /etc/udev/rules.d/11-chestnut.rules 2>/dev/null || true)" != "$rules" ]; then
    "${as_root[@]}" tee /etc/udev/rules.d/11-chestnut.rules >/dev/null <<< "$rules"
    if "${as_root[@]}" udevadm control --reload-rules; then
      "${as_root[@]}" udevadm trigger --subsystem-match=usb || true
    fi
  fi
fi

if ! command -v uv >/dev/null; then
  download https://astral.sh/uv/install.sh .cache/install-uv.sh
  UV_NO_MODIFY_PATH=1 sh .cache/install-uv.sh
fi
unset VIRTUAL_ENV
uv sync --locked --python 3.12
.venv/bin/python tools/setup.py
echo 'Preparing models...'
.venv/bin/python tools/export.py
echo 'Ready. Activate with: source .venv/bin/activate'
