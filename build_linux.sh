#!/usr/bin/env bash
# Build dist/HungryFrog-linux (one file, runs on most 64-bit Linux: Ubuntu 20.04+, Debian 11+, Mint, Arch...)
set -e
cd "$(dirname "$0")"
docker run --rm -v "$PWD":/src -w /src python:3.12-bullseye bash -c '
  pip install -q pygame-ce pyinstaller &&
  pyinstaller --noconfirm --clean --onefile --windowed --name HungryFrog-linux \
      --distpath dist --workpath build/linux --specpath build/linux \
      --add-data "/src/assets:assets" hungry_frog.py &&
  chown -R '"$(id -u):$(id -g)"' dist build
'
echo "Built: dist/HungryFrog-linux"
