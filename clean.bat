@echo off
REM Clean build artifacts and temporary files

echo Cleaning build artifacts...

REM Remove build directories
if exist "build" rmdir /s /q "build"
if exist "build_msvc" rmdir /s /q "build_msvc"
if exist "build_mingw" rmdir /s /q "build_mingw"

REM Remove compiled binaries from dist (keep source files)
if exist "dist\*.pyd" del /q "dist\*.pyd"
if exist "dist\*.so" del /q "dist\*.so"

REM Remove Python cache
if exist "__pycache__" rmdir /s /q "__pycache__"
for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
del /s /q *.pyc 2>nul

REM Remove temporary test files
if exist "test_*.py" del /q "test_*.py"
if exist "test_*.txt" del /q "test_*.txt"
if exist "py37_paths.txt" del /q "py37_paths.txt"

REM Remove downloaded dependencies (optional - uncomment to clean)
REM if exist "pybind11_src" rmdir /s /q "pybind11_src"
REM if exist "pybind11.zip" del /q "pybind11.zip"

REM Remove virtual environments (optional - uncomment to clean)
REM if exist "venv37" rmdir /s /q "venv37"
REM for /d %%d in (venv*) do @if exist "%%d" rmdir /s /q "%%d"

echo.
echo Cleanup complete!
echo.
echo Kept:
echo   - Source files
echo   - Documentation
echo   - dist/__init__.py and examples
echo   - pybind11_src/ (uncomment in script to remove)
echo   - venv37/ (uncomment in script to remove)
echo.
