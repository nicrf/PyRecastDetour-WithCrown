# PyRecastDetour Advanced Features - Examples

This directory contains comprehensive examples demonstrating all the advanced features added to PyRecastDetour.

## Overview of New Features

PyRecastDetour now includes extensive advanced features for professional navigation and crowd simulation:

### 1. Convex Volumes (Nav Volumes)
Mark different terrain types with custom properties:
- Water zones (swimming required)
- Roads (preferred paths, lower cost)
- Grass areas (slower movement)
- Danger zones (high cost, avoided)
- Custom area types

### 2. Off-Mesh Connections
Special navigation links for:
- Jump connections (one-way or bidirectional)
- Ladders and climbing surfaces
- Teleports and doors
- Custom connections with flags and areas

### 3. Advanced Crowd Management
- **Obstacle Avoidance Profiles**: Aggressive, Passive, Defensive, Custom
- **Query Filters**: Different movement capabilities per agent type (Infantry, Amphibious, Flying)
- **Agent Queries**: Neighbors, path corners, active agents
- **Runtime Updates**: Change agent parameters during simulation

### 4. Auto-Markup System
Automatic area marking using geometric shapes:
- Box areas
- Cylinder areas
- Convex polygon areas
- Walkable slope configuration

## Examples

### test_convex_volumes.py
Demonstrates convex volume creation and management:
```bash
python examples/test_convex_volumes.py
```

Features:
- Creating water, road, and danger zones
- Querying volume information
- Building navmesh with volumes
- Deleting volumes

### test_offmesh_connections.py
Shows off-mesh connection usage:
```bash
python examples/test_offmesh_connections.py
```

Features:
- Jump connections (unidirectional)
- Ladder connections (bidirectional)
- Door/teleport connections
- Pathfinding using connections

### test_crowd_advanced.py
Advanced crowd simulation features:
```bash
python examples/test_crowd_advanced.py
```

Features:
- Multiple obstacle avoidance profiles
- Query filters for different agent types
- Agent neighbor detection
- Path corner queries
- Active agent management
- Runtime parameter updates

### test_auto_markup.py
Automatic area marking:
```bash
python examples/test_auto_markup.py
```

Features:
- Box area marking
- Cylinder area marking
- Convex polygon marking
- Walkable slope configuration
- Area erosion
- Median filtering

### test_complete_example.py
Comprehensive example combining all features:
```bash
python examples/test_complete_example.py
```

Features:
- Full navmesh setup with terrain areas
- Off-mesh connections
- Multiple agent types (Infantry, Marines, Civilians, Vehicles)
- Different avoidance profiles
- Query filters
- Complete simulation with analysis

## API Reference

### Convex Volumes

```python
# Add a convex volume
navmesh.add_convex_volume(
    verts=[x1, y1, z1, x2, y2, z2, ...],  # 3-12 points
    minh=0.0,
    maxh=2.0,
    area=POLYAREA_WATER
)

# Query volumes
count = navmesh.get_convex_volume_count()
volume = navmesh.get_convex_volume(index)
all_volumes = navmesh.get_all_convex_volumes()

# Delete volume
navmesh.delete_convex_volume(index)
```

### Off-Mesh Connections

```python
# Add connection
navmesh.add_offmesh_connection(
    start_pos=[x1, y1, z1],
    end_pos=[x2, y2, z2],
    radius=0.5,
    bidirectional=True,
    area=POLYAREA_JUMP,
    flags=POLYFLAGS_JUMP
)

# Query connections
count = navmesh.get_offmesh_connection_count()
conn = navmesh.get_offmesh_connection(index)
all_conns = navmesh.get_all_offmesh_connections()

# Delete connection
navmesh.delete_offmesh_connection(index)
```

### Advanced Crowd

```python
# Setup obstacle avoidance
params = create_obstacle_avoidance_params("aggressive")
navmesh.set_obstacle_avoidance_params(0, params)

# Setup query filter
setup_query_filter_infantry(navmesh, 0)
# Or manually:
navmesh.set_query_filter_area_cost(0, POLYAREA_WATER, 10.0)
navmesh.set_query_filter_include_flags(0, POLYFLAGS_WALK | POLYFLAGS_JUMP)

# Agent queries
neighbors = navmesh.get_agent_neighbors(agent_id)
corners = navmesh.get_agent_corners(agent_id)
active = navmesh.get_active_agents()
is_active = navmesh.is_agent_active(agent_id)
params = navmesh.get_agent_parameters(agent_id)
```

### Auto-Markup

```python
# Mark box area
navmesh.mark_box_area(
    bmin=[x1, y1, z1],
    bmax=[x2, y2, z2],
    area_id=POLYAREA_ROAD
)

# Mark cylinder area
navmesh.mark_cylinder_area(
    pos=[x, y, z],
    radius=5.0,
    height=2.0,
    area_id=POLYAREA_WATER
)

# Mark convex polygon
navmesh.mark_convex_poly_area(
    verts=[x1, y1, z1, x2, y2, z2, ...],
    hmin=0.0,
    hmax=2.0,
    area_id=POLYAREA_DANGER
)
```

## Constants

### Area Types
- `POLYAREA_GROUND` (0) - Normal walkable ground
- `POLYAREA_WATER` (1) - Water (swimming required)
- `POLYAREA_ROAD` (2) - Roads (preferred path)
- `POLYAREA_DOOR` (3) - Doors
- `POLYAREA_GRASS` (4) - Grass (slower)
- `POLYAREA_JUMP` (5) - Jump connections
- `POLYAREA_CLIMB` (6) - Climbable surfaces
- `POLYAREA_DANGER` (7) - Dangerous areas

### Poly Flags
- `POLYFLAGS_WALK` (0x01) - Can walk
- `POLYFLAGS_SWIM` (0x02) - Can swim
- `POLYFLAGS_DOOR` (0x04) - Can use doors
- `POLYFLAGS_JUMP` (0x08) - Can jump
- `POLYFLAGS_CLIMB` (0x10) - Can climb
- `POLYFLAGS_DISABLED` (0x20) - Disabled
- `POLYFLAGS_ALL` (0xFFFF) - All abilities

### Crowd Flags
- `CROWD_ANTICIPATE_TURNS` (1)
- `CROWD_OBSTACLE_AVOIDANCE` (2)
- `CROWD_SEPARATION` (4)
- `CROWD_OPTIMIZE_VIS` (8)
- `CROWD_OPTIMIZE_TOPO` (16)

## Helper Functions

```python
# Create default agent parameters
params = create_default_agent_params()

# Create vehicle parameters
vehicle_params = create_vehicle_params()

# Create obstacle avoidance parameters
avoid_params = create_obstacle_avoidance_params("aggressive")  # or "passive", "defensive"

# Setup query filters
setup_query_filter_infantry(navmesh, 0)
setup_query_filter_amphibious(navmesh, 1)
setup_query_filter_flying(navmesh, 2)
```

## Requirements

- PyRecastDetour compiled module
- Python 3.6+
- An OBJ file for testing (replace "level.obj" in examples)

## Notes

1. **OBJ Files**: All examples require an OBJ file. Replace `"level.obj"` with your actual geometry file.

2. **Build Order**: Always call functions in this order:
   ```python
   navmesh.init_by_obj("file.obj")
   # Add volumes and connections here
   navmesh.build_navmesh()
   navmesh.init_crowd(...)
   ```

3. **Performance**: Convex volumes and off-mesh connections are processed during navmesh build. Add them before calling `build_navmesh()`.

4. **Query Filters**: Must be set up after `init_crowd()` and before adding agents.

5. **Agent Updates**: Use `update_agent_parameters()` to modify agent behavior at runtime.

## Troubleshooting

**Q: Agents don't use off-mesh connections**
A: Ensure the agent's query filter includes the appropriate flags (e.g., `POLYFLAGS_JUMP` for jump connections)

**Q: Areas don't affect pathfinding**
A: Check that query filter area costs are set correctly. Higher costs mean agents avoid those areas.

**Q: Agents collide too much**
A: Adjust `separationWeight` parameter or use different obstacle avoidance profiles.

**Q: Navmesh build fails**
A: Check the build log with `navmesh.get_log()` for error messages.

## License

Same as PyRecastDetour main project.
