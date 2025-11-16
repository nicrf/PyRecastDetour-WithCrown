# PyRecastDetour for Cave Engine

Python bindings for [Recast Navigation](https://github.com/recastnavigation/recastnavigation) with **full Crowd and Agent support**, optimized for **Cave Engine** (Python 3.7.4, Windows).

**Original project:** [PyRecastDetour](https://github.com/Tugcga/PyRecastDetour) by Tugcga
**Enhanced by:** nicrf - Added crowd/agent management, formations, convex volumes, off-mesh connections, and advanced features.

Use this library to add AI pathfinding and navigation to your Cave Engine games.

---

## Quick Start for Cave Engine

### Installation

Copy the `dist/` folder to your Cave Engine project and import:

```python
import sys
sys.path.append("path/to/PyRecastDetour/dist")
from PyRecastDetour import Navmesh, create_default_agent_params
```

### Basic Cave Engine Integration

```python
import cave
from PyRecastDetour import Navmesh, create_default_agent_params

class AIController(cave.Component):
    def start(self, scene):
        # Build navmesh from level geometry
        self.navmesh = Navmesh()
        self.navmesh.init_by_obj("Content/Level1_navmesh.obj")
        self.navmesh.build_navmesh()

        # Initialize crowd system
        self.navmesh.init_crowd(maxAgents=50, maxAgentRadius=1.0)

        # Create AI agent
        params = create_default_agent_params()
        params["maxSpeed"] = 3.5
        params["radius"] = 0.6

        pos = self.entity.getTransform().position
        self.agent_id = self.navmesh.add_agent([pos.x, pos.y, pos.z], params)

    def update(self):
        dt = cave.getDeltaTime()

        # Update crowd simulation
        self.navmesh.update_crowd(dt)

        # Get agent position and update entity
        pos = self.navmesh.get_agent_position(self.agent_id)
        self.entity.getTransform().position.set(pos[0], pos[1], pos[2])

    def set_target(self, target_pos):
        """Set navigation target for this AI"""
        self.navmesh.set_agent_target(self.agent_id,
            [target_pos.x, target_pos.y, target_pos.z])
```

---

## Complete Function Reference

### 📦 Initialization & Building (8 functions)

#### Geometry Loading
- **`init_by_obj(file_path: str)`** - Load geometry from OBJ file
- **`init_by_raw(vertices: List[float], faces: List[int])`** - Load from vertex/face data
  - `vertices`: `[x1, y1, z1, x2, y2, z2, ...]`
  - `faces`: `[i1, i2, i3, i4, i5, i6, ...]` (triangle indices)

#### Building & Configuration
- **`build_navmesh()`** - Generate navigation mesh (call after init)
- **`get_log() -> str`** - Get build log messages
- **`get_settings() -> dict`** - Get navmesh build settings
- **`set_settings(settings: dict)`** - Configure build parameters
  - Keys: `cellSize`, `cellHeight`, `agentHeight`, `agentRadius`, `agentMaxClimb`, `agentMaxSlope`, etc.
- **`get_partition_type() -> int`** - Get partition algorithm (0=Watershed, 1=Monotone, 2=Layers)
- **`set_partition_type(type: int)`** - Set partition algorithm
- **`get_bounding_box() -> tuple`** - Returns `((min_x, min_y, min_z), (max_x, max_y, max_z))`

### 🎯 Pathfinding (5 functions)

- **`pathfind_straight(start, end, vertex_mode=0) -> list`** - Find path between two points
  - Returns: `[(x1,y1,z1), (x2,y2,z2), ...]`
  - `vertex_mode`: 0=corners only, 1=area changes, 2=all edge crossings

- **`pathfind_straight_batch(coords, vertex_mode=0) -> list`** - Batch pathfinding
  - `coords`: `[s1x, s1y, s1z, e1x, e1y, e1z, s2x, ...]` (must be divisible by 6)
  - Returns: `[path1, path2, ...]` where each path is `[(x,y,z), ...]`

- **`raycast(start, end) -> list`** - Cast ray through navmesh
  - Returns: `[(start_x, start_y, start_z), (hit_x, hit_y, hit_z)]`

- **`hit_mesh(start, end) -> tuple`** - Ray intersection with original geometry
  - Returns: `(x, y, z)` intersection point

- **`distance_to_wall(point) -> float`** - Distance to nearest navmesh edge

### 💾 Serialization (4 functions)

- **`save_navmesh(file_path: str)`** - Save built navmesh to .bin file
- **`load_navmesh(file_path: str)`** - Load navmesh from .bin file
- **`get_navmesh_trianglulation() -> tuple`** - Export as triangles
  - Returns: `(vertices, triangles)` where `triangles` are triangle indices
- **`get_navmesh_poligonization() -> tuple`** - Export as polygons
  - Returns: `(vertices, polygons, sizes)` with variable polygon sizes

### 👥 Crowd Simulation (17 functions)

#### Initialization
- **`init_crowd(maxAgents: int, maxAgentRadius: float) -> bool`** - Initialize crowd manager
  - Must be called after `build_navmesh()` and before adding agents

#### Agent Management
- **`add_agent(pos: tuple, params: dict) -> int`** - Add agent, returns agent_id (-1 on failure)
- **`remove_agent(idx: int)`** - Remove agent from crowd
- **`update_agent_parameters(idx: int, params: dict)`** - Update agent parameters at runtime

#### Agent Control
- **`set_agent_target(idx: int, pos: tuple) -> bool`** - Set navigation target
- **`set_agent_velocity(idx: int, vel: tuple)`** - Set velocity directly (manual control)
- **`reset_agent_target(idx: int)`** - Clear agent's target

#### Simulation Update
- **`update_crowd(dt: float)`** - Update crowd simulation (call every frame)
  - `dt`: Delta time in seconds (e.g., `cave.getDeltaTime()`)

#### Agent Queries
- **`get_agent_position(idx: int) -> tuple`** - Returns `(x, y, z)`
- **`get_agent_velocity(idx: int) -> tuple`** - Returns `(vx, vy, vz)`
- **`get_agent_count() -> int`** - Total number of agents
- **`get_agent_state(idx: int) -> dict`** - Complete agent state
  - Keys: `posX/Y/Z`, `velX/Y/Z`, `radius`, `height`, `maxSpeed`, `active`, `state`, `targetState`, etc.
- **`get_agent_neighbors(idx: int) -> list`** - List of neighboring agent indices
- **`get_agent_corners(idx: int) -> list`** - Path corner points `[(x,y,z), ...]`
- **`get_active_agents() -> list`** - All active agent indices
- **`is_agent_active(idx: int) -> bool`** - Check if agent is active
- **`get_agent_parameters(idx: int) -> dict`** - Get agent's current parameters
- **`get_max_agent_count() -> int`** - Maximum agent capacity
- **`get_query_half_extents() -> tuple`** - Query search extents `(x, y, z)`

### 📐 Convex Volumes - v1.1.0 (5 functions)

Mark 3D regions with special area types (water, roads, danger zones):

- **`add_convex_volume(verts, minh, maxh, area)`** - Add volume
  - `verts`: `[x1,y1,z1, x2,y2,z2, ...]` (3-12 vertices, must be convex)
  - `minh/maxh`: Min/max height
  - `area`: Area type (use `POLYAREA_*` constants)

- **`delete_convex_volume(index: int)`** - Remove volume
- **`get_convex_volume_count() -> int`** - Number of volumes
- **`get_convex_volume(index: int) -> dict`** - Get volume info
- **`get_all_convex_volumes() -> list`** - All volumes

**Example:**
```python
from PyRecastDetour import POLYAREA_WATER

# Mark water zone (rectangular pool)
navmesh.add_convex_volume([10,0,10, 20,0,10, 20,0,20, 10,0,20], 0.0, 2.0, POLYAREA_WATER)
navmesh.build_navmesh()  # Rebuild to apply
```

### 🌉 Off-Mesh Connections - v1.1.0 (5 functions)

Create special connections (jumps, ladders, teleports):

- **`add_offmesh_connection(start, end, radius, bidirectional, area, flags)`**
  - `start/end`: Position tuples `(x, y, z)`
  - `radius`: Connection radius
  - `bidirectional`: `True` for two-way
  - `area`: Area type (`POLYAREA_JUMP`, etc.)
  - `flags`: Capability flags (`POLYFLAGS_JUMP`, etc.)

- **`delete_offmesh_connection(index: int)`**
- **`get_offmesh_connection_count() -> int`**
- **`get_offmesh_connection(index: int) -> dict`**
- **`get_all_offmesh_connections() -> list`**

**Example:**
```python
from PyRecastDetour import POLYAREA_JUMP, POLYFLAGS_JUMP

# Add jump connection (one-way)
navmesh.add_offmesh_connection(
    (5, 2, 5), (10, 3, 10),  # Start -> End
    radius=0.5,
    bidirectional=False,
    area=POLYAREA_JUMP,
    flags=POLYFLAGS_JUMP
)
navmesh.build_navmesh()
```

### 🎨 Auto-Markup System - v1.1.0 (6 functions)

Automatically mark areas before building navmesh:

- **`mark_walkable_triangles(slope_angle: float)`** - Mark walkable based on slope
- **`mark_box_area(bmin, bmax, area_id)`** - Mark box region
  - `bmin/bmax`: `(x, y, z)` corners
- **`mark_cylinder_area(pos, radius, height, area_id)`** - Mark cylinder
- **`mark_convex_poly_area(verts, hmin, hmax, area_id)`** - Mark polygon
- **`erode_walkable_area(radius: int)`** - Shrink walkable area by radius (cells)
- **`median_filter_walkable_area()`** - Smooth walkable area

**Example:**
```python
# Mark road (fast travel)
navmesh.mark_box_area((0,0,0), (100,1,5), POLYAREA_ROAD)

# Mark water pond
navmesh.mark_cylinder_area((25,0,25), 10.0, 2.0, POLYAREA_WATER)

navmesh.build_navmesh()
```

### 🚀 Advanced Crowd Features - v1.1.0 (6 functions)

#### Obstacle Avoidance Profiles
- **`set_obstacle_avoidance_params(idx, params: dict)`** - Configure avoidance profile (0-7)
- **`get_obstacle_avoidance_params(idx) -> dict`** - Get avoidance profile

#### Query Filters (Unit Types)
- **`set_query_filter_area_cost(filter_idx, area_id, cost: float)`** - Set area cost
- **`get_query_filter_area_cost(filter_idx, area_id) -> float`** - Get area cost
- **`set_query_filter_include_flags(filter_idx, flags: int)`** - Required capabilities
- **`set_query_filter_exclude_flags(filter_idx, flags: int)`** - Excluded capabilities

**Example:**
```python
# Infantry can't swim
navmesh.set_query_filter_area_cost(0, POLYAREA_WATER, 100.0)  # Expensive
navmesh.set_query_filter_area_cost(0, POLYAREA_ROAD, 0.5)     # Fast
navmesh.set_query_filter_include_flags(0, POLYFLAGS_WALK | POLYFLAGS_JUMP)

# Agent uses filter 0
params["queryFilterType"] = 0
```

### 🎖️ Formations & Group Behaviors - v1.1.0 (9 functions)

Create and manage group formations:

- **`create_formation(type: int, spacing: float) -> int`** - Create formation
  - Types: 0=Line, 1=Column, 2=Wedge, 3=Box, 4=Circle
  - Returns formation_id

- **`delete_formation(formation_id: int)`**
- **`add_agent_to_formation(formation_id, agent_idx) -> bool`**
- **`remove_agent_from_formation(agent_idx) -> bool`**
- **`set_formation_target(formation_id, target_pos, target_dir)`**
  - `target_dir`: Direction vector `(x, y, z)` (normalized automatically)
- **`set_formation_leader(formation_id, agent_idx)`**
- **`get_formation_agents(formation_id) -> list`** - Agent indices in formation
- **`get_formation_info(formation_id) -> dict`** - Formation details
- **`update_formations(dt: float)`** - Update all formations (call every frame)
- **`get_formation_count() -> int`**

**Example:**
```python
# Create wedge formation
formation = navmesh.create_formation(2, spacing=2.0)  # FORMATION_WEDGE

# Add agents
for agent_id in my_agents:
    navmesh.add_agent_to_formation(formation, agent_id)

# Move formation
navmesh.set_formation_target(formation, (50, 0, 50), (0, 0, 1))  # Move north

# In game loop
navmesh.update_crowd(dt)
navmesh.update_formations(dt)
```

### 🛠️ Helper Functions (6 functions)

- **`create_default_agent_params() -> dict`** - Default agent parameters
- **`create_vehicle_params() -> dict`** - Vehicle agent parameters (larger, faster)
- **`create_obstacle_avoidance_params(profile: str) -> dict`**
  - Profiles: `"default"`, `"aggressive"`, `"passive"`, `"defensive"`
- **`setup_query_filter_infantry(navmesh, filter_idx)`** - Infantry filter (can't swim)
- **`setup_query_filter_amphibious(navmesh, filter_idx)`** - Can walk and swim
- **`setup_query_filter_flying(navmesh, filter_idx)`** - Ignores terrain

---

## Constants Reference

### Area Types (Terrain)
```python
POLYAREA_GROUND = 0    # Normal walkable ground
POLYAREA_WATER = 1     # Water (swimming required)
POLYAREA_ROAD = 2      # Roads (low cost, preferred)
POLYAREA_DOOR = 3      # Doors
POLYAREA_GRASS = 4     # Grass (slower movement)
POLYAREA_JUMP = 5      # Jump connections
POLYAREA_CLIMB = 6     # Climbable surfaces
POLYAREA_DANGER = 7    # Dangerous areas (high cost)
```

### Capability Flags
```python
POLYFLAGS_WALK = 0x01       # Can walk
POLYFLAGS_SWIM = 0x02       # Can swim
POLYFLAGS_DOOR = 0x04       # Can use doors
POLYFLAGS_JUMP = 0x08       # Can jump
POLYFLAGS_CLIMB = 0x10      # Can climb
POLYFLAGS_DISABLED = 0x20   # Disabled polygon
POLYFLAGS_ALL = 0xFFFF      # All abilities
```

### Crowd Behavior Flags
```python
CROWD_ANTICIPATE_TURNS = 1      # Anticipate turns
CROWD_OBSTACLE_AVOIDANCE = 2    # Avoid obstacles
CROWD_SEPARATION = 4            # Separate from other agents
CROWD_OPTIMIZE_VIS = 8          # Optimize visibility
CROWD_OPTIMIZE_TOPO = 16        # Optimize topology
```

### Agent States
```python
CROWDAGENT_STATE_INVALID = 0
CROWDAGENT_STATE_WALKING = 1
CROWDAGENT_STATE_OFFMESH = 2

CROWDAGENT_TARGET_NONE = 0
CROWDAGENT_TARGET_FAILED = 1
CROWDAGENT_TARGET_VALID = 2
CROWDAGENT_TARGET_REQUESTING = 3
CROWDAGENT_TARGET_WAITING_FOR_QUEUE = 4
CROWDAGENT_TARGET_WAITING_FOR_PATH = 5
CROWDAGENT_TARGET_VELOCITY = 6
```

### Formation Types
```python
FORMATION_LINE = 0      # Horizontal line
FORMATION_COLUMN = 1    # Vertical column
FORMATION_WEDGE = 2     # V-shaped
FORMATION_BOX = 3       # Rectangular grid
FORMATION_CIRCLE = 4    # Circular
```

---

## Cave Engine Examples

### Example 1: Simple Enemy AI

```python
import cave
from PyRecastDetour import Navmesh, create_default_agent_params

class EnemyAI(cave.Component):
    """Simple enemy that patrols waypoints"""

    patrol_waypoints = []  # Set in editor

    def start(self, scene):
        # Get global navmesh from scene
        manager = scene.getChild("NavMeshManager")
        self.navmesh = manager.get("NavMeshComponent").navmesh

        # Create agent
        params = create_default_agent_params()
        params["maxSpeed"] = 2.5
        pos = self.entity.getTransform().position
        self.agent_id = self.navmesh.add_agent([pos.x, pos.y, pos.z], params)

        self.waypoint_index = 0
        self.next_waypoint()

    def update(self):
        # Get agent position
        pos = self.navmesh.get_agent_position(self.agent_id)

        # Update entity transform
        transf = self.entity.getTransform()
        transf.position.set(pos[0], pos[1], pos[2])

        # Check if reached waypoint
        target = self.patrol_waypoints[self.waypoint_index]
        dist = cave.math.distance(transf.position, target)

        if dist < 2.0:
            self.next_waypoint()

    def next_waypoint(self):
        self.waypoint_index = (self.waypoint_index + 1) % len(self.patrol_waypoints)
        wp = self.patrol_waypoints[self.waypoint_index]
        self.navmesh.set_agent_target(self.agent_id, [wp.x, wp.y, wp.z])
```

### Example 2: Global NavMesh Manager

```python
import cave
from PyRecastDetour import Navmesh

class NavMeshComponent(cave.Component):
    """Global navigation mesh manager"""

    navmesh_file = "Content/Level1.obj"

    def start(self, scene):
        # Build navmesh
        self.navmesh = Navmesh()
        self.navmesh.init_by_obj(self.navmesh_file)

        # Configure for human-sized agents
        settings = self.navmesh.get_settings()
        settings["agentHeight"] = 1.8
        settings["agentRadius"] = 0.4
        settings["agentMaxClimb"] = 0.5
        self.navmesh.set_settings(settings)

        self.navmesh.build_navmesh()

        # Initialize crowd
        self.navmesh.init_crowd(maxAgents=100, maxAgentRadius=1.0)

        print("NavMesh built:", self.navmesh.get_log())

    def update(self):
        # Update crowd every frame
        dt = cave.getDeltaTime()
        self.navmesh.update_crowd(dt)
```

### Example 3: Squad Formation System

```python
from PyRecastDetour import FORMATION_WEDGE

class SquadController(cave.Component):
    """Control a squad of units in formation"""

    def start(self, scene):
        self.navmesh = scene.getChild("NavMeshManager").get("NavMeshComponent").navmesh
        self.formation_id = self.navmesh.create_formation(FORMATION_WEDGE, spacing=2.5)
        self.squad_agents = []

        # Create squad members
        for i in range(5):
            params = create_default_agent_params()
            pos = [10 + i*2, 0, 10]
            agent_id = self.navmesh.add_agent(pos, params)
            self.squad_agents.append(agent_id)
            self.navmesh.add_agent_to_formation(self.formation_id, agent_id)

    def update(self):
        dt = cave.getDeltaTime()

        # Update formations
        self.navmesh.update_formations(dt)

        # Update entity positions
        for agent_id in self.squad_agents:
            pos = self.navmesh.get_agent_position(agent_id)
            # Update corresponding entity...

    def move_to(self, target_pos, facing_dir):
        """Order squad to move"""
        self.navmesh.set_formation_target(
            self.formation_id,
            [target_pos.x, target_pos.y, target_pos.z],
            [facing_dir.x, facing_dir.y, facing_dir.z]
        )
```

### Example 4: Different Unit Types

```python
from PyRecastDetour import (
    POLYAREA_WATER, POLYFLAGS_WALK, POLYFLAGS_SWIM,
    setup_query_filter_infantry, setup_query_filter_amphibious
)

class UnitSpawner(cave.Component):
    def start(self, scene):
        self.navmesh = scene.getChild("NavMeshManager").get("NavMeshComponent").navmesh

        # Setup filters for different unit types
        setup_query_filter_infantry(self.navmesh, 0)      # Filter 0: Infantry
        setup_query_filter_amphibious(self.navmesh, 1)    # Filter 1: Marines

        # Spawn infantry (can't swim)
        infantry_params = create_default_agent_params()
        infantry_params["queryFilterType"] = 0
        infantry_id = self.navmesh.add_agent([10, 0, 10], infantry_params)

        # Spawn marine (can swim)
        marine_params = create_default_agent_params()
        marine_params["queryFilterType"] = 1
        marine_id = self.navmesh.add_agent([15, 0, 10], marine_params)

        # Infantry will avoid water, marines won't
        self.navmesh.set_agent_target(infantry_id, [90, 0, 90])
        self.navmesh.set_agent_target(marine_id, [90, 0, 90])
```

---

## Performance Tips

- **Navmesh Building:** Do this once at startup or pre-bake and use `save_navmesh()`
- **Crowd Updates:** Call `update_crowd()` once per frame for all agents
- **Agent Count:** 100+ agents at 60 FPS is typical
- **Cell Size:** Smaller = higher detail but slower build (default: 0.3)
- **Query Filters:** Use different filters for different unit types (infantry, vehicles, etc.)

---

## Troubleshooting

**No path found?**
- Check that both start and end are on navmesh
- Verify navmesh built successfully with `get_log()`
- Ensure agent radius fits through narrow passages

**Agents stuck?**
- Check `get_agent_state()` for `targetState`
- Verify target is reachable with `pathfind_straight()`
- Increase `collisionQueryRange` in agent params

**Agents won't use connections?**
- Ensure query filter includes required flags (`POLYFLAGS_JUMP`, etc.)
- Check connection was added BEFORE `build_navmesh()`

**Navmesh build fails?**
- Check file path exists for `init_by_obj()`
- Verify settings are valid (cell size > 0.0001)
- Review `get_log()` for error messages

---

## Documentation Files

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference cheat sheet
- **[FEATURES.md](FEATURES.md)** - Feature overview
- **[PYTHON_API.md](PYTHON_API.md)** - Detailed API documentation
- **[dist/example.py](dist/example.py)** - 7 complete code examples
- **[BUILD_SETUP.md](BUILD_SETUP.md)** - Build from source guide

---

## Version Info

**Current Version:** v1.1.0 Enhanced Edition

**Features Added:**
- ✅ Crowd simulation (17 functions)
- ✅ Convex volumes (5 functions)
- ✅ Off-mesh connections (5 functions)
- ✅ Auto-markup system (6 functions)
- ✅ Advanced crowd features (6 functions)
- ✅ Formations (9 functions)
- ✅ Helper functions (6 functions)

**Total:** 80+ functions available

---

## Creating Releases

### Automatic GitHub Release

This repository includes a GitHub Actions workflow that automatically creates releases when you push a version tag.

**Steps:**

1. Commit your changes:
   ```bash
   git add .
   git commit -m "Prepare version 1.2.0"
   ```

2. Create and push a version tag:
   ```bash
   git tag v1.2.0
   git push origin v1.2.0
   ```

3. GitHub Actions will automatically:
   - Zip the `dist/` folder
   - Create a GitHub Release
   - Upload `PyRecastDetour-dist.zip` as an asset
   - Generate release notes

### Manual Release (Local)

Use the included scripts to create a release zip locally:

**Windows (Batch):**
```batch
create_release.bat 1.2.0
```

**Windows (PowerShell):**
```powershell
.\create_release.ps1 -Version 1.2.0
```

These scripts will create `PyRecastDetour-v1.2.0-dist.zip` in the project root.

---

## Credits

- **Recast Navigation:** Mikko Mononen
- **Original PyRecastDetour:** Tugcga
- **Cave Engine Edition:** nicrf
- **Enhanced with:** Claude AI assistance

---

**Built for the Cave Engine game development community** 🎮
