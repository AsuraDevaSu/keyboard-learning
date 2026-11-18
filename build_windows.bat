@echo off
REM Build HungryFrog.exe on a Windows PC (needs Python 3.10+ from python.org)
cd /d "%~dp0"
python -m pip install pygame-ce pyinstaller pillow || goto :err
python -m PyInstaller --noconfirm --clean --onefile --windowed --noupx --name HungryFrog --icon assets\icon.png --add-data "assets;assets" hungry_frog.py || goto :err
echo.
echo Done! Your game is in: dist\HungryFrog.exe
pause
exit /b 0
:err
echo Build failed.
pause
