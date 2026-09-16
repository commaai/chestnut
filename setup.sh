#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$PATH"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.cache/uv}"

as_root=()
if [ "$EUID" -ne 0 ]; then as_root=(sudo); fi
run_root() {
  if [ "$EUID" -ne 0 ] && ! command -v sudo >/dev/null; then
    echo 'Install sudo or run ./setup.sh as root.' >&2
    return 1
  fi
  "${as_root[@]}" "$@"
}

if ! command -v clang >/dev/null || ! command -v curl >/dev/null ||
   ! ldconfig -p 2>/dev/null | grep -E 'libLLVM(-|\.so\.)(19|20|21)' >/dev/null ||
   ! ldconfig -p 2>/dev/null | grep -F 'libusb-1.0.so' >/dev/null; then
  if command -v apt-get >/dev/null; then
    run_root apt-get update
    llvm_package=llvm
    for version in 21 20 19; do
      if apt-cache show "libllvm$version" >/dev/null 2>&1; then llvm_package="libllvm$version"; break; fi
    done
    run_root apt-get install -y --no-install-recommends ca-certificates curl clang "$llvm_package" libusb-1.0-0
  elif command -v dnf >/dev/null; then
    run_root dnf install -y clang llvm-libs libusb1 curl
  elif command -v pacman >/dev/null; then
    run_root pacman -S --needed --noconfirm clang llvm-libs libusb curl
  elif command -v zypper >/dev/null; then
    run_root zypper --non-interactive install clang llvm libusb-1_0-0 curl
  else
    echo 'Install clang, curl, LLVM 19+, and libusb with your package manager.' >&2
    exit 1
  fi
fi

# Like openpilot, allow access to the device without running examples as root.
if [ -d /etc/udev/rules.d ] && command -v udevadm >/dev/null &&
   [[ ",$(findmnt -n -o OPTIONS -T /etc/udev/rules.d)," != *,ro,* ]]; then
  rules='SUBSYSTEM=="usb", ATTR{idVendor}=="3801", ATTR{idProduct}=="0001", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="add1", ATTR{idProduct}=="0001", MODE="0666"'
  if [ "$(cat /etc/udev/rules.d/11-chestnut.rules 2>/dev/null || true)" != "$rules" ]; then
    run_root tee /etc/udev/rules.d/11-chestnut.rules >/dev/null <<< "$rules"
    run_root udevadm control --reload-rules && run_root udevadm trigger --subsystem-match=usb || true
  fi
fi

if ! command -v uv >/dev/null; then
  curl --retry 5 --retry-delay 5 --retry-all-errors -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
fi
uv sync --locked --python 3.12
.venv/bin/python tools/export.py
if [ ! -f zidane.jpg ]; then
  mkdir -p .cache
  curl --retry 5 --retry-delay 5 --retry-all-errors -fLsS https://ultralytics.com/images/zidane.jpg -o .cache/zidane.jpg
  mv .cache/zidane.jpg zidane.jpg
fi

echo "Ready. PC: .venv/bin/python examples/02_vision.py zidane.jpg"
echo "Chestnut: DEV=USB+AMD:LLVM .venv/bin/python examples/02_vision.py zidane.jpg"
