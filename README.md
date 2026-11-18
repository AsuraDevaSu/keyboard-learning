# Hungry Frog 🐸 / កង្កែបឃ្លាន — typing game for kids

Bugs fly over the pond with letters on them. Type the letter and the frog catches the bug!

## Play (Linux)
    ./run.sh

## Make the Windows .exe
- **On this Linux PC (Docker):** `./build_windows.sh` → `dist/HungryFrog.exe`
- **On a Windows PC:** install Python from python.org, double-click `build_windows.bat` → `dist\HungryFrog.exe`

Copy `HungryFrog.exe` to any Windows 10/11 PC and double-click it. No install needed.

## Make the Linux program
`./build_linux.sh` → `dist/HungryFrog-linux` (runs on Ubuntu 20.04+, Debian 11+, Mint, Arch...).
Copy it to the other PC, then: `chmod +x HungryFrog-linux && ./HungryFrog-linux`
On Linux, progress is saved in `~/HungryFrog/save.json`.

## Check a build works
`HungryFrog.exe --selftest out` (or `./HungryFrog-linux --selftest out`) plays every screen
automatically and saves screenshots in the `out` folder.
On Windows, student progress is saved in `%APPDATA%\HungryFrog\save.json`.

## Features
- **Students**: "Who is playing?" screen. Each student has their own stars, speed and tricky keys.
- **Khmer / English**: language button on the student and title screens.
- **Hand Lesson**: hands on the keyboard show where every finger goes (home row A S D F / J K L ;).
- **18 levels**: F J → home row → top row → bottom row → words. Each level starts with "press F and J".
- **Music**: two original tunes (menu + game). Note button or F8 = music on/off. F11 = full screen.
  Tunes are made by `tools/make_music.py` (edit the notes there, re-run it, then rebuild).
- **Stars**: 3 stars = 95%+ accuracy. 1 star unlocks the next level.
