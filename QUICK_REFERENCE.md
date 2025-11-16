# PyRecastDetour v1.1.0 - Quick Reference

## Quick Start

```python
import PyRecastDetour as prd

# Setup
navmesh = prd.Navmesh()
navmesh.init_by_obj("level.obj")
navmesh.build_navmesh()
navmesh.init_crowd(100, 1.0)

# Create agent
params = prd.create_default_agent_params()
agent = navmesh.add_agent([0, 0, 0], params)
navmesh.set_agent_target(agent, [50, 0, 50])

# Update loop
navmesh.update_crowd(0.016)
```

## Cheat Sheet

### Convex Volumes
```python
# Add water zone
navmesh.add_convex_volume([x1,y1,z1, x2,y2,z2, ...], 0.0, 2.0, prd.POLYAREA_WATER)

# Query
count = navmesh.get_convex_volume_count()
vols = navmesh.get_all_convex_volumes()
```

### Off-Mesh Connections
```python
# Add jump
navmesh.add_offmesh_connection([x1,y1,z1], [x2,y2,z2], 0.5, False,
                               prd.POLYAREA_JUMP, prd.POLYFLAGS_JUMP)

# Query
count = navmesh.get_offmesh_connection_count()
conns = navmesh.get_all_offmesh_connections()
```

### Auto-Markup
```python
# Box area
navmesh.mark_box_area([x1,y1,z1], [x2,y2,z2], prd.POLYAREA_ROAD)

# Cylinder area
navmesh.mark_cylinder_area([x,y,z], radius, height, prd.POLYAREA_WATER)

# Polygon area
navmesh.mark_convex_poly_area([x1,y1,z1, ...], hmin, hmax, prd.POLYAREA_GRASS)
```

### Obstacle Avoidance
```python
# Set profile
navmesh.set_obstacle_avoidance_params(0, prd.create_obstacle_avoidance_params("aggressive"))

# Use in agent
params["obstacleAvoidanceType"] = 0
```

### Query Filters
```python
# Setup filter
prd.setup_query_filter_infantry(navmesh, 0)

# Or manually
navmesh.set_query_filter_area_cost(0, prd.POLYAREA_WATER, 10.0)
navmesh.set_query_filter_include_flags(0, prd.POLYFLAGS_WALK | prd.POLYFLAGS_JUMP)

# Use in agent
params["queryFilterType"] = 0
```

### Agent Queries
```python
# Neighbors
neighbors = navmesh.get_agent_neighbors(agent_id)

# Path corners
corners = navmesh.get_agent_corners(agent_id)

# Active agents
active = navmesh.get_active_agents()

# Check active
if navmesh.is_agent_active(agent_id):
    pos = navmesh.get_agent_position(agent_id)

# Get params
params = navmesh.get_agent_parameters(agent_id)
```

## Constants Reference

### Areas
```python
POLYAREA_GROUND = 0    # Normal
POLYAREA_WATER = 1     # Swimming
POLYAREA_ROAD = 2      # Preferred
POLYAREA_DOOR = 3      # Doors
POLYAREA_GRASS = 4     # Slower
POLYAREA_JUMP = 5      # Jump zones
POLYAREA_CLIMB = 6     # Climb zones
POLYAREA_DANGER = 7    # Avoid
```

### Flags
```python
POLYFLAGS_WALK = 0x01       # Walk
POLYFLAGS_SWIM = 0x02       # Swim
POLYFLAGS_DOOR = 0x04       # Doors
POLYFLAGS_JUMP = 0x08       # Jump
POLYFLAGS_CLIMB = 0x10      # Climb
POLYFLAGS_DISABLED = 0x20   # Disabled
POLYFLAGS_ALL = 0xFFFF      # All
```

### Crowd Flags
```python
CROWD_ANTICIPATE_TURNS = 1      # Anticipate
CROWD_OBSTACLE_AVOIDANCE = 2    # Avoid obstacles
CROWD_SEPARATION = 4            # Separate from others
CROWD_OPTIMIZE_VIS = 8          # Optimize visibility
CROWD_OPTIMIZE_TOPO = 16        # Optimize topology
```

## Common Patterns

### Different Agent Types
```python
# Infantry (can't swim)
prd.setup_query_filter_infantry(navmesh, 0)
params = prd.create_default_agent_params()
params["queryFilterType"] = 0
params["obstacleAvoidanceType"] = 0  # Aggressive

# Marine (can swim)
prd.setup_query_filter_amphibious(navmesh, 1)
params = prd.create_default_agent_params()
params["queryFilterType"] = 1
params["obstacleAvoidanceType"] = 2  # Defensive
```

### Terrain Setup
```python
# Mark different areas
navmesh.mark_cylinder_area([25,0,25], 10.0, 2.0, prd.POLYAREA_WATER)
navmesh.mark_box_area([0,0,0], [100,1,5], prd.POLYAREA_ROAD)
navmesh.mark_cylinder_area([50,0,50], 5.0, 1.0, prd.POLYAREA_DANGER)

# Add connections
navmesh.add_offmesh_connection([5,2,5], [10,3,10], 0.5, False,
                               prd.POLYAREA_JUMP, prd.POLYFLAGS_JUMP)

navmesh.build_navmesh()
```

### Complete Setup
```python
# 1. Navmesh
navmesh = prd.Navmesh()
navmesh.init_by_obj("level.obj")

# 2. Terrain
navmesh.mark_cylinder_area([25,0,25], 10.0, 2.0, prd.POLYAREA_WATER)

# 3. Connections
navmesh.add_offmesh_connection([5,2,5], [10,3,10], 0.5, False,
                               prd.POLYAREA_JUMP, prd.POLYFLAGS_JUMP)

# 4. Build
navmesh.build_navmesh()

# 5. Crowd
navmesh.init_crowd(100, 1.0)

# 6. Profiles
navmesh.set_obstacle_avoidance_params(0, prd.create_obstacle_avoidance_params("aggressive"))

# 7. Filters
prd.setup_query_filter_infantry(navmesh, 0)

# 8. Agents
params = prd.create_default_agent_params()
params["obstacleAvoidanceType"] = 0
params["queryFilterType"] = 0
agent = navmesh.add_agent([5,0,5], params)

# 9. Simulate
navmesh.set_agent_target(agent, [50,0,50])
navmesh.update_crowd(0.016)
```

## Troubleshooting

**Agent won't use connection?**
→ Check query filter includes required flags

**Path goes through water?**
→ Increase water area cost in query filter

**Agents collide too much?**
→ Increase `separationWeight` or use defensive profile

**Build fails?**
→ Check `navmesh.get_log()` for errors

## File Modifications

### Modified
- `Navmesh.h` - Added 29 method declarations
- `Navmesh.cpp` - Added 627 lines of implementation
- `PyRecastDetour.cpp` - Added 39 PyBind11 bindings
- `__init__.py` - Rewritten with 385 lines

### Created
- `examples/test_convex_volumes.py`
- `examples/test_offmesh_connections.py`
- `examples/test_crowd_advanced.py`
- `examples/test_auto_markup.py`
- `examples/test_complete_example.py`
- `examples/README.md`
- `FEATURES.md`
- `IMPLEMENTATION_SUMMARY.md`
- `QUICK_REFERENCE.md` (this file)

## Links

- Examples: `examples/`
- Full Documentation: `FEATURES.md`
- Implementation Details: `IMPLEMENTATION_SUMMARY.md`
- Recast Navigation: https://github.com/recastnavigation/recastnavigation
