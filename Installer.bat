@echo off
setlocal
title PyTorch-Calculator Installer

echo.
echo PyTorch-Calculator Installer
echo ----------------------------
echo.

cd /d %~dp0


if exist "%cd%\python" (
    echo PyTorch-Calculator is already installed, press enter to reinstall!
    echo.
    pause
    echo.
)


set "PythonUrl=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
set "PythonSavePath=%cd%\Python-3.11.9.zip"

echo Downloading Python...
where curl >nul 2>&1
if %errorlevel% equ 0 (
    curl -s -o "%PythonSavePath%" "%PythonUrl%" >nul 2>&1
) else (
    powershell -Command "$ProgressPreference = 'SilentlyContinue'; $wc = New-Object System.Net.WebClient; $wc.DownloadFile('%PythonUrl%', '%PythonSavePath%')"
)


set "PythonZipPath=%PythonSavePath%"
set "PythonExtractPath=%cd%\python"

echo Extracting Python...

if exist "%PythonExtractPath%" (
    rmdir /s /q "%PythonExtractPath%"
)

mkdir "%PythonExtractPath%" >nul 2>&1
powershell -Command "$ProgressPreference = 'SilentlyContinue'; Expand-Archive -Path '%PythonZipPath%' -DestinationPath '%PythonExtractPath%' -Force"


echo Installing pip...

set "PipUrl=https://bootstrap.pypa.io/get-pip.py"
set "PipSavePath=%PythonExtractPath%\get-pip.py"

where curl >nul 2>&1
if %errorlevel% equ 0 (
    curl -s -o "%PipSavePath%" "%PipUrl%" >nul 2>&1
) else (
    powershell -Command "$ProgressPreference = 'SilentlyContinue'; $wc = New-Object System.Net.WebClient; $wc.DownloadFile('%PipUrl%', '%PipSavePath%')"
)

"%PythonExtractPath%\python.exe" "%PipSavePath%" >nul 2>&1


echo Editing installations...

set "PthFilePath=%PythonExtractPath%\python311._pth"

if exist "%PthFilePath%" (
    echo Lib\site-packages >> "%PthFilePath%"
    powershell -Command "$ProgressPreference = 'SilentlyContinue'; (gc '%PthFilePath%') -replace '#import site','import site' | Out-File -encoding ASCII '%PthFilePath%'"
) else (
    echo ERROR: File not found: %PthFilePath%
    pause
)

if exist "%PythonSavePath%" (
    del "%PythonSavePath%"
)


echo Editing environment...

set "PATH=%PythonExtractPath%;%PythonExtractPath%\Scripts"


echo Installing requirements...

python -m pip install -r config/requirements.txt -q


echo Done.
echo.


echo Python Version:
python  --version
echo.

echo Pip Version:
python -m pip --version
echo.

echo Pip Packages:
python -m pip list


echo.
echo App Installed
echo -------------
echo.

endlocal
pause