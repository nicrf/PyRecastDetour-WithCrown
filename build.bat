@echo off
REM Build script for PyRecastDetour on Windows with g++

echo ================================================
echo Building PyRecastDetour for Python 3.13
echo ================================================

REM Get Python paths
for /f "delims=" %%i in ('python -c "import pybind11; print(pybind11.get_include())"') do set PYBIND11_INCLUDE=%%i
for /f "delims=" %%i in ('python -c "import sysconfig; print(sysconfig.get_path('include'))"') do set PYTHON_INCLUDE=%%i
for /f "delims=" %%i in ('python -c "import sysconfig; print(sysconfig.get_config_var('LIBDIR'))"') do set PYTHON_LIBS=%%i
for /f "delims=" %%i in ('python -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))"') do set EXT_SUFFIX=%%i

echo Python Include: %PYTHON_INCLUDE%
echo PyBind11 Include: %PYBIND11_INCLUDE%
echo Python Libs: %PYTHON_LIBS%
echo Extension Suffix: %EXT_SUFFIX%

REM Set module name based on Python version
set MODULE_NAME=Py310RecastDetour

REM Create build directory
if not exist "build" mkdir build
cd build

echo.
echo ================================================
echo Compiling source files...
echo ================================================

REM Compile all source files
g++ -c -O3 -Wall -shared -std=c++11 -fPIC ^
    -D_Python310 ^
    -I"%PYTHON_INCLUDE%" ^
    -I"%PYBIND11_INCLUDE%" ^
    -I".." ^
    -I"..\include\recastnavigation" ^
    ..\PyRecastDetour.cpp ^
    ..\Navmesh.cpp ^
    ..\ChunkyTriMesh.cpp ^
    ..\ConvexVolumeTool.cpp ^
    ..\CrowdTool.cpp ^
    ..\InputGeom.cpp ^
    ..\MeshLoaderObj.cpp ^
    ..\NavMeshPruneTool.cpp ^
    ..\NavMeshTesterTool.cpp ^
    ..\OffMeshConnectionTool.cpp ^
    ..\PerfTimer.cpp ^
    ..\Sample.cpp ^
    ..\SampleInterfaces.cpp ^
    ..\Sample_Debug.cpp ^
    ..\Sample_SoloMesh.cpp ^
    ..\Sample_TempObstacles.cpp ^
    ..\Sample_TileMesh.cpp ^
    ..\ValueHistory.cpp

if %errorlevel% neq 0 (
    echo ERROR: Compilation failed!
    cd ..
    exit /b 1
)

echo.
echo ================================================
echo Linking...
echo ================================================

REM Link to create the Python module
g++ -shared -o %MODULE_NAME%%EXT_SUFFIX% ^
    PyRecastDetour.o ^
    Navmesh.o ^
    ChunkyTriMesh.o ^
    ConvexVolumeTool.o ^
    CrowdTool.o ^
    InputGeom.o ^
    MeshLoaderObj.o ^
    NavMeshPruneTool.o ^
    NavMeshTesterTool.o ^
    OffMeshConnectionTool.o ^
    PerfTimer.o ^
    Sample.o ^
    SampleInterfaces.o ^
    Sample_Debug.o ^
    Sample_SoloMesh.o ^
    Sample_TempObstacles.o ^
    Sample_TileMesh.o ^
    ValueHistory.o ^
    -L"..\lib" ^
    -L"%PYTHON_LIBS%" ^
    -lRecast ^
    -lDetour ^
    -lDetourCrowd ^
    -lDetourTileCache ^
    -lDebugUtils ^
    -lpython313

if %errorlevel% neq 0 (
    echo ERROR: Linking failed!
    cd ..
    exit /b 1
)

REM Copy output to parent directory
copy %MODULE_NAME%%EXT_SUFFIX% ..

cd ..

REM Create dist directory and copy files
echo.
echo ================================================
echo Creating distribution package...
echo ================================================

if not exist "dist" mkdir dist
copy %MODULE_NAME%%EXT_SUFFIX% dist\
copy __init__.py dist\

echo.
echo ================================================
echo Build successful!
echo Output: %MODULE_NAME%%EXT_SUFFIX%
echo Distribution package created in: dist\
echo ================================================
echo.
echo You can now import the module in Python:
echo   from PyRecastDetour import Navmesh
echo.
echo Or install the dist package:
echo   xcopy /E /I dist "C:\path\to\your\project\PyRecastDetour"
echo ================================================
