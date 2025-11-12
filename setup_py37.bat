@echo off
REM Setup script - Create Python 3.7 venv and install pybind11
REM Created by: nicrf with assistance from Claude AI
REM Date: 2024-11-09

echo ================================================
echo RVO3D - Python 3.7 Environment Setup
echo ================================================
echo.

REM Python path
set PYTHON_PATH=C:\Users\Nic_r\.pyenv\pyenv-win\versions\3.7.4\python.exe

REM Check if Python exists
if not exist "%PYTHON_PATH%" (
    echo ERROR: Python 3.7 not found at %PYTHON_PATH%
    echo Please install Python 3.7 or adjust PYTHON_PATH in this script
    pause
    exit /b 1
)

echo Found Python: %PYTHON_PATH%
%PYTHON_PATH% --version
echo.

REM Create virtual environment
if not exist "venv37" (
    echo Creating Python 3.7 virtual environment...
    %PYTHON_PATH% -m venv venv37
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Make sure Python 3.7 has venv module installed
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
    echo.
) else (
    echo Virtual environment already exists
    echo.
)

REM Activate and install pybind11
echo Installing pybind11 in virtual environment...
venv37\Scripts\pip.exe install pybind11==2.13.6
if errorlevel 1 (
    echo ERROR: Failed to install pybind11
    pause
    exit /b 1
)

echo.
echo ================================================
echo Setup complete!
echo ================================================
echo.
echo Virtual environment: venv37
echo PyBind11 version: 2.13.6
echo.
echo To verify installation:
echo   venv37\Scripts\python.exe -c "import pybind11; print('PyBind11:', pybind11.__version__)"
echo.
echo Next step: Run compile.bat to build the module
echo.
pause
