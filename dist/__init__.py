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
    path = navmesh.pathfind_straight((0, 0, 0), (10, 0, 10))

    # Initialize crowd simulation
    navmesh.init_crowd(maxAgents=100, maxAgentRadius=1.0)

    # Add agents
    agent_params = create_default_agent_params()
    agent_id = navmesh.add_agent((5, 0, 5), agent_params)

    # Set target and update
    navmesh.set_agent_target(agent_id, (10, 0, 10))
    navmesh.update_crowd(0.016)  # dt in seconds

    # Get agent state
    pos = navmesh.get_agent_position(agent_id)
    vel = navmesh.get_agent_velocity(agent_id)
"""

import sys
import os
from typing import List, Tuple, Optional, Dict, Any

if sys.version_info[0] == 2:
    import Py2RecastDetour as rd
else:
    if sys.version_info[1] == 6:
        from . import Py36RecastDetour as rd
    elif sys.version_info[1] == 7:
        from . import Py37RecastDetour as rd
    elif sys.version_info[1] == 8:
        from . import Py38RecastDetour as rd
    elif sys.version_info[1] == 9:
        from . import Py39RecastDetour as rd
    else:
        from . import Py310RecastDetour as rd  # type: ignore


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


def create_default_agent_params() -> Dict[str, Any]:
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


class Navmesh():
    def __init__(self) -> None:
        self._navmesh = rd.Navmesh()

    def init_by_obj(self, file_path: str) -> None:
        '''Initialize geomery by reading *.obj file

        Input:
            file_path - path to the file with extension *.obj
        '''
        if os.path.exists(file_path):
            extension: str = os.path.splitext(file_path)[1]
            if extension == ".obj":
                self._navmesh.init_by_obj(file_path)
            else:
                print("Fail init geometry. Only *.obj files are supported")
        else:
            print("Fail init geometry. File " + file_path + " does not exist")

    def init_by_raw(self, vertices: List[float], faces: List[int]) -> None:
        '''Initialize geometry by raw data. This data contains vertex positions and vertex indexes of polygons.

        Input:
            vertices - list of floats of the length 3x(the number of vertices) in the form [x1, y1, z1, x2, y2, z2, ...], where
                xi, yi, zi - coordinates of the i-th vertex
            faces - list of integers in the form [n1, i1, i2, ..., in1, n2, i1, i2, ..., in2, ...],
                where n1, n2, ... - the number of edges in each polygon, i1, i2, ... - indexes of polygon corners
                orientation of polygons should be in clock-wise direction

        Example: the simple plane has the following data
            [1.0, 0.0, 1.0, -1.0, 0.0, 1.0, -1.0, 0.0, -1.0, 1.0, 0.0, -1.0], [4, 0, 3, 2, 1]
        '''
        if len(vertices) % 3 == 0:
            self._navmesh.init_by_raw(vertices, faces)
        else:
            print("Fail init geometry from raw data. The number of vertices coordinates should be 3*k")

    def build_navmesh(self) -> None:
        '''Generate navmesh data. Before this method the geometry should be inited.
        '''
        self._navmesh.build_navmesh()

    def get_log(self) -> str:
        '''Return the string with inetrnal log messages.

        Output:
            string with log messages
        '''
        return self._navmesh.get_log()

    def pathfind_straight(self, start: Tuple[float, float, float], end: Tuple[float, float, float], vertex_mode: int = 0) -> Optional[List[Tuple[float, float, float]]]:
        '''Return the shortest path between start and end point inside generated navmesh.

        Input:
            start - triple of floats in the form [x, y, z]
            end - triple of floats in the form [x, y, z]
            vertex_mode - define how the result path is formed
                if vertex_mode = 0 then points adden only in path corners,
                if vertex_mode = 1 then a vertex at every polygon edge crossing where area changes is added
                if vertex_mode = 2 then vertex at every polygon edge crossing is added

        Output:
            list in the from [(x1, y1, z1), ... (xn, yn, zn)] with sequences of path points
        '''
        if len(start) == 3 and len(end) == 3:
            coordinates: List[float] = self._navmesh.pathfind_straight(start, end, vertex_mode)
            points_count = len(coordinates) // 3
            return [(coordinates[3*i], coordinates[3*i + 1], coordinates[3*i + 2]) for i in range(points_count)]
        else:
            print("Fail to find straight path. Points should be triples")
            return None

    def pathfind_straight_batch(self, coordinates: List[float], vertex_mode: int = 0) -> Optional[List[List[Tuple[float, float, float]]]]:
        '''Find path between multiple input points.

        Input:
            coordinates - list of floats in the form [s1_x, s1_y, s1_z, e1_x, e1_y, e1_z, s2_x, s2_y, s2_z, e2_x, e2_y, e2_z, ...], where
                si_* are coordinates of the i-th start point, ei_* are coordinates of the i-th end point.
                The number of float values in the list should be x6.
            vertex_mode - define how the result path is formed
                if vertex_mode = 0 then points adden only in path corners,
                if vertex_mode = 1 then a vertex at every polygon edge crossing where area changes is added
                if vertex_mode = 2 then vertex at every polygon edge crossing is added

        Output:
            One list in the form [[(p1_x1, p1_y1, p1_z1), ...], [(p2_x1, p2_y1, p2_z1), ...]], where each item in the list is a list
                with 3-tuples of path coordinates. The number of ites is the same as the number of input pairs (len(coordinates) // 6)
        '''
        batch_size: int = len(coordinates) // 6
        if len(coordinates) % 6 == 0:
            output: List[float] = self._navmesh.pathfind_straight_batch(coordinates, vertex_mode)
            result_array: List[List[Tuple[float, float, float]]] = []
            index: int = 0
            for step in range(batch_size):
                step_size = int(output[index])  # the number of points in the path
                step_array: List[Tuple[float, float, float]] = []
                index += 1
                for p_index in range(step_size):
                    step_array.append((output[index], output[index + 1], output[index + 2]))
                    index += 3
                result_array.append(step_array)
            return result_array
        else:
            print("Fail to find straight path for several points. The number of input coorsinates should be divisible by 6")
            return None

    def distance_to_wall(self, point: Tuple[float, float, float]) -> Optional[float]:
        '''Return the minimal distance between input point and navmesh edge

        Input:
            point - triple of floats in the form [x, y, z]

        Output:
            minimal distance as float number
        '''
        if len(point) == 3:
            return self._navmesh.distance_to_wall(point)
        else:
            print("Fail calculate distance to wall. The point should be triple")
            return None

    def raycast(self, start: Tuple[float, float, float], end: Tuple[float, float, float]) -> Optional[List[Tuple[float, float, float]]]:
        '''Return the segment of the line between start point and navmesh edge (or end point, if there are no collisions with navmesh edges)

        Input:
            start - triple of floats in the form [x, y, z]
            end - triple of floats in the form [x, y, z]

        Output:
            the pair [(x1, y1, z1), (x2, y2, z2)], where (x1, y1, z1) - coordinates of the start point, (x2, y2, z2) - coordinates of the finish point
        '''
        if len(start) == 3 and len(end) == 3:
            c = self._navmesh.raycast(start, end)
            if len(c) > 0:
                return [(c[0], c[1], c[2]), (c[3], c[4], c[5])]
            else:
                return None  # if calculations are fail
        else:
            print("Fails to raycast. Start and end should be triples")
            return None

    def hit_mesh(self, start: Tuple[float, float, float], end: Tuple[float, float, float]) -> Optional[Tuple[float, float, float]]:
        '''Return coordinates of the intersection point of the ray from start to end and geometry polygons

        Input:
            start - triple of floats in the form [x, y, z]
            end - triple of floats in the form [x, y, z]

        Output:
            the tuple (x, y, z) with coordinates of the intersection point
                if there are no intersections, then return coordinates of the end point
        '''
        if len(start) == 3 and len(end) == 3:
            c = self._navmesh.hit_mesh(start, end)
            if len(c) == 3:
                return (c[0], c[1], c[2])
            else:
                return None  # if calculations are fail
        else:
            print("Fails to hit mesh. Start and end should be triples")
            return None

    def get_settings(self) -> Dict[str, Any]:
        '''Return current setting, which will be used for building navmesh

        Output:
            dictionary with the following keys:
                cellSize - cell size in world units
                cellHeight - cell height in world units
                agentHeight - agent height in world units
                agentRadius - agent radius in world units
                agentMaxClimb - agent max climb in world units
                agentMaxSlope - agent max slope in degrees
                regionMinSize - region minimum size in voxels
                regionMergeSize - region merge size in voxels
                edgeMaxLen - eEdge max length in world units
                edgeMaxError - edge max error in voxels
                vertsPerPoly - the maximum number of vertices in each polygon
                detailSampleDist - detail sample distance in voxels
                detailSampleMaxError - detail sample max error in voxel heights
        '''
        return self._navmesh.get_settings()

    def set_settings(self, settings: Dict[str, Any]) -> None:
        '''Set settings for building navmesh

        Input:
            settings - dictionary with the following keys:
                cellSize - cell size in world units, should be >= 0.0001
                cellHeight - cell height in world units, should be >= 0.0001
                agentHeight - agent height in world units, should be >= 0.0
                agentRadius - agent radius in world units, should be >= 0.0
                agentMaxClimb - agent max climb in world units
                agentMaxSlope - agent max slope in degrees
                regionMinSize - region minimum size in voxels
                regionMergeSize - region merge size in voxels
                edgeMaxLen - eEdge max length in world units
                edgeMaxError - edge max error in voxels
                vertsPerPoly - the maximum number of vertices in each polygon, should be integer from 3 to 6
                detailSampleDist - detail sample distance in voxels
                detailSampleMaxError - detail sample max error in voxel heights
        '''
        self._navmesh.set_settings(settings)

    def get_partition_type(self) -> int:
        '''Retrun the index of the partition type, which used for generating polygons in the navmesh

        Output:
            one integer from 0 to 2
                0 - SAMPLE_PARTITION_WATERSHED
                1 - SAMPLE_PARTITION_MONOTONE
                2 - SAMPLE_PARTITION_LAYERS
        '''
        return self._navmesh.get_partition_type()

    def set_partition_type(self, type: int) -> None:
        '''Set partition type for generation navmesh

        Input:
            type - integer from 0 to 2
                0 - SAMPLE_PARTITION_WATERSHED
                1 - SAMPLE_PARTITION_MONOTONE
                2 - SAMPLE_PARTITION_LAYERS
        '''
        self._navmesh.set_partition_type(type)

    def get_bounding_box(self) -> Optional[Tuple[Tuple[float, float, float], Tuple[float, float, float]]]:
        '''Return bounding box of the mesh

        Output:
            tuple in the form (b_min, b_max), where
                b_min is a triple (x, y, z) with the lowerest corner of the bounding box
                b_max is a triple (x, y, z) with the highest corner of the bounding box
        '''
        b = self._navmesh.get_bounding_box()
        if len(b) == 6:
            return ((b[0], b[1], b[2]), (b[3], b[4], b[5]))
        else:
            return None

    def save_navmesh(self, file_path: str) -> None:
        '''Save generated navmesh to the bindary firle with extension *.bin

        Input:
            file_path - full path to the file to save
        '''
        self._navmesh.save_navmesh(file_path)

    def _generate_plane(self, plane_size: float) -> Tuple[List[float], List[int]]:
        '''Internal function, generate geometry data for simple plane
        '''
        plane_verts: List[float] = [plane_size, 0.0, plane_size,
                                    -plane_size, 0.0, plane_size,
                                    -plane_size, 0.0, -plane_size,
                                    plane_size, 0.0, -plane_size]
        plane_polys: List[int] = [4, 0, 3, 2, 1]
        return (plane_verts, plane_polys)

    def load_navmesh(self, file_path: str) -> None:
        '''Load navmesh from *.bin file

        Input:
            file_path - path to the file with extension *.bin
        '''
        if os.path.exists(file_path):
            # clear generated navmesh and load simple plane
            # by default we will use the size 4.0
            self.init_by_raw(*self._generate_plane(4.0))
            settings: Dict[str, Any] = self.get_settings()
            cell_size: float = settings["cellSize"]
            if 4.0 / cell_size < 20.0:
                # regenerate the plane
                plane_size: float = cell_size * 20.0  # assume that the plane contains 20 tiles in each direction
                self.init_by_raw(*self._generate_plane(plane_size))
            # build this simple navmesh
            self.build_navmesh()
            self._navmesh.load_navmesh(file_path)
        else:
            print("Fails to load navmesh. The file " + file_path + " does not exist")

    def get_navmesh_trianglulation(self) -> Tuple[List[float], List[int]]:
        '''Return triangulation data of the generated navmesh

        Output:
            the tuple (vertices, triangles), where
                vertices is a list [x1, y1, z1, x2, y2, z2, ...] with coordinates of the navmesh vertices
                triangles is a list [t11, t12, t13, t21, t22, t23, t31, t32, t33, t41, t42, t43, ...], where ti1, ti2 and ti3 are vertex indexes of the i-th triangle
        '''
        return self._navmesh.get_navmesh_trianglulation()

    def get_navmesh_poligonization(self) -> Tuple[List[float], List[int], List[int]]:
        '''Return polygon description of the navigation mesh

        Output:
            the tuple (vertices, polygons, sizes), where
                vertices is a list [x1, y1, z1, x2, y2, z2, ...] with coordinates of the navmesh vertices
                polygons is a list [p11, p12, p13, ..., p1n1, p21, p22, p23, ..., p2n2, ...], where pij is the j-th vertex index of the polygon pi
                sizes is a list [n1, n2, ...], where ni is a size of the i-th polygon
        '''
        return self._navmesh.get_navmesh_polygonization()

    # ========================================================================
    # Crowd and Agent Management Methods
    # ========================================================================

    def init_crowd(self, maxAgents: int, maxAgentRadius: float) -> bool:
        '''Initialize the crowd simulation system.

        Input:
            maxAgents - maximum number of agents that can be managed
            maxAgentRadius - maximum radius of any agent in the crowd

        Output:
            True if initialization successful, False otherwise
        '''
        return self._navmesh.init_crowd(maxAgents, maxAgentRadius)

    def add_agent(self, pos: Tuple[float, float, float], params: Dict[str, Any]) -> int:
        '''Add an agent to the crowd.

        Input:
            pos - initial position as tuple (x, y, z)
            params - dictionary with agent parameters:
                radius - agent radius
                height - agent height
                maxAcceleration - maximum acceleration
                maxSpeed - maximum speed
                collisionQueryRange - collision detection range
                pathOptimizationRange - path optimization range
                separationWeight - separation weight for crowd separation
                updateFlags - behavior flags (use CROWD_* constants)
                obstacleAvoidanceType - obstacle avoidance quality [0-3]
                queryFilterType - navigation query filter type

        Output:
            agent ID (integer >= 0) if successful, -1 if failed
        '''
        if len(pos) != 3:
            print("Fail to add agent. Position should be a triple (x, y, z)")
            return -1
        return self._navmesh.add_agent(list(pos), params)

    def remove_agent(self, idx: int) -> None:
        '''Remove an agent from the crowd.

        Input:
            idx - agent ID returned by add_agent()
        '''
        self._navmesh.remove_agent(idx)

    def update_crowd(self, dt: float) -> None:
        '''Update the crowd simulation.

        Input:
            dt - time step in seconds (e.g., 0.016 for 60 FPS)
        '''
        self._navmesh.update_crowd(dt)

    def set_agent_target(self, idx: int, pos: Tuple[float, float, float]) -> bool:
        '''Set movement target for an agent.

        Input:
            idx - agent ID
            pos - target position as tuple (x, y, z)

        Output:
            True if successful, False otherwise
        '''
        if len(pos) != 3:
            print("Fail to set agent target. Position should be a triple (x, y, z)")
            return False
        return self._navmesh.set_agent_target(idx, list(pos))

    def set_agent_velocity(self, idx: int, vel: Tuple[float, float, float]) -> bool:
        '''Set velocity for an agent (manual control).

        Input:
            idx - agent ID
            vel - velocity as tuple (vx, vy, vz)

        Output:
            True if successful, False otherwise
        '''
        if len(vel) != 3:
            print("Fail to set agent velocity. Velocity should be a triple (vx, vy, vz)")
            return False
        return self._navmesh.set_agent_velocity(idx, list(vel))

    def reset_agent_target(self, idx: int) -> bool:
        '''Reset/cancel the movement target for an agent.

        Input:
            idx - agent ID

        Output:
            True if successful, False otherwise
        '''
        return self._navmesh.reset_agent_target(idx)

    def get_agent_position(self, idx: int) -> Optional[Tuple[float, float, float]]:
        '''Get current position of an agent.

        Input:
            idx - agent ID

        Output:
            position as tuple (x, y, z) or None if failed
        '''
        pos = self._navmesh.get_agent_position(idx)
        if len(pos) == 3:
            return (pos[0], pos[1], pos[2])
        return None

    def get_agent_velocity(self, idx: int) -> Optional[Tuple[float, float, float]]:
        '''Get current velocity of an agent.

        Input:
            idx - agent ID

        Output:
            velocity as tuple (vx, vy, vz) or None if failed
        '''
        vel = self._navmesh.get_agent_velocity(idx)
        if len(vel) == 3:
            return (vel[0], vel[1], vel[2])
        return None

    def get_agent_state(self, idx: int) -> Optional[Dict[str, float]]:
        '''Get complete state information for an agent.

        Input:
            idx - agent ID

        Output:
            dictionary with agent state information:
                active - 1.0 if agent is active, 0.0 otherwise
                state - agent state (use CROWDAGENT_STATE_* constants)
                targetState - target request state (use CROWDAGENT_TARGET_* constants)
                position_x, position_y, position_z - current position
                velocity_x, velocity_y, velocity_z - current velocity
                desiredVelocity_x, desiredVelocity_y, desiredVelocity_z - desired velocity
                cornerVerts_x, cornerVerts_y, cornerVerts_z - next corner position
                ncorners - number of corners in current path
                ... and other internal state values
            Returns None if agent not found
        '''
        return self._navmesh.get_agent_state(idx)

    def get_agent_count(self) -> int:
        '''Get the current number of active agents in the crowd.

        Output:
            number of active agents
        '''
        return self._navmesh.get_agent_count()

    def update_agent_parameters(self, idx: int, params: Dict[str, Any]) -> None:
        '''Update parameters of an existing agent.

        Input:
            idx - agent ID
            params - dictionary with agent parameters to update (same as add_agent)
        '''
        self._navmesh.update_agent_parameters(idx, params)


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
