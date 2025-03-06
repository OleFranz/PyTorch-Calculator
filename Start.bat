@echo off
setlocal
title PyTorch-Calculator Console

echo.
echo PyTorch-Calculator
echo ------------------
echo.

cd /d %~dp0

set "PATH=%cd%\python\Scripts;%cd%\python"

if not exist "%cd%\python" (
    echo PyTorch-Calculator is not installed, use the Installer.bat to install it!
    echo.
    goto :end
)

python app/main.py %*

:end
endlocal
pause