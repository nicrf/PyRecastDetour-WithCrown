cmake_minimum_required(VERSION 3.12)
project(PyRecastDetour)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# Find pybind11
find_package(pybind11 CONFIG REQUIRED)

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include/recastnavigation
)

# Link directories
link_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/lib
)

# Source files
set(SOURCE_FILES
    PyRecastDetour.cpp
    Navmesh.cpp
    ChunkyTriMesh.cpp
    ConvexVolumeTool.cpp
    CrowdTool.cpp
    InputGeom.cpp
    MeshLoaderObj.cpp
    NavMeshPruneTool.cpp
    NavMeshTesterTool.cpp
    OffMeshConnectionTool.cpp
    PerfTimer.cpp
    Sample.cpp
    SampleInterfaces.cpp
    Sample_Debug.cpp
    Sample_SoloMesh.cpp
    Sample_TempObstacles.cpp
    Sample_TileMesh.cpp
    ValueHistory.cpp
)

# Determine Python version for module name
if(Python_VERSION_MAJOR EQUAL 2)
    set(MODULE_NAME "Py2RecastDetour")
    add_definitions(-D_Python2)
elseif(Python_VERSION_MINOR EQUAL 6)
    set(MODULE_NAME "Py36RecastDetour")
    add_definitions(-D_Python36)
elseif(Python_VERSION_MINOR EQUAL 7)
    set(MODULE_NAME "Py37RecastDetour")
    add_definitions(-D_Python37)
elseif(Python_VERSION_MINOR EQUAL 8)
    set(MODULE_NAME "Py38RecastDetour")
    add_definitions(-D_Python38)
elseif(Python_VERSION_MINOR EQUAL 9)
    set(MODULE_NAME "Py39RecastDetour")
    add_definitions(-D_Python39)
else()
    set(MODULE_NAME "Py310RecastDetour")
    add_definitions(-D_Python310)
endif()

# Create Python module
pybind11_add_module(${MODULE_NAME} ${SOURCE_FILES})

# Link libraries
target_link_libraries(${MODULE_NAME} PRIVATE
    Recast
    Detour
    DetourCrowd
    DetourTileCache
    DebugUtils
)

# Set output directory
set_target_properties(${MODULE_NAME} PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

message(STATUS "Building ${MODULE_NAME} for Python ${Python_VERSION}")
