#!/bin/bash
# Build script for PyRecastDetour on Linux/Mac

echo "================================================"
echo "Building PyRecastDetour"
echo "================================================"

# Get Python paths
PYBIND11_INCLUDE=$(python3 -c "import pybind11; print(pybind11.get_include())")
PYTHON_INCLUDE=$(python3 -c "import sysconfig; print(sysconfig.get_path('include'))")
PYTHON_LIBDIR=$(python3 -c "import sysconfig; print(sysconfig.get_config_var('LIBDIR'))")
EXT_SUFFIX=$(python3 -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))")
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')")

echo "Python Include: $PYTHON_INCLUDE"
echo "PyBind11 Include: $PYBIND11_INCLUDE"
echo "Python Lib Dir: $PYTHON_LIBDIR"
echo "Extension Suffix: $EXT_SUFFIX"

# Determine module name based on Python version
if [ "$PYTHON_VERSION" == "36" ]; then
    MODULE_NAME="Py36RecastDetour"
    PYTHON_FLAG="-D_Python36"
elif [ "$PYTHON_VERSION" == "37" ]; then
    MODULE_NAME="Py37RecastDetour"
    PYTHON_FLAG="-D_Python37"
elif [ "$PYTHON_VERSION" == "38" ]; then
    MODULE_NAME="Py38RecastDetour"
    PYTHON_FLAG="-D_Python38"
elif [ "$PYTHON_VERSION" == "39" ]; then
    MODULE_NAME="Py39RecastDetour"
    PYTHON_FLAG="-D_Python39"
else
    MODULE_NAME="Py310RecastDetour"
    PYTHON_FLAG="-D_Python310"
fi

echo "Module name: $MODULE_NAME"

# Create build directory
mkdir -p build
cd build

echo ""
echo "================================================"
echo "Compiling source files..."
echo "================================================"

# Compile all source files
g++ -c -O3 -Wall -shared -std=c++11 -fPIC \
    $PYTHON_FLAG \
    -I"$PYTHON_INCLUDE" \
    -I"$PYBIND11_INCLUDE" \
    -I".." \
    -I"../include/recastnavigation" \
    ../PyRecastDetour.cpp \
    ../Navmesh.cpp \
    ../ChunkyTriMesh.cpp \
    ../ConvexVolumeTool.cpp \
    ../CrowdTool.cpp \
    ../InputGeom.cpp \
    ../MeshLoaderObj.cpp \
    ../NavMeshPruneTool.cpp \
    ../NavMeshTesterTool.cpp \
    ../OffMeshConnectionTool.cpp \
    ../PerfTimer.cpp \
    ../Sample.cpp \
    ../SampleInterfaces.cpp \
    ../Sample_Debug.cpp \
    ../Sample_SoloMesh.cpp \
    ../Sample_TempObstacles.cpp \
    ../Sample_TileMesh.cpp \
    ../ValueHistory.cpp

if [ $? -ne 0 ]; then
    echo "ERROR: Compilation failed!"
    cd ..
    exit 1
fi

echo ""
echo "================================================"
echo "Linking..."
echo "================================================"

# Link to create the Python module
g++ -shared -o ${MODULE_NAME}${EXT_SUFFIX} \
    PyRecastDetour.o \
    Navmesh.o \
    ChunkyTriMesh.o \
    ConvexVolumeTool.o \
    CrowdTool.o \
    InputGeom.o \
    MeshLoaderObj.o \
    NavMeshPruneTool.o \
    NavMeshTesterTool.o \
    OffMeshConnectionTool.o \
    PerfTimer.o \
    Sample.o \
    SampleInterfaces.o \
    Sample_Debug.o \
    Sample_SoloMesh.o \
    Sample_TempObstacles.o \
    Sample_TileMesh.o \
    ValueHistory.o \
    -L"../lib" \
    -L"$PYTHON_LIBDIR" \
    -lRecast \
    -lDetour \
    -lDetourCrowd \
    -lDetourTileCache \
    -lDebugUtils

if [ $? -ne 0 ]; then
    echo "ERROR: Linking failed!"
    cd ..
    exit 1
fi

# Copy output to parent directory
cp ${MODULE_NAME}${EXT_SUFFIX} ..

cd ..

# Create dist directory and copy files
echo ""
echo "================================================"
echo "Creating distribution package..."
echo "================================================"

mkdir -p dist
cp ${MODULE_NAME}${EXT_SUFFIX} dist/
cp __init__.py dist/

echo ""
echo "================================================"
echo "Build successful!"
echo "Output: ${MODULE_NAME}${EXT_SUFFIX}"
echo "Distribution package created in: dist/"
echo "================================================"
echo ""
echo "You can now import the module in Python:"
echo "  from PyRecastDetour import Navmesh"
echo ""
echo "Or install the dist package:"
echo "  cp -r dist/ /path/to/your/project/PyRecastDetour"
echo "================================================"
