#!/usr/bin/env bash
# Build dist/HungryFrog.exe (Windows 10/11, 64-bit) from Linux using Docker + Wine.
set -e
cd "$(dirname "$0")"
docker run --rm -v "$PWD":/src -w /src -e HOST_UID="$(id -u)" -e HOST_GID="$(id -g)" tobix/pywine:3.12 bash -c '
  wine python -m pip install -q pygame-ce pyinstaller pillow &&
  wine pyinstaller --noconfirm --clean --onefile --windowed --noupx --name HungryFrog \
       --distpath dist --workpath build/win --specpath build/win \
       --icon Z:/src/assets/icon.png --add-data "Z:/src/assets;assets" hungry_frog.py &&
  chown -R "$HOST_UID:$HOST_GID" dist build
'
echo "Built: dist/HungryFrog.exe"
