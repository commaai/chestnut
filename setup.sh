#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$PATH"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.cache/uv}"

if [ ! -f /AGNOS ] && command -v apt-get >/dev/null; then
  missing=()
  for package in ca-certificates git curl clang libllvm20 libusb-1.0-0; do
    if [ "$(dpkg-query -W -f='${db:Status-Status}' "$package" 2>/dev/null || true)" != installed ]; then
      missing+=("$package")
    fi
  done
  if [ ${#missing[@]} -gt 0 ]; then
    as_root=()
    if [ "$EUID" -ne 0 ]; then as_root=(sudo); fi
    "${as_root[@]}" apt-get update
    "${as_root[@]}" apt-get install -y "${missing[@]}"
  fi
fi

if ! command -v uv >/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
fi

git submodule update --init --depth 1
uv sync --locked --python 3.12 --extra speech "$@"
