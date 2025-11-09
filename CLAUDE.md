# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**PyRecastDetour-Sources** is the source code for building Python bindings to the [Recast Navigation](https://github.com/recastnavigation/recastnavigation) library. It provides pathfinding and navigation mesh generation capabilities for Python applications, particularly for game AI and robotics applications.

This is a **C++ codebase with Python bindings** built using PyBind11. The module wraps the Recast Navigation library to expose navmesh building and pathfinding functionality to Python.

## Build Requirements

The project requires:
- PyBind11 for Python-C++ bindings
- Recast Navigation libraries (included in `lib/`)
- Recast Navigation headers (included in `include/recastnavigation/`)
- Multiple Python version support (Python 2, 3.6, 3.7, 3.8, 3.9, 3.10)

Pre-built libraries are provided:
- `lib/Recast.lib` - Core navmesh generation
- `lib/Detour.lib` - Pathfinding queries
- `lib/DetourCrowd.lib` - Crowd simulation
- `lib/DetourTileCache.lib` - Dynamic obstacle support
- `lib/DebugUtils.lib` - Debugging utilities

## Architecture

### Core Components

**Navmesh.h/cpp** - Main Python API wrapper class
- `Navmesh` class manages the entire navmesh lifecycle
- Wraps Recast's mesh building and Detour's pathfinding
- Provides initialization from OBJ files or raw vertex/face data
- State tracking: `is_init` (geometry loaded), `is_build` (navmesh built)

**PyRecastDetour.cpp** - PyBind11 bindings
- Defines Python module for different Python versions (Py2RecastDetour, Py36RecastDetour, etc.)
- Exposes all `Navmesh` methods to Python
- Controlled by preprocessor defines: `_Python2`, `_Python36`, `_Python37`, `_Python38`, `_Python39`, `_Python310`

**InputGeom.h/cpp** - Geometry management
- Handles mesh loading from OBJ files or raw data
- Manages convex volumes for custom area definitions
- Provides bounding box and mesh data access

**Sample_SoloMesh.h/cpp** - Single-mesh navmesh builder
- Implements solo (non-tiled) navmesh generation
- Configures build settings (cell size, agent dimensions, etc.)
- Handles intermediate build results (heightfield, contours, polymesh)

### Mesh Building Pipeline

1. **Initialization**: Load geometry via `init_by_obj()` or `init_by_raw()`
2. **Configuration**: Set build parameters via `set_settings()` (agent height/radius, cell size, etc.)
3. **Building**: Call `build_navmesh()` to generate navigation mesh
4. **Querying**: Use pathfinding methods (`pathfind_straight()`, `raycast()`, `distance_to_wall()`)
5. **Persistence**: Save/load navmesh with `save_navmesh()`/`load_navmesh()`

### Build Settings

Critical parameters exposed through `BuildSettings`:
- `cellSize`, `cellHeight` - Voxelization resolution
- `agentHeight`, `agentRadius` - Agent dimensions
- `agentMaxClimb`, `agentMaxSlope` - Traversal constraints
- `regionMinSize`, `regionMergeSize` - Region building
- `edgeMaxLen`, `edgeMaxError` - Edge simplification
- `vertsPerPoly` - Polygon complexity (3-6 vertices)
- `detailSampleDist`, `detailSampleMaxError` - Detail mesh generation

### Python API

The `Navmesh` class exposes these methods to Python:
- `init_by_obj(file_path)` - Load geometry from OBJ file
- `init_by_raw(vertices, faces)` - Load from vertex/face arrays
- `build_navmesh()` - Generate the navigation mesh
- `get_log()` - Retrieve build log messages (clears after call)
- `pathfind_straight(start, end, vertex_mode=0)` - Find path between two points
- `pathfind_straight_batch(coordinates, vertex_mode=0)` - Batch pathfinding
- `distance_to_wall(point)` - Query distance to nearest obstacle
- `raycast(start, end)` - Cast ray through navmesh
- `get_settings()` / `set_settings(settings)` - Query/modify build parameters
- `get_partition_type()` / `set_partition_type(type)` - Control region partitioning
- `get_bounding_box()` - Get geometry bounds
- `save_navmesh(file_path)` / `load_navmesh(file_path)` - Serialize navmesh
- `get_navmesh_trianglulation()` - Export navmesh as triangles
- `get_navmesh_polygonization()` - Export navmesh as polygons
- `hit_mesh(start, end)` - Ray intersection with input geometry

### Crowd Simulation API

The `Navmesh` class also provides crowd simulation capabilities through Detour Crowd:

**Initialization:**
- `init_crowd(maxAgents, maxAgentRadius)` - Initialize crowd manager (requires built navmesh)
  - Returns `True` on success, `False` on failure
  - Must be called before adding agents

**Agent Management:**
- `add_agent(pos, params)` - Add new agent to crowd
  - `pos`: [x, y, z] position vector
  - `params`: Dictionary with agent parameters (see Agent Parameters below)
  - Returns agent index (int) or -1 on failure

- `remove_agent(idx)` - Remove agent from crowd
  - `idx`: Agent index returned by `add_agent()`

- `update_agent_parameters(idx, params)` - Update agent configuration at runtime
  - `idx`: Agent index
  - `params`: Dictionary with parameters to update

**Agent Control:**
- `set_agent_target(idx, pos)` - Set agent's navigation target
  - Returns `True` on success, `False` on failure
  - Position is automatically snapped to nearest navmesh polygon

- `set_agent_velocity(idx, vel)` - Set agent's velocity directly
  - `vel`: [x, y, z] velocity vector
  - Use for manual control instead of pathfinding

- `reset_agent_target(idx)` - Clear agent's current target

**Simulation:**
- `update_crowd(dt)` - Update crowd simulation
  - `dt`: Delta time in seconds (e.g., 0.016 for 60 FPS)
  - Must be called every frame to update agent positions

**Agent Queries:**
- `get_agent_position(idx)` - Returns [x, y, z] current position
- `get_agent_velocity(idx)` - Returns [x, y, z] current velocity
- `get_agent_count()` - Returns total number of agents in crowd
- `get_agent_state(idx)` - Returns dictionary with full agent state:
  - Position: `posX`, `posY`, `posZ`
  - Velocity: `velX`, `velY`, `velZ`
  - Desired velocity: `dvelX`, `dvelY`, `dvelZ`
  - Adjusted velocity: `nvelX`, `nvelY`, `nvelZ`
  - Parameters: `radius`, `height`, `maxSpeed`, `maxAcceleration`, etc.
  - State: `active`, `state`, `partial`
  - Target: `targetState`, `targetPosX`, `targetPosY`, `targetPosZ`

### Agent Parameters

Agent behavior is configured via a dictionary with these keys:

**Physical Properties:**
- `radius` (float, default 0.6) - Agent collision radius
- `height` (float, default 2.0) - Agent height
- `maxAcceleration` (float, default 8.0) - Maximum acceleration
- `maxSpeed` (float, default 3.5) - Maximum movement speed

**Pathfinding:**
- `collisionQueryRange` (float, default radius*12) - Collision detection range
- `pathOptimizationRange` (float, default radius*30) - Path optimization range

**Steering Behavior:**
- `separationWeight` (float, default 2.0) - Agent separation strength
- `updateFlags` (int, default 15) - Bitwise flags controlling behavior:
  - `1` (DT_CROWD_ANTICIPATE_TURNS) - Anticipate turns
  - `2` (DT_CROWD_OBSTACLE_AVOIDANCE) - Enable obstacle avoidance
  - `4` (DT_CROWD_SEPARATION) - Enable agent separation
  - `8` (DT_CROWD_OPTIMIZE_VIS) - Optimize visibility along path
  - `16` (DT_CROWD_OPTIMIZE_TOPO) - Optimize path topology

- `obstacleAvoidanceType` (int, default 3) - Avoidance quality (0-7)
- `queryFilterType` (int, default 0) - Query filter index

**Example:**
```python
agent_params = {
    "radius": 0.5,
    "height": 2.0,
    "maxSpeed": 4.0,
    "maxAcceleration": 10.0,
    "updateFlags": 15  # All features enabled
}
agent_id = navmesh.add_agent([5.0, 0.0, 5.0], agent_params)
```

### Crowd States

Agent states (returned in `get_agent_state()`):
- `DT_CROWDAGENT_STATE_INVALID` (0) - Invalid/error state
- `DT_CROWDAGENT_STATE_WALKING` (1) - Walking on navmesh
- `DT_CROWDAGENT_STATE_OFFMESH` (2) - Traversing off-mesh connection

Target states (returned in `targetState`):
- `DT_CROWDAGENT_TARGET_NONE` (0) - No target set
- `DT_CROWDAGENT_TARGET_FAILED` (1) - Failed to reach target
- `DT_CROWDAGENT_TARGET_VALID` (2) - Has valid target
- `DT_CROWDAGENT_TARGET_REQUESTING` (3) - Requesting path
- `DT_CROWDAGENT_TARGET_WAITING_FOR_QUEUE` (4) - Waiting in queue
- `DT_CROWDAGENT_TARGET_WAITING_FOR_PATH` (5) - Waiting for path calculation
- `DT_CROWDAGENT_TARGET_VELOCITY` (6) - Using direct velocity control

## Additional Tools

**NavMeshTesterTool** - Pathfinding testing
- Used internally by `Navmesh` for path queries
- Handles straight path computation and random point sampling

**Sample_TileMesh** - Tiled navmesh support (not exposed to Python in base wrapper)
**Sample_TempObstacles** - Dynamic obstacle support (not exposed to Python in base wrapper)

## Partition Types

Three partitioning algorithms available:
- `SAMPLE_PARTITION_WATERSHED` (0) - Default, best quality
- `SAMPLE_PARTITION_MONOTONE` (1) - Faster, simpler regions
- `SAMPLE_PARTITION_LAYERS` (2) - For layered/overlapping geometry

## Important Notes

- The `BuildContext` (`ctx`) captures log messages during mesh building; retrieve with `get_log()`
- Settings must be configured AFTER initialization and BEFORE building
- `vertsPerPoly` is clamped to [3, 6] range automatically
- Pathfinding returns flat float arrays representing 3D coordinates
- Crowd must be initialized AFTER navmesh is built
- Crowd simulation requires regular `update_crowd()` calls to move agents
- Agent parameters can be updated at runtime but may cause temporary behavior changes
- Module name varies by Python version due to different compiled artifacts
