# Changelog - PyRecastDetour With Crowd

Modifications and additions to the original PyRecastDetour project.

**Ported and enhanced by:** nicrf
**With assistance from:** Claude AI (Anthropic)

## Version 1.0 - With Crowd Support (2024-11-09)

### 🔄 Port to Latest Recast Navigation

Updated the original code to work with the latest version of Recast Navigation:
- Updated Recast/Detour APIs
- Fixed version incompatibilities
- Adapted to new data structures

## Added Features

### 🎉 New Major Features

#### Full Crowd Simulation Support
Added crowd management with all Detour Crowd features.

**New Navmesh methods:**
- ✅ `init_crowd(maxAgents, maxAgentRadius)` - Initialize crowd system
- ✅ `add_agent(pos, params)` - Add agent with configurable parameters
- ✅ `remove_agent(idx)` - Remove agent
- ✅ `update_crowd(dt)` - Update simulation
- ✅ `set_agent_target(idx, pos)` - Set navigation target
- ✅ `set_agent_velocity(idx, vel)` - Direct velocity control
- ✅ `reset_agent_target(idx)` - Cancel target
- ✅ `get_agent_position(idx)` - Current position
- ✅ `get_agent_velocity(idx)` - Current velocity
- ✅ `get_agent_state(idx)` - Complete state (20+ properties)
- ✅ `get_agent_count()` - Number of active agents
- ✅ `update_agent_parameters(idx, params)` - Modify parameters on-the-fly

### 📝 Modified Files

#### C++ Source Code

**Navmesh.h**
- Added `#include "DetourCrowd.h"`
- Added 13 new public methods for crowd management
- Added private member `dtCrowd* crowd`
- Added flag `bool is_crowd_init`

**Navmesh.cpp** (+400 lines)
- Crowd initialization and cleanup in constructor/destructor
- Complete implementation of 13 crowd methods
- Error handling with detailed log messages
- Support for configurable agent parameters
- Automatic position → polygon conversion for targets

**PyRecastDetour.cpp**
- Added PyBind11 bindings for all new methods
- Methods are now accessible from Python

**Sample.cpp**
- Fixed includes: `<math.h>` → `<cmath>`, etc.
- Added `<cstring>` for C++11 compatibility

**SampleInterfaces.cpp**
- Fixed includes: `<stdio.h>` → `<cstdio>`, etc.
- Added `<cstring>` for C++11 compatibility

### 📦 New Files

#### Build Scripts

**build.bat** (Windows MinGW)
- Automatic compilation of all source files
- Automatic Python and PyBind11 detection
- Automatic dist/ folder creation
- File copying to dist/

**build.sh** (Linux/Mac)
- Unix version of build script
- Multi-version Python support (3.6-3.13)
- Automatic path detection

**build_msvc.bat** (Windows MSVC) ⭐ **RECOMMENDED**
- Compilation with Microsoft Visual C++
- Compatible with provided .lib libraries
- Optimized Release build

**CMakeLists.txt**
- Complete CMake configuration
- Multi-platform support
- Automatic Python version detection

#### Documentation

**PYTHON_API.md** (18 KB)
- Complete documentation of all functions
- Detailed parameter descriptions
- Code examples for each function
- Reference tables
- Constants and flags guide
- 4 complete examples

**QUICK_START.md** (8.5 KB)
- Quick start guide
- First program
- Agent configuration
- Usage examples (game, simulation)
- Important points
- Troubleshooting

**BUILD_INSTRUCTIONS.md** (2.8 KB)
- Solutions to compilation problems
- Instructions for MSVC, MinGW, CMake
- Multi-platform support
- Distribution checklist

**DISTRIBUTION.md** (5.7 KB)
- Package creation guide
- Distribution instructions
- Multi-platform support
- Version naming
- Complete checklist

**CLAUDE.md** (updated, 9.4 KB)
- Crowd Simulation API documentation
- Detailed agent parameters
- States and flags
- Code examples
- Important notes

**CHANGELOG.md** (this file)
- Change history
- New features list
- Modified/added files

#### Python Module

**__init__.py** (3.5 KB)
- Automatic import based on Python version
- Constants (CROWD_*, CROWDAGENT_*, PARTITION_*)
- `create_default_agent_params()` function
- Complete docstring documentation

**example.py** (13 KB)
- 7 commented examples:
  1. Basic pathfinding
  2. Custom configuration
  3. Crowd simulation
  4. Dynamic agent management
  5. Parameter modification
  6. Save/Load
  7. Spatial queries
- Directly executable code
- Educational examples

#### dist/ Folder

**dist/README.md**
- Installation instructions
- How to get the .pyd
- Quick usage
- Common problems
- Support

**dist/** (structure)
```
dist/
├── __init__.py          # Python module
├── example.py           # Examples
├── README.md            # Instructions
└── Py*.pyd (after build) # Compiled module
```

### 🔧 Technical Improvements

#### C++ Compatibility
- Migration to standard C++ headers (`<cmath>`, `<cstring>`)
- Complete C++11 support
- Fixes for GCC and MSVC

#### Error Handling
- All logs go through `rcContext::log()`
- Explicit error messages in English
- State verification (is_init, is_build, is_crowd_init)

#### Performance
- Optimized default values for agents
- Support for 100+ agents in real-time
- Efficient obstacle avoidance

### 📊 Statistics

**Lines of Code Added:**
- C++ source: ~450 lines
- Python: ~600 lines
- Documentation: ~2500 lines
- **Total: ~3550 lines**

**Files Created:** 11
**Files Modified:** 5
**New Features:** 13

### 🎯 Main Features

#### Before (Original)
- ✅ Navmesh building (OBJ, raw)
- ✅ Basic pathfinding
- ✅ Raycast
- ✅ Distance to wall
- ✅ Save/Load navmesh
- ❌ Crowd simulation
- ❌ Agents
- ❌ Obstacle avoidance
- ❌ Python documentation

#### After (Enhanced)
- ✅ Navmesh building (OBJ, raw)
- ✅ Basic pathfinding
- ✅ Raycast
- ✅ Distance to wall
- ✅ Save/Load navmesh
- ✅ **Crowd simulation**
- ✅ **Agents with configurable parameters**
- ✅ **Obstacle and agent avoidance**
- ✅ **Complete Python documentation**
- ✅ **Automatic build scripts**
- ✅ **Commented examples**
- ✅ **Improved multi-platform support**

### 🐛 Bug Fixes

- Fix: Missing includes for `memset` (added `<cstring>`)
- Fix: Private method `getTile()` call → using const version
- Fix: C++11 compatibility with GCC

### 🔄 Backwards Compatibility

✅ **100% backwards compatible**

All existing code using PyRecastDetour continues to work:
```python
# Original code - still works
navmesh = Navmesh()
navmesh.init_by_obj("level.obj")
navmesh.build_navmesh()
path = navmesh.pathfind_straight([0,0,0], [10,0,10])
```

New features are purely additive.

### 📦 Installation and Usage

#### Before
```python
# Difficult manual installation
# No build scripts provided
# Limited documentation
```

#### After
```bash
# Simple - single script
build_msvc.bat  # or build.sh on Linux

# Ready package in dist/
cd dist
python example.py
```

### 🎓 Documentation

#### Before
- Basic README.md
- No Python API documentation
- No examples

#### After
- **PYTHON_API.md** - Complete reference (55 functions documented)
- **QUICK_START.md** - Getting started guide
- **example.py** - 7 complete examples
- **BUILD_INSTRUCTIONS.md** - Build guide
- **DISTRIBUTION.md** - Distribution guide
- **CLAUDE.md** updated

### 🚀 Using New Features

```python
from PyRecastDetour import Navmesh, create_default_agent_params

# Setup navmesh (as before)
navmesh = Navmesh()
navmesh.init_by_obj("level.obj")
navmesh.build_navmesh()

# NEW: Crowd simulation
navmesh.init_crowd(100, 1.0)

# NEW: Add agents
params = create_default_agent_params()
params["maxSpeed"] = 5.0
agent = navmesh.add_agent([0, 0, 0], params)

# NEW: Control agents
navmesh.set_agent_target(agent, [100, 0, 100])
navmesh.update_crowd(0.016)

# NEW: Query agents
pos = navmesh.get_agent_position(agent)
state = navmesh.get_agent_state(agent)
```

### 📈 Possible Next Steps

Suggestions for future improvements:
- [ ] Tiled Navmesh support (expose to Python)
- [ ] Dynamic Obstacles support (already in source)
- [ ] Bindings for Off-Mesh Connections
- [ ] Convex Volumes support
- [ ] Multithreading for update_crowd
- [ ] Profiling and optimizations
- [ ] Python unit tests
- [ ] CI/CD with GitHub Actions

### 🙏 Credits

**Original Project:**
- [Recast Navigation](https://github.com/recastnavigation/recastnavigation) - Mikko Mononen
- [PyRecastDetour](https://github.com/Tugcga/PyRecastDetour) - Tugcga

**This Fork:**
- Port to latest Recast Navigation: nicrf (2024-11-09)
- Crowd/Agent support: nicrf with assistance from Claude AI (2024-11-09)
- Complete documentation: Created with Claude AI (2024-11-09)
- Build scripts: Created with Claude AI (2024-11-09)
- Repository: https://github.com/nicrf/PyRecastDetour-WithCrown

### 📄 License

Preserves the original PyRecastDetour project license.
New features under the same license.

---

**Enhanced Version 1.0** - November 2024

Complete project with Crowd/Agent support, exhaustive documentation, and automatic build scripts.
