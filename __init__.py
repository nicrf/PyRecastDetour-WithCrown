"""
PyRecastDetour - Python bindings for Recast Navigation library

This module provides navmesh generation, pathfinding, and crowd simulation
capabilities using the Recast Navigation C++ library.

Example usage:
    from PyRecastDetour import Navmesh

    # Create and build navmesh
    navmesh = Navmesh()
    navmesh.init_by_obj("level.obj")
    navmesh.build_navmesh()

    # Find path
    path = navmesh.pathfind_straight([0, 0, 0], [10, 0, 10])

    # Initialize crowd simulation
    navmesh.init_crowd(maxAgents=100, maxAgentRadius=1.0)

    # Add agents
    agent_params = {
        "radius": 0.5,
        "height": 2.0,
        "maxSpeed": 3.5,
        "maxAcceleration": 8.0
    }
    agent_id = navmesh.add_agent([5, 0, 5], agent_params)

    # Set target and update
    navmesh.set_agent_target(agent_id, [10, 0, 10])
    navmesh.update_crowd(0.016)  # dt in seconds

    # Get agent state
    pos = navmesh.get_agent_position(agent_id)
    vel = navmesh.get_agent_velocity(agent_id)
"""

import sys

# Import the appropriate compiled module based on Python version
if sys.version_info.major == 2:
    from Py2RecastDetour import *
elif sys.version_info.major == 3:
    if sys.version_info.minor == 6:
        from Py36RecastDetour import *
    elif sys.version_info.minor == 7:
        from Py37RecastDetour import *
    elif sys.version_info.minor == 8:
        from Py38RecastDetour import *
    elif sys.version_info.minor == 9:
        from Py39RecastDetour import *
    else:
        # Python 3.10+
        from Py310RecastDetour import *
else:
    raise ImportError(f"Unsupported Python version: {sys.version_info.major}.{sys.version_info.minor}")

# Crowd update flags constants
CROWD_ANTICIPATE_TURNS = 1
CROWD_OBSTACLE_AVOIDANCE = 2
CROWD_SEPARATION = 4
CROWD_OPTIMIZE_VIS = 8
CROWD_OPTIMIZE_TOPO = 16

# Crowd agent states
CROWDAGENT_STATE_INVALID = 0
CROWDAGENT_STATE_WALKING = 1
CROWDAGENT_STATE_OFFMESH = 2

# Move request states
CROWDAGENT_TARGET_NONE = 0
CROWDAGENT_TARGET_FAILED = 1
CROWDAGENT_TARGET_VALID = 2
CROWDAGENT_TARGET_REQUESTING = 3
CROWDAGENT_TARGET_WAITING_FOR_QUEUE = 4
CROWDAGENT_TARGET_WAITING_FOR_PATH = 5
CROWDAGENT_TARGET_VELOCITY = 6

# Partition types
PARTITION_WATERSHED = 0
PARTITION_MONOTONE = 1
PARTITION_LAYERS = 2

def create_default_agent_params():
    """
    Create a dictionary with default agent parameters.

    Returns:
        dict: Default agent parameters for crowd simulation
    """
    return {
        "radius": 0.6,
        "height": 2.0,
        "maxAcceleration": 8.0,
        "maxSpeed": 3.5,
        "collisionQueryRange": 7.2,  # radius * 12
        "pathOptimizationRange": 18.0,  # radius * 30
        "separationWeight": 2.0,
        "updateFlags": CROWD_ANTICIPATE_TURNS | CROWD_OPTIMIZE_VIS | CROWD_OPTIMIZE_TOPO | CROWD_OBSTACLE_AVOIDANCE,
        "obstacleAvoidanceType": 3,
        "queryFilterType": 0
    }

__all__ = [
    'Navmesh',
    'create_default_agent_params',
    'CROWD_ANTICIPATE_TURNS',
    'CROWD_OBSTACLE_AVOIDANCE',
    'CROWD_SEPARATION',
    'CROWD_OPTIMIZE_VIS',
    'CROWD_OPTIMIZE_TOPO',
    'CROWDAGENT_STATE_INVALID',
    'CROWDAGENT_STATE_WALKING',
    'CROWDAGENT_STATE_OFFMESH',
    'CROWDAGENT_TARGET_NONE',
    'CROWDAGENT_TARGET_FAILED',
    'CROWDAGENT_TARGET_VALID',
    'CROWDAGENT_TARGET_REQUESTING',
    'CROWDAGENT_TARGET_WAITING_FOR_QUEUE',
    'CROWDAGENT_TARGET_WAITING_FOR_PATH',
    'CROWDAGENT_TARGET_VELOCITY',
    'PARTITION_WATERSHED',
    'PARTITION_MONOTONE',
    'PARTITION_LAYERS'
]
