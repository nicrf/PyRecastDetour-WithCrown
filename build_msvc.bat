@echo off
REM Build script for PyRecastDetour on Windows with MSVC

REM Initialize MSVC environment
REM Try to find and run vcvarsall.bat for Visual Studio
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
) else if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
) else if exist "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    call "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
) else (
    echo WARNING: Visual Studio not found at default locations
    echo Please run this script from "Developer Command Prompt for VS" or set MSVC environment manually
)

echo ================================================
echo Building PyRecastDetour for Python 3.7 with MSVC
echo ================================================

REM Set Python path explicitly - use venv
set PYTHON_PATH=venv37\Scripts\python.exe

REM Set PyBind11 include path manually (using local pybind11)
set PYBIND11_INCLUDE=%CD%\pybind11_src\include

REM Get Python paths
for /f "delims=" %%i in ('%PYTHON_PATH% -c "import sysconfig; print(sysconfig.get_path('include'))"') do set PYTHON_INCLUDE=%%i
for /f "delims=" %%i in ('%PYTHON_PATH% -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))"') do set EXT_SUFFIX=%%i

REM Get Python libs path dynamically (works for both venv and system Python)
for /f "delims=" %%i in ('%PYTHON_PATH% -c "import sys, os; print(os.path.join(sys.base_prefix, 'libs'))"') do set PYTHON_LIBS=%%i

echo Python Include: %PYTHON_INCLUDE%
echo PyBind11 Include: %PYBIND11_INCLUDE%
echo Python Libs: %PYTHON_LIBS%
echo Extension Suffix: %EXT_SUFFIX%

REM Set module name based on Python version
set MODULE_NAME=Py37RecastDetour

REM Create build directory
if not exist "build_msvc" mkdir build_msvc
cd build_msvc

echo.
echo ================================================
echo Compiling source files with MSVC...
echo ================================================

REM Compile all source files (project + Recast/Detour sources)
cl /c /O2 /EHsc /MD /std:c++14 ^
    /D_Python37 /DNDEBUG ^
    /I"%PYTHON_INCLUDE%" ^
    /I"%PYBIND11_INCLUDE%" ^
    /I".." ^
    /I"..\include\recastnavigation" ^
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
    ..\ValueHistory.cpp ^
    ..\Sample.cpp ^
    ..\SampleInterfaces.cpp ^
    ..\Sample_SoloMesh.cpp ^
    ..\DebugUtilsStub.cpp ^
    ..\include\recastnavigation\Recast.cpp ^
    ..\include\recastnavigation\RecastAlloc.cpp ^
    ..\include\recastnavigation\RecastArea.cpp ^
    ..\include\recastnavigation\RecastAssert.cpp ^
    ..\include\recastnavigation\RecastContour.cpp ^
    ..\include\recastnavigation\RecastFilter.cpp ^
    ..\include\recastnavigation\RecastLayers.cpp ^
    ..\include\recastnavigation\RecastMesh.cpp ^
    ..\include\recastnavigation\RecastMeshDetail.cpp ^
    ..\include\recastnavigation\RecastRasterization.cpp ^
    ..\include\recastnavigation\RecastRegion.cpp ^
    ..\include\recastnavigation\DetourAlloc.cpp ^
    ..\include\recastnavigation\DetourAssert.cpp ^
    ..\include\recastnavigation\DetourCommon.cpp ^
    ..\include\recastnavigation\DetourNavMesh.cpp ^
    ..\include\recastnavigation\DetourNavMeshBuilder.cpp ^
    ..\include\recastnavigation\DetourNavMeshQuery.cpp ^
    ..\include\recastnavigation\DetourNode.cpp ^
    ..\include\recastnavigation\DetourCrowd.cpp ^
    ..\include\recastnavigation\DetourLocalBoundary.cpp ^
    ..\include\recastnavigation\DetourObstacleAvoidance.cpp ^
    ..\include\recastnavigation\DetourPathCorridor.cpp ^
    ..\include\recastnavigation\DetourPathQueue.cpp ^
    ..\include\recastnavigation\DetourProximityGrid.cpp ^
    ..\include\recastnavigation\DebugDraw.cpp ^
    ..\include\recastnavigation\RecastDebugDraw.cpp ^
    ..\include\recastnavigation\DetourDebugDraw.cpp

if %errorlevel% neq 0 (
    echo ERROR: Compilation failed!
    cd ..
    exit /b 1
)

echo.
echo ================================================
echo Linking with MSVC...
echo ================================================

REM Link to create the Python module
link /DLL /OUT:%MODULE_NAME%%EXT_SUFFIX% ^
    PyRecastDetour.obj ^
    Navmesh.obj ^
    ChunkyTriMesh.obj ^
    ConvexVolumeTool.obj ^
    CrowdTool.obj ^
    InputGeom.obj ^
    MeshLoaderObj.obj ^
    NavMeshPruneTool.obj ^
    NavMeshTesterTool.obj ^
    OffMeshConnectionTool.obj ^
    PerfTimer.obj ^
    ValueHistory.obj ^
    Sample.obj ^
    SampleInterfaces.obj ^
    Sample_SoloMesh.obj ^
    DebugUtilsStub.obj ^
    Recast.obj ^
    RecastAlloc.obj ^
    RecastArea.obj ^
    RecastAssert.obj ^
    RecastContour.obj ^
    RecastFilter.obj ^
    RecastLayers.obj ^
    RecastMesh.obj ^
    RecastMeshDetail.obj ^
    RecastRasterization.obj ^
    RecastRegion.obj ^
    DetourAlloc.obj ^
    DetourAssert.obj ^
    DetourCommon.obj ^
    DetourNavMesh.obj ^
    DetourNavMeshBuilder.obj ^
    DetourNavMeshQuery.obj ^
    DetourNode.obj ^
    DetourCrowd.obj ^
    DetourLocalBoundary.obj ^
    DetourObstacleAvoidance.obj ^
    DetourPathCorridor.obj ^
    DetourPathQueue.obj ^
    DetourProximityGrid.obj ^
    DebugDraw.obj ^
    RecastDebugDraw.obj ^
    DetourDebugDraw.obj ^
    /LIBPATH:"%PYTHON_LIBS%" ^
    python37.lib

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
