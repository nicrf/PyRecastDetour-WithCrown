# PyRecastDetour - Quick Start Guide

Quick start guide for PyRecastDetour with Crowd and Agent support.

## 📦 Project Contents

```
PyRecastDetour-Sources-main/
├── dist/                      # 📁 Distribution package
│   ├── __init__.py           # Python module
│   ├── example.py            # Usage examples
│   ├── README.md             # Installation instructions
│   └── Py*.pyd (after build) # Compiled module
│
├── PYTHON_API.md             # 📖 Complete API documentation
├── DISTRIBUTION.md           # 📦 Distribution guide
├── BUILD_INSTRUCTIONS.md     # 🔨 Build instructions
├── CLAUDE.md                 # 🤖 Technical documentation
├── CMakeLists.txt            # ⚙️ CMake configuration
│
├── build.bat                 # 🔨 Windows script (MinGW)
├── build.sh                  # 🔨 Linux/Mac script
├── build_msvc.bat            # 🔨 Windows script (MSVC) ⭐
│
└── src/ (C++ files)          # Source code
```

## 🚀 Quick Start

### Step 1: Compile the Module

Choose your method according to your system:

#### Windows with Visual Studio (Recommended)
```batch
build_msvc.bat
```

#### Windows with MinGW
```batch
build.bat
```

#### Linux/Mac
```bash
chmod +x build.sh
./build.sh
```

### Step 2: Verify Compilation

After compilation, check that the `dist/` folder contains:
- ✅ `__init__.py`
- ✅ `example.py`
- ✅ `Py310RecastDetour.*.pyd` (or `.so` on Linux/Mac)
- ✅ `README.md`

### Step 3: Test

```bash
cd dist
python example.py
```

Or quick test:
```bash
python -c "from PyRecastDetour import Navmesh; print('Import OK!')"
```

## 💡 First Program

```python
from PyRecastDetour import Navmesh, create_default_agent_params

# 1. Create and build navmesh
navmesh = Navmesh()
navmesh.init_by_obj("level.obj")  # Your .obj file
navmesh.build_navmesh()

# 2. Pathfinding
path = navmesh.pathfind_straight([0, 0, 0], [10, 0, 10])
print(f"Path: {len(path)//3} points")

# 3. Crowd simulation
navmesh.init_crowd(maxAgents=100, maxAgentRadius=1.0)

# 4. Add an agent
params = create_default_agent_params()
params["maxSpeed"] = 5.0
agent_id = navmesh.add_agent([5, 0, 5], params)

# 5. Set a target
navmesh.set_agent_target(agent_id, [50, 0, 50])

# 6. Game loop (60 FPS)
while True:
    navmesh.update_crowd(0.016)
    pos = navmesh.get_agent_position(agent_id)
    print(f"Agent position: {pos}")
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **PYTHON_API.md** | 📖 Complete documentation of all functions |
| **example.py** | 💻 7 practical commented examples |
| **CLAUDE.md** | 🤖 Architecture and technical details |
| **BUILD_INSTRUCTIONS.md** | 🔨 Build problems and solutions |
| **DISTRIBUTION.md** | 📦 How to distribute your compiled module |

## 🎯 Main Features

### ✅ Navigation Mesh
- Build from OBJ file or raw data
- Advanced configuration (cellSize, agentHeight, etc.)
- Save/Load binary (.bin)
- Export triangulation/polygonization

### ✅ Pathfinding
- `pathfind_straight()` - Direct path
- `pathfind_straight_batch()` - Multiple paths
- `raycast()` - Raycast
- `distance_to_wall()` - Distance to obstacles
- `hit_mesh()` - Intersection with geometry

### ✅ Crowd Simulation
- Manage hundreds of agents
- Obstacle and agent avoidance
- Customizable parameters per agent
- Real-time updates
- Dynamic parameter modification

### ✅ Agent Management
- `init_crowd()` - Initialize system
- `add_agent()` - Add an agent
- `remove_agent()` - Remove an agent
- `set_agent_target()` - Set a target
- `set_agent_velocity()` - Manual control
- `get_agent_position()` - Current position
- `get_agent_velocity()` - Current velocity
- `get_agent_state()` - Complete state
- `update_agent_parameters()` - Modify on-the-fly

## 🔧 Agent Configuration

Available parameters for each agent:

```python
params = {
    # Physical dimensions
    "radius": 0.6,              # Collision radius
    "height": 2.0,              # Agent height

    # Movement
    "maxSpeed": 3.5,            # Max speed
    "maxAcceleration": 8.0,     # Max acceleration

    # Navigation
    "collisionQueryRange": 7.2, # Collision detection
    "pathOptimizationRange": 18.0,  # Path optimization

    # Behavior
    "separationWeight": 2.0,    # Agent separation
    "updateFlags": 15,          # Behavior flags
    "obstacleAvoidanceType": 3, # Avoidance type [0-7]
    "queryFilterType": 0        # Filter type
}
```

### Behavior Flags

```python
from PyRecastDetour import (
    CROWD_ANTICIPATE_TURNS,    # 1  - Anticipate turns
    CROWD_OBSTACLE_AVOIDANCE,  # 2  - Avoid obstacles
    CROWD_SEPARATION,          # 4  - Separate agents
    CROWD_OPTIMIZE_VIS,        # 8  - Optimize visibility
    CROWD_OPTIMIZE_TOPO        # 16 - Optimize topology
)

# Combine with |
flags = CROWD_ANTICIPATE_TURNS | CROWD_OBSTACLE_AVOIDANCE | CROWD_OPTIMIZE_VIS
params["updateFlags"] = flags
```

## 🎮 Usage Examples

### Video Game
```python
# Game loop
def game_loop():
    navmesh.update_crowd(delta_time)

    for agent_id in active_agents:
        pos = navmesh.get_agent_position(agent_id)
        # Update 3D character position
        character.set_position(pos)
```

### Simulation
```python
# Crowd simulation
for i in range(100):
    params = create_default_agent_params()
    params["maxSpeed"] = random.uniform(2.0, 5.0)

    start = [random.uniform(0, 10), 0, random.uniform(0, 10)]
    agent_id = navmesh.add_agent(start, params)

    target = [random.uniform(90, 100), 0, random.uniform(90, 100)]
    navmesh.set_agent_target(agent_id, target)
```

### Asynchronous Pathfinding
```python
import threading

def find_path_async(start, end, callback):
    def worker():
        path = navmesh.pathfind_straight(start, end)
        callback(path)

    thread = threading.Thread(target=worker)
    thread.start()
```

## ⚠️ Important Points

1. **Initialization order:**
   ```python
   init_by_obj() → build_navmesh() → init_crowd() → add_agent()
   ```

2. **Check for errors:**
   ```python
   log = navmesh.get_log()
   if "error" in log.lower():
       print(f"Error: {log}")
   ```

3. **Performance:**
   - Build navmesh once, save with `save_navmesh()`
   - Limit number of agents (< 200 for real-time)
   - Call `update_crowd()` every frame

4. **Coordinates:**
   - Format: `[x, y, z]` always
   - Paths: `[x1, y1, z1, x2, y2, z2, ...]`
   - Delta time in seconds (e.g., 0.016 for 60 FPS)

## 🐛 Common Problems

### Module not found
```bash
# Check that the .pyd is in dist/
ls dist/*.pyd

# Add to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/path/to/dist
```

### Linking errors during compilation
- Windows: Use `build_msvc.bat` with Visual Studio
- Incompatible libraries: Recompile Recast/Detour with the same compiler

### Empty path
- Check that navmesh is built: `build_navmesh()`
- Start/end points must be on the navmesh
- Use `hit_mesh()` to check positions

### Crowd not initialized
```python
# Always initialize before adding agents
if not navmesh.init_crowd(100, 1.0):
    print("Error:", navmesh.get_log())
```

## 📞 Support

- **API Documentation:** `PYTHON_API.md`
- **Examples:** `example.py` (in dist/)
- **Build problems:** `BUILD_INSTRUCTIONS.md`
- **GitHub:** https://github.com/Tugcga/PyRecastDetour
- **Recast Navigation:** https://github.com/recastnavigation/recastnavigation

## 🎓 Learning Resources

1. **Get started:**
   - Read this guide
   - Run `example.py`
   - Modify the examples

2. **Go deeper:**
   - Read `PYTHON_API.md`
   - Experiment with parameters
   - Create a small project

3. **Master:**
   - Read Recast Navigation documentation
   - Optimize performance
   - Contribute to the project

## 🏆 Complete Example Project

See `example.py` for 7 complete examples:
1. ✅ Basic pathfinding
2. ✅ Custom configuration
3. ✅ Crowd simulation
4. ✅ Dynamic agent management
5. ✅ Parameter modification
6. ✅ Save/Load
7. ✅ Spatial queries

---

**Happy coding! 🚀**

For any questions, check `PYTHON_API.md` first, then GitHub issues.
