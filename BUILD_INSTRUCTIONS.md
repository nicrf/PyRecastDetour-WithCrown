# PyRecastDetour - Build Instructions

## Current Issue

The Recast/Detour libraries in `lib/` are compiled with MSVC and incompatible with MinGW/GCC.

## Solutions

### Solution 1: Use MSVC (Recommended for Windows)

1. **Install Visual Studio** or Build Tools for Visual Studio:
   - Download: https://visualstudio.microsoft.com/downloads/
   - Install "Desktop development with C++"

2. **Open "Developer Command Prompt for VS"**

3. **Compile with the provided batch script:**
   ```batch
   build_msvc.bat
   ```

### Solution 2: Recompile Recast/Detour with MinGW

1. **Clone Recast Navigation:**
   ```bash
   git clone https://github.com/recastnavigation/recastnavigation.git
   cd recastnavigation
   ```

2. **Create a build with MinGW:**
   ```bash
   mkdir build && cd build
   cmake -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release ..
   mingw32-make
   ```

3. **Copy the generated libraries** (`.a` files) to the PyRecastDetour `lib/` folder

4. **Modify build.bat** to use `.a` instead of `.lib`

5. **Recompile PyRecastDetour:**
   ```batch
   build.bat
   ```

### Solution 3: Use CMake with available compiler

If CMake is installed:

```bash
mkdir build && cd build
cmake -G "MinGW Makefiles" ..
mingw32-make
```

Or with MSVC:
```batch
mkdir build && cd build
cmake ..
cmake --build . --config Release
```

## Created Files

- ✅ `CMakeLists.txt` - CMake configuration
- ✅ `build.bat` - Windows build script (requires compatible libraries)
- ✅ `build.sh` - Linux/Mac build script
- ✅ `__init__.py` - Python helper module with constants
- ✅ C++ code with full crowd/agent support

## Modifications Made

### Modified files:
1. **Navmesh.h/cpp** - Added 13 methods for crowd management
2. **PyRecastDetour.cpp** - PyBind11 bindings for new methods
3. **CLAUDE.md** - Complete crowd API documentation

### Added features:
- `init_crowd()` - Initialize crowd system
- `add_agent()` - Add agents with configurable parameters
- `update_crowd()` - Update simulation
- `set_agent_target()` - Set navigation target
- `get_agent_position()`, `get_agent_velocity()`, `get_agent_state()` - Query agents
- And more (see CLAUDE.md)

## Next Steps

1. Choose a solution above
2. Compile Recast/Detour libraries if necessary
3. Compile PyRecastDetour
4. Test with:
   ```python
   from PyRecastDetour import Navmesh
   navmesh = Navmesh()
   # etc...
   ```

## Support

For more information:
- **Recast Navigation**: https://github.com/recastnavigation/recastnavigation
- **PyBind11**: https://pybind11.readthedocs.io/
