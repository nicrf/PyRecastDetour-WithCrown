# PyRecastDetour - Advanced Features Documentation

## Version 1.1.0 - Complete Feature Set

This document describes all the advanced features added to PyRecastDetour, providing professional-grade navigation and crowd simulation capabilities.

---

## Table of Contents

1. [Nav Volumes & 3D Navigation](#nav-volumes--3d-navigation)
2. [Off-Mesh Connections](#off-mesh-connections)
3. [Auto-Markup System](#auto-markup-system)
4. [Advanced Crowd Management](#advanced-crowd-management)
5. [Complete API Reference](#complete-api-reference)

---

## Nav Volumes & 3D Navigation

### Overview

Convex volumes allow you to mark specific areas of the navmesh with custom properties, enabling sophisticated gameplay mechanics and AI behaviors.

### Use Cases

- **Water zones**: Areas requiring swimming
- **Roads**: Preferred paths with lower traversal cost
- **Danger zones**: High-cost areas agents avoid
- **Grass/mud**: Slower movement areas
- **Custom zones**: Any gameplay-specific area type

### API

```python
# Add a convex volume (3-12 vertices, counterclockwise)
navmesh.add_convex_volume(
    verts=[x1, y1, z1, x2, y2, z2, ...],  # Flat list of 3D points
    minh=0.0,                              # Minimum height
    maxh=2.0,                              # Maximum height
    area=POLYAREA_WATER                    # Area type
)

# Query volumes
count = navmesh.get_convex_volume_count()
volume = navmesh.get_convex_volume(index)  # Returns dict with 'verts', 'hmin', 'hmax', 'area'
all_volumes = navmesh.get_all_convex_volumes()  # Returns list of dicts

# Delete volume
navmesh.delete_convex_volume(index)
```

### Example

```python
# Water pond (rectangular)
water_verts = [
    10.0, 0.0, 10.0,
    20.0, 0.0, 10.0,
    20.0, 0.0, 20.0,
    10.0, 0.0, 20.0
]
navmesh.add_convex_volume(water_verts, 0.0, 2.0, POLYAREA_WATER)

# Build navmesh to apply volumes
navmesh.build_navmesh()
```

### Area Types

- `POLYAREA_GROUND` (0): Normal walkable terrain
- `POLYAREA_WATER` (1): Water (requires swimming)
- `POLYAREA_ROAD` (2): Roads (lower cost, preferred)
- `POLYAREA_DOOR` (3): Doors (can be toggled)
- `POLYAREA_GRASS` (4): Grass (higher cost)
- `POLYAREA_JUMP` (5): Jump zones
- `POLYAREA_CLIMB` (6): Climbable areas
- `POLYAREA_DANGER` (7): Dangerous (very high cost)

---

## Off-Mesh Connections

### Overview

Off-mesh connections create special navigation links that allow agents to traverse gaps, climb ladders, jump between platforms, or use teleports.

### Use Cases

- **Jumps**: One-way shortcuts across gaps
- **Ladders**: Bidirectional vertical connections
- **Doors**: Connections that can be enabled/disabled
- **Teleports**: Instant transport between distant points
- **Ziplines**: Fast traversal paths

### API

```python
# Add off-mesh connection
navmesh.add_offmesh_connection(
    start_pos=[x1, y1, z1],       # Start position
    end_pos=[x2, y2, z2],         # End position
    radius=0.5,                    # Connection radius
    bidirectional=True,            # Can traverse both ways
    area=POLYAREA_JUMP,            # Area type
    flags=POLYFLAGS_JUMP           # Required flags to use
)

# Query connections
count = navmesh.get_offmesh_connection_count()
conn = navmesh.get_offmesh_connection(index)
# Returns dict with 'start', 'end', 'radius', 'bidirectional', 'area', 'flags'
all_conns = navmesh.get_all_offmesh_connections()

# Delete connection
navmesh.delete_offmesh_connection(index)
```

### Example

```python
# Jump connection (one-way)
navmesh.add_offmesh_connection(
    start_pos=[5.0, 2.0, 5.0],
    end_pos=[10.0, 3.0, 10.0],
    radius=0.5,
    bidirectional=False,
    area=POLYAREA_JUMP,
    flags=POLYFLAGS_JUMP
)

# Ladder (bidirectional)
navmesh.add_offmesh_connection(
    start_pos=[15.0, 0.0, 5.0],
    end_pos=[15.0, 5.0, 5.0],
    radius=0.3,
    bidirectional=True,
    area=POLYAREA_CLIMB,
    flags=POLYFLAGS_CLIMB
)

# Agent must have appropriate flags in query filter to use connections
navmesh.set_query_filter_include_flags(0, POLYFLAGS_WALK | POLYFLAGS_JUMP | POLYFLAGS_CLIMB)
```

### Poly Flags

- `POLYFLAGS_WALK` (0x01): Standard walking
- `POLYFLAGS_SWIM` (0x02): Swimming ability
- `POLYFLAGS_DOOR` (0x04): Can use doors
- `POLYFLAGS_JUMP` (0x08): Can jump
- `POLYFLAGS_CLIMB` (0x10): Can climb
- `POLYFLAGS_DISABLED` (0x20): Disabled polygon
- `POLYFLAGS_ALL` (0xFFFF): All abilities

---

## Auto-Markup System

### Overview

Automatic area marking using geometric primitives, eliminating the need for manual vertex definition.

### API

```python
# Mark box area
navmesh.mark_box_area(
    bmin=[x1, y1, z1],  # Minimum bounds
    bmax=[x2, y2, z2],  # Maximum bounds
    area_id=POLYAREA_ROAD
)

# Mark cylinder area
navmesh.mark_cylinder_area(
    pos=[x, y, z],      # Center position
    radius=5.0,         # Radius
    height=2.0,         # Height
    area_id=POLYAREA_WATER
)

# Mark convex polygon area
navmesh.mark_convex_poly_area(
    verts=[x1, y1, z1, x2, y2, z2, ...],  # Vertices
    hmin=0.0,          # Min height
    hmax=2.0,          # Max height
    area_id=POLYAREA_GRASS
)

# Configure walkable slope
navmesh.mark_walkable_triangles(walkable_slope_angle=45.0)

# Erode walkable area (keeps agents from edges)
navmesh.erode_walkable_area(radius=2)

# Apply median filter (smoothing)
navmesh.median_filter_walkable_area()
```

### Example

```python
# Mark a road network
navmesh.mark_box_area([0, 0, 0], [100, 1, 5], POLYAREA_ROAD)

# Mark a circular water pond
navmesh.mark_cylinder_area([25, 0, 25], 10.0, 2.0, POLYAREA_WATER)

# Mark a danger zone (custom polygon)
danger_verts = [10, 0, 10, 15, 0, 10, 12.5, 0, 15]
navmesh.mark_convex_poly_area(danger_verts, 0.0, 2.0, POLYAREA_DANGER)

navmesh.build_navmesh()
```

---

## Advanced Crowd Management

### Overview

Professional-grade crowd simulation with customizable behaviors, query filters, and obstacle avoidance.

### 1. Obstacle Avoidance Profiles

Configure how agents avoid obstacles and other agents.

```python
# Set up avoidance profile
params = {
    "velBias": 0.4,          # Velocity bias
    "weightDesVel": 2.0,     # Weight for desired velocity
    "weightCurVel": 0.75,    # Weight for current velocity
    "weightSide": 0.75,      # Side preference weight
    "weightToi": 2.5,        # Time-to-impact weight
    "horizTime": 2.5,        # Horizon time
    "gridSize": 33,          # Sampling grid size
    "adaptiveDivs": 7,       # Adaptive divisions
    "adaptiveRings": 2,      # Adaptive rings
    "adaptiveDepth": 5       # Adaptive depth
}
navmesh.set_obstacle_avoidance_params(0, params)

# Or use presets
navmesh.set_obstacle_avoidance_params(0, create_obstacle_avoidance_params("aggressive"))
navmesh.set_obstacle_avoidance_params(1, create_obstacle_avoidance_params("passive"))
navmesh.set_obstacle_avoidance_params(2, create_obstacle_avoidance_params("defensive"))

# Assign to agent
agent_params["obstacleAvoidanceType"] = 0  # Use profile 0
```

**Profiles:**
- **Aggressive**: Direct pathfinding, less cautious
- **Passive**: More cautious, maintains distance
- **Defensive**: Very cautious, large safety margins
- **Default**: Balanced behavior

### 2. Query Filters

Control which areas and connections each agent type can use.

```python
# Set area costs (higher = avoid more)
navmesh.set_query_filter_area_cost(filter_index, POLYAREA_WATER, 10.0)  # Avoid water
navmesh.set_query_filter_area_cost(filter_index, POLYAREA_ROAD, 0.5)    # Prefer roads

# Set capability flags
navmesh.set_query_filter_include_flags(filter_index, POLYFLAGS_WALK | POLYFLAGS_JUMP)
navmesh.set_query_filter_exclude_flags(filter_index, POLYFLAGS_SWIM | POLYFLAGS_DISABLED)

# Get area cost
cost = navmesh.get_query_filter_area_cost(filter_index, area_id)

# Or use helper functions
setup_query_filter_infantry(navmesh, 0)     # Can walk, jump, not swim
setup_query_filter_amphibious(navmesh, 1)  # Can walk and swim
setup_query_filter_flying(navmesh, 2)      # Ignores terrain

# Assign to agent
agent_params["queryFilterType"] = 0  # Use filter 0
```

### 3. Agent Queries

Get detailed information about agents during simulation.

```python
# Get neighboring agents
neighbors = navmesh.get_agent_neighbors(agent_id)  # Returns list of agent IDs

# Get path corners
corners = navmesh.get_agent_corners(agent_id)  # Returns [x,y,z, x,y,z, ...]

# Get all active agents
active = navmesh.get_active_agents()  # Returns list of active agent IDs

# Check if agent is active
is_active = navmesh.is_agent_active(agent_id)  # Returns bool

# Get agent parameters
params = navmesh.get_agent_parameters(agent_id)  # Returns dict

# Get max agent count
max_count = navmesh.get_max_agent_count()

# Get query half extents
extents = navmesh.get_query_half_extents()  # Returns [x, y, z]
```

### 4. Runtime Updates

Modify agent behavior during simulation.

```python
# Update agent parameters
new_params = {
    "maxSpeed": 5.0,
    "maxAcceleration": 10.0,
    "separationWeight": 3.0
}
navmesh.update_agent_parameters(agent_id, new_params)
```

### Complete Example

```python
# Setup
navmesh.init_crowd(maxAgents=100, maxAgentRadius=2.0)

# Configure profiles
navmesh.set_obstacle_avoidance_params(0, create_obstacle_avoidance_params("aggressive"))
setup_query_filter_infantry(navmesh, 0)

# Create agent
params = create_default_agent_params()
params["obstacleAvoidanceType"] = 0  # Aggressive avoidance
params["queryFilterType"] = 0        # Infantry filter
params["maxSpeed"] = 4.0

agent_id = navmesh.add_agent([5, 0, 5], params)
navmesh.set_agent_target(agent_id, [50, 0, 50])

# Simulation loop
dt = 0.016  # 60 FPS
for frame in range(600):  # 10 seconds
    navmesh.update_crowd(dt)

    # Query agent
    if navmesh.is_agent_active(agent_id):
        pos = navmesh.get_agent_position(agent_id)
        vel = navmesh.get_agent_velocity(agent_id)
        neighbors = navmesh.get_agent_neighbors(agent_id)
        corners = navmesh.get_agent_corners(agent_id)

        print(f"Frame {frame}: Pos {pos}, Speed {sum(v**2 for v in vel)**0.5:.2f}, Neighbors {len(neighbors)}")
```

---

## Complete API Reference

### Convex Volumes
- `add_convex_volume(verts, minh, maxh, area)`
- `delete_convex_volume(index)`
- `get_convex_volume_count()`
- `get_convex_volume(index)`
- `get_all_convex_volumes()`

### Off-Mesh Connections
- `add_offmesh_connection(start_pos, end_pos, radius, bidirectional, area, flags)`
- `delete_offmesh_connection(index)`
- `get_offmesh_connection_count()`
- `get_offmesh_connection(index)`
- `get_all_offmesh_connections()`

### Auto-Markup
- `mark_walkable_triangles(walkable_slope_angle)`
- `mark_box_area(bmin, bmax, area_id)`
- `mark_cylinder_area(pos, radius, height, area_id)`
- `mark_convex_poly_area(verts, hmin, hmax, area_id)`
- `erode_walkable_area(radius)`
- `median_filter_walkable_area()`

### Advanced Crowd
- `set_obstacle_avoidance_params(idx, params)`
- `get_obstacle_avoidance_params(idx)`
- `set_query_filter_area_cost(filter_index, area_id, cost)`
- `get_query_filter_area_cost(filter_index, area_id)`
- `set_query_filter_include_flags(filter_index, flags)`
- `set_query_filter_exclude_flags(filter_index, flags)`
- `get_agent_neighbors(agent_idx)`
- `get_agent_corners(agent_idx)`
- `get_active_agents()`
- `get_max_agent_count()`
- `get_query_half_extents()`
- `is_agent_active(idx)`
- `get_agent_parameters(idx)`

### Helper Functions
- `create_default_agent_params()`
- `create_vehicle_params()`
- `create_obstacle_avoidance_params(profile)`
- `setup_query_filter_infantry(navmesh, filter_index)`
- `setup_query_filter_amphibious(navmesh, filter_index)`
- `setup_query_filter_flying(navmesh, filter_index)`

---

## Performance Considerations

1. **Convex Volumes**: Processed during navmesh build. Add before calling `build_navmesh()`.

2. **Off-Mesh Connections**: Also processed during build. Maximum 256 connections.

3. **Query Filters**: Configure once after `init_crowd()`, before adding agents.

4. **Obstacle Avoidance**: Up to 8 profiles can be configured. Choose based on agent type.

5. **Agent Queries**: `get_agent_neighbors()` and `get_agent_corners()` are fast, call every frame if needed.

---

## Migration Guide

### From Previous Version

```python
# Old way (limited)
navmesh = Navmesh()
navmesh.init_by_obj("level.obj")
navmesh.build_navmesh()
navmesh.init_crowd(100, 1.0)
agent = navmesh.add_agent([0,0,0], params)

# New way (with advanced features)
navmesh = Navmesh()
navmesh.init_by_obj("level.obj")

# Add terrain marking
navmesh.mark_cylinder_area([25,0,25], 10.0, 2.0, POLYAREA_WATER)

# Add special connections
navmesh.add_offmesh_connection([5,2,5], [10,3,10], 0.5, False, POLYAREA_JUMP, POLYFLAGS_JUMP)

navmesh.build_navmesh()
navmesh.init_crowd(100, 1.0)

# Configure behaviors
navmesh.set_obstacle_avoidance_params(0, create_obstacle_avoidance_params("aggressive"))
setup_query_filter_infantry(navmesh, 0)

# Create specialized agent
params = create_default_agent_params()
params["obstacleAvoidanceType"] = 0
params["queryFilterType"] = 0
agent = navmesh.add_agent([0,0,0], params)

# Advanced queries
neighbors = navmesh.get_agent_neighbors(agent)
```

---

## License

PyRecastDetour is provided under the same license as the Recast Navigation library.

For more information, visit: https://github.com/recastnavigation/recastnavigation
