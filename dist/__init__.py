"""
PyRecastDetour - Python bindings for Recast Navigation library

This module provides navmesh generation, pathfinding, crowd simulation,
and advanced navigation features using the Recast Navigation C++ library.

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
    agent_params = {
        "radius": 0.5,
        "height": 2.0,
        "maxSpeed": 3.5,
        "maxAcceleration": 8.0
    }
    agent_id = navmesh.add_agent((5, 0, 5), agent_params)

    # Set target and update
    navmesh.set_agent_target(agent_id, (10, 0, 10))
    navmesh.update_crowd(0.016)  # dt in seconds

    # Get agent state
    pos = navmesh.get_agent_position(agent_id)
    vel = navmesh.get_agent_velocity(agent_id)
"""

import os
from typing import List, Tuple, Dict, Optional, Any

# Import the appropriate compiled module based on Python version
import Py37RecastDetour as rd

# ============================================================================
# CONSTANTS
# ============================================================================

# Crowd update flags
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

# Poly Area Types - for marking different terrain types
POLYAREA_GROUND = 0      # Normal walkable ground
POLYAREA_WATER = 1       # Water (swimming required)
POLYAREA_ROAD = 2        # Roads (preferred path, lower cost)
POLYAREA_DOOR = 3        # Doors (can be opened/closed)
POLYAREA_GRASS = 4       # Grass (slower movement)
POLYAREA_JUMP = 5        # Jump connections
POLYAREA_CLIMB = 6       # Climbable surfaces
POLYAREA_DANGER = 7      # Dangerous areas (high cost)

# Poly Flags - capabilities of each polygon
POLYFLAGS_WALK = 0x01       # Ability to walk (ground travel)
POLYFLAGS_SWIM = 0x02       # Ability to swim (water travel)
POLYFLAGS_DOOR = 0x04       # Ability to move through doors
POLYFLAGS_JUMP = 0x08       # Ability to jump
POLYFLAGS_CLIMB = 0x10      # Ability to climb
POLYFLAGS_DISABLED = 0x20   # Disabled polygon
POLYFLAGS_ALL = 0xFFFF      # All abilities

# Formation types
FORMATION_LINE = 0          # Horizontal line formation
FORMATION_COLUMN = 1        # Vertical column formation
FORMATION_WEDGE = 2         # V-shaped wedge formation
FORMATION_BOX = 3           # Rectangular box/grid formation
FORMATION_CIRCLE = 4        # Circular formation

# ============================================================================
# NAVMESH WRAPPER CLASS
# ============================================================================

class Navmesh:
    """
    Python wrapper for Recast Navigation navmesh with type conversion and validation.

    This class wraps the C++ Navmesh class and provides:
    - Type conversions between Python tuples and C++ vectors
    - Input validation and error messages
    - Pythonic API with type hints
    """

    def __init__(self) -> None:
        """Initialize a new Navmesh instance."""
        self._navmesh = rd.Navmesh()

    # ========================================================================
    # INITIALIZATION & BUILDING
    # ========================================================================

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

    # ========================================================================
    # SETTINGS
    # ========================================================================

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

    # ========================================================================
    # PATHFINDING
    # ========================================================================

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

    # ========================================================================
    # SERIALIZATION
    # ========================================================================

    def save_navmesh(self, file_path: str) -> None:
        '''Save generated navmesh to the bindary firle with extension *.bin

        Input:
            file_path - full path to the file to save
        '''
        self._navmesh.save_navmesh(file_path)

    def load_navmesh(self, file_path: str) -> None:
        """
        Load navmesh from *.bin file

        Input:
            file_path - path to the file with extension *.bin
        """
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

    # ========================================================================
    # MESH EXPORT
    # ========================================================================

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
    # SERIALIZATION - HELPER
    # ========================================================================

    def _generate_plane(self, plane_size: float) -> Tuple[List[float], List[int]]:
        """Internal function, generate geometry data for simple plane"""
        plane_verts: List[float] = [plane_size, 0.0, plane_size,
                                    -plane_size, 0.0, plane_size,
                                    -plane_size, 0.0, -plane_size,
                                    plane_size, 0.0, -plane_size]
        plane_polys: List[int] = [4, 0, 3, 2, 1]
        return (plane_verts, plane_polys)

    # ========================================================================
    # CROWD SIMULATION
    # ========================================================================

    def init_crowd(self, maxAgents: int, maxAgentRadius: float) -> bool:
        """
        Initialize crowd simulation system.

        Args:
            maxAgents: Maximum number of agents
            maxAgentRadius: Maximum agent radius

        Returns:
            True if successful
        """
        return self._navmesh.init_crowd(maxAgents, maxAgentRadius)

    def add_agent(self, pos: Tuple[float, float, float], params: Dict[str, Any]) -> int:
        """
        Add agent to crowd.

        Args:
            pos: Initial position (x, y, z)
            params: Agent parameters dictionary

        Returns:
            Agent index, or -1 on failure
        """
        return self._navmesh.add_agent(list(pos), params)

    def remove_agent(self, idx: int) -> None:
        """Remove agent from crowd."""
        self._navmesh.remove_agent(idx)

    def update_agent_parameters(self, idx: int, params: Dict[str, Any]) -> None:
        """
        Update agent parameters at runtime.

        Args:
            idx: Agent index
            params: Parameters to update
        """
        self._navmesh.update_agent_parameters(idx, params)

    def set_agent_target(self, idx: int, pos: Tuple[float, float, float]) -> bool:
        """
        Set agent's navigation target.

        Args:
            idx: Agent index
            pos: Target position (x, y, z)

        Returns:
            True if successful
        """
        return self._navmesh.set_agent_target(idx, list(pos))

    def set_agent_velocity(self, idx: int, vel: Tuple[float, float, float]) -> None:
        """
        Set agent's velocity directly.

        Args:
            idx: Agent index
            vel: Velocity vector (x, y, z)
        """
        self._navmesh.set_agent_velocity(idx, list(vel))

    def reset_agent_target(self, idx: int) -> None:
        """Clear agent's current target."""
        self._navmesh.reset_agent_target(idx)

    def update_crowd(self, dt: float) -> None:
        """
        Update crowd simulation.

        Args:
            dt: Delta time in seconds
        """
        self._navmesh.update_crowd(dt)

    def get_agent_position(self, idx: int) -> Tuple[float, float, float]:
        """
        Get agent's current position.

        Args:
            idx: Agent index

        Returns:
            Position as (x, y, z)
        """
        pos = self._navmesh.get_agent_position(idx)
        return (pos[0], pos[1], pos[2])

    def get_agent_velocity(self, idx: int) -> Tuple[float, float, float]:
        """
        Get agent's current velocity.

        Args:
            idx: Agent index

        Returns:
            Velocity as (x, y, z)
        """
        vel = self._navmesh.get_agent_velocity(idx)
        return (vel[0], vel[1], vel[2])

    def get_agent_count(self) -> int:
        """Get total number of agents in crowd."""
        return self._navmesh.get_agent_count()

    def get_agent_state(self, idx: int) -> Dict[str, Any]:
        """
        Get complete agent state.

        Args:
            idx: Agent index

        Returns:
            Dictionary with agent state information
        """
        return self._navmesh.get_agent_state(idx)

    # ========================================================================
    # CONVEX VOLUMES (NEW v1.1.0)
    # ========================================================================

    def add_convex_volume(
        self,
        verts: List[float],
        minh: float,
        maxh: float,
        area: int
    ) -> None:
        """
        Add convex volume for area marking.

        Args:
            verts: Flat list of vertices [x1,y1,z1, x2,y2,z2, ...] (3-12 vertices)
            minh: Minimum height
            maxh: Maximum height
            area: Area type (POLYAREA_*)

        Example:
            # Water zone (rectangular)
            verts = [10,0,10, 20,0,10, 20,0,20, 10,0,20]
            navmesh.add_convex_volume(verts, 0.0, 2.0, POLYAREA_WATER)
        """
        self._navmesh.add_convex_volume(verts, minh, maxh, area)

    def delete_convex_volume(self, index: int) -> None:
        """
        Delete convex volume by index.

        Args:
            index: Volume index
        """
        self._navmesh.delete_convex_volume(index)

    def get_convex_volume_count(self) -> int:
        """
        Get number of convex volumes.

        Returns:
            Volume count
        """
        return self._navmesh.get_convex_volume_count()

    def get_convex_volume(self, index: int) -> Dict[str, Any]:
        """
        Get convex volume information.

        Args:
            index: Volume index

        Returns:
            Dictionary with 'verts', 'hmin', 'hmax', 'area'
        """
        return self._navmesh.get_convex_volume(index)

    def get_all_convex_volumes(self) -> List[Dict[str, Any]]:
        """
        Get all convex volumes.

        Returns:
            List of volume dictionaries
        """
        return self._navmesh.get_all_convex_volumes()

    # ========================================================================
    # OFF-MESH CONNECTIONS (NEW v1.1.0)
    # ========================================================================

    def add_offmesh_connection(
        self,
        start_pos: Tuple[float, float, float],
        end_pos: Tuple[float, float, float],
        radius: float,
        bidirectional: bool,
        area: int,
        flags: int
    ) -> None:
        """
        Add off-mesh connection (jump, ladder, teleport, etc).

        Args:
            start_pos: Start position (x, y, z)
            end_pos: End position (x, y, z)
            radius: Connection radius
            bidirectional: True for two-way connections
            area: Area type (POLYAREA_*)
            flags: Capability flags (POLYFLAGS_*)

        Example:
            # Jump connection (one-way)
            navmesh.add_offmesh_connection(
                (5, 2, 5), (10, 3, 10),
                radius=0.5, bidirectional=False,
                area=POLYAREA_JUMP, flags=POLYFLAGS_JUMP
            )
        """
        self._navmesh.add_offmesh_connection(
            list(start_pos), list(end_pos),
            radius, bidirectional, area, flags
        )

    def delete_offmesh_connection(self, index: int) -> None:
        """
        Delete off-mesh connection by index.

        Args:
            index: Connection index
        """
        self._navmesh.delete_offmesh_connection(index)

    def get_offmesh_connection_count(self) -> int:
        """
        Get number of off-mesh connections.

        Returns:
            Connection count
        """
        return self._navmesh.get_offmesh_connection_count()

    def get_offmesh_connection(self, index: int) -> Dict[str, Any]:
        """
        Get off-mesh connection information.

        Args:
            index: Connection index

        Returns:
            Dictionary with connection details
        """
        return self._navmesh.get_offmesh_connection(index)

    def get_all_offmesh_connections(self) -> List[Dict[str, Any]]:
        """
        Get all off-mesh connections.

        Returns:
            List of connection dictionaries
        """
        return self._navmesh.get_all_offmesh_connections()

    # ========================================================================
    # AUTO-MARKUP SYSTEM (NEW v1.1.0)
    # ========================================================================

    def mark_walkable_triangles(self, walkable_slope_angle: float) -> None:
        """
        Mark walkable triangles based on slope angle.

        Args:
            walkable_slope_angle: Maximum walkable slope in degrees
        """
        self._navmesh.mark_walkable_triangles(walkable_slope_angle)

    def mark_box_area(
        self,
        bmin: Tuple[float, float, float],
        bmax: Tuple[float, float, float],
        area_id: int
    ) -> None:
        """
        Mark box-shaped area.

        Args:
            bmin: Minimum bounds (x, y, z)
            bmax: Maximum bounds (x, y, z)
            area_id: Area type (POLYAREA_*)

        Example:
            # Road
            navmesh.mark_box_area((0,0,0), (100,1,5), POLYAREA_ROAD)
        """
        self._navmesh.mark_box_area(list(bmin), list(bmax), area_id)

    def mark_cylinder_area(
        self,
        pos: Tuple[float, float, float],
        radius: float,
        height: float,
        area_id: int
    ) -> None:
        """
        Mark cylindrical area.

        Args:
            pos: Center position (x, y, z)
            radius: Cylinder radius
            height: Cylinder height
            area_id: Area type (POLYAREA_*)

        Example:
            # Water pond
            navmesh.mark_cylinder_area((25,0,25), 10.0, 2.0, POLYAREA_WATER)
        """
        self._navmesh.mark_cylinder_area(list(pos), radius, height, area_id)

    def mark_convex_poly_area(
        self,
        verts: List[float],
        hmin: float,
        hmax: float,
        area_id: int
    ) -> None:
        """
        Mark convex polygon area.

        Args:
            verts: Flat list of vertices [x1,y1,z1, x2,y2,z2, ...]
            hmin: Minimum height
            hmax: Maximum height
            area_id: Area type (POLYAREA_*)
        """
        self._navmesh.mark_convex_poly_area(verts, hmin, hmax, area_id)

    def erode_walkable_area(self, radius: int) -> None:
        """
        Erode walkable area by radius.

        Args:
            radius: Erosion radius in cells
        """
        self._navmesh.erode_walkable_area(radius)

    def median_filter_walkable_area(self) -> None:
        """Apply median filter to walkable area for smoothing."""
        self._navmesh.median_filter_walkable_area()

    # ========================================================================
    # ADVANCED CROWD FEATURES (NEW v1.1.0)
    # ========================================================================

    def set_obstacle_avoidance_params(self, idx: int, params: Dict[str, float]) -> None:
        """
        Set obstacle avoidance parameters for profile.

        Args:
            idx: Profile index (0-7)
            params: Avoidance parameters dictionary

        Example:
            params = create_obstacle_avoidance_params("aggressive")
            navmesh.set_obstacle_avoidance_params(0, params)
        """
        self._navmesh.set_obstacle_avoidance_params(idx, params)

    def get_obstacle_avoidance_params(self, idx: int) -> Dict[str, float]:
        """
        Get obstacle avoidance parameters.

        Args:
            idx: Profile index (0-7)

        Returns:
            Avoidance parameters dictionary
        """
        return self._navmesh.get_obstacle_avoidance_params(idx)

    def set_query_filter_area_cost(self, filter_index: int, area_id: int, cost: float) -> None:
        """
        Set area traversal cost for query filter.

        Args:
            filter_index: Filter index (0-15)
            area_id: Area type (POLYAREA_*)
            cost: Traversal cost multiplier

        Example:
            # Make water expensive for infantry
            navmesh.set_query_filter_area_cost(0, POLYAREA_WATER, 10.0)
        """
        self._navmesh.set_query_filter_area_cost(filter_index, area_id, cost)

    def get_query_filter_area_cost(self, filter_index: int, area_id: int) -> float:
        """
        Get area cost for query filter.

        Args:
            filter_index: Filter index (0-15)
            area_id: Area type (POLYAREA_*)

        Returns:
            Area cost
        """
        return self._navmesh.get_query_filter_area_cost(filter_index, area_id)

    def set_query_filter_include_flags(self, filter_index: int, flags: int) -> None:
        """
        Set required capability flags for query filter.

        Args:
            filter_index: Filter index (0-15)
            flags: Capability flags (POLYFLAGS_*)

        Example:
            # Infantry can walk and jump
            navmesh.set_query_filter_include_flags(0, POLYFLAGS_WALK | POLYFLAGS_JUMP)
        """
        self._navmesh.set_query_filter_include_flags(filter_index, flags)

    def set_query_filter_exclude_flags(self, filter_index: int, flags: int) -> None:
        """
        Set excluded capability flags for query filter.

        Args:
            filter_index: Filter index (0-15)
            flags: Capability flags to exclude (POLYFLAGS_*)
        """
        self._navmesh.set_query_filter_exclude_flags(filter_index, flags)

    def get_agent_neighbors(self, agent_idx: int) -> List[int]:
        """
        Get neighboring agent indices.

        Args:
            agent_idx: Agent index

        Returns:
            List of neighbor agent indices
        """
        return self._navmesh.get_agent_neighbors(agent_idx)

    def get_agent_corners(self, agent_idx: int) -> List[Tuple[float, float, float]]:
        """
        Get path corner points for agent.

        Args:
            agent_idx: Agent index

        Returns:
            List of corner positions [(x,y,z), ...]
        """
        corners_flat = self._navmesh.get_agent_corners(agent_idx)
        if not corners_flat:
            return []
        count = len(corners_flat) // 3
        return [(corners_flat[3*i], corners_flat[3*i+1], corners_flat[3*i+2])
                for i in range(count)]

    def get_active_agents(self) -> List[int]:
        """
        Get all active agent indices.

        Returns:
            List of active agent indices
        """
        return self._navmesh.get_active_agents()

    def get_max_agent_count(self) -> int:
        """
        Get maximum agent count.

        Returns:
            Maximum number of agents
        """
        return self._navmesh.get_max_agent_count()

    def get_query_half_extents(self) -> Tuple[float, float, float]:
        """
        Get query half extents.

        Returns:
            Half extents as (x, y, z)
        """
        extents = self._navmesh.get_query_half_extents()
        return (extents[0], extents[1], extents[2])

    def is_agent_active(self, idx: int) -> bool:
        """
        Check if agent is active.

        Args:
            idx: Agent index

        Returns:
            True if agent is active
        """
        return self._navmesh.is_agent_active(idx)

    def get_agent_parameters(self, idx: int) -> Dict[str, Any]:
        """
        Get agent's current parameters.

        Args:
            idx: Agent index

        Returns:
            Dictionary with agent parameters
        """
        return self._navmesh.get_agent_parameters(idx)

    # ========================================================================
    # FORMATIONS & GROUP BEHAVIORS (NEW v1.1.0)
    # ========================================================================

    def create_formation(self, formation_type: int, spacing: float) -> int:
        """
        Create a new formation group.

        Args:
            formation_type: Formation type:
                0 = Line (agents in a horizontal line)
                1 = Column (agents in a vertical column)
                2 = Wedge (V-shaped formation)
                3 = Box (rectangular grid)
                4 = Circle (circular arrangement)
            spacing: Distance between agents in meters

        Returns:
            Formation ID, or -1 on failure

        Example:
            # Create line formation with 2m spacing
            formation_id = navmesh.create_formation(0, 2.0)
        """
        return self._navmesh.create_formation(formation_type, spacing)

    def delete_formation(self, formation_id: int) -> None:
        """
        Delete a formation group.

        Args:
            formation_id: Formation ID
        """
        self._navmesh.delete_formation(formation_id)

    def add_agent_to_formation(self, formation_id: int, agent_idx: int) -> bool:
        """
        Add an agent to a formation.

        Args:
            formation_id: Formation ID
            agent_idx: Agent index

        Returns:
            True if successful

        Example:
            formation_id = navmesh.create_formation(0, 2.0)
            agent_id = navmesh.add_agent((10, 0, 10), params)
            navmesh.add_agent_to_formation(formation_id, agent_id)
        """
        return self._navmesh.add_agent_to_formation(formation_id, agent_idx)

    def remove_agent_from_formation(self, agent_idx: int) -> bool:
        """
        Remove an agent from its formation.

        Args:
            agent_idx: Agent index

        Returns:
            True if agent was in a formation and removed
        """
        return self._navmesh.remove_agent_from_formation(agent_idx)

    def set_formation_target(
        self,
        formation_id: int,
        target_pos: Tuple[float, float, float],
        target_dir: Tuple[float, float, float]
    ) -> None:
        """
        Set target position and direction for formation.

        Args:
            formation_id: Formation ID
            target_pos: Target position (x, y, z)
            target_dir: Target facing direction (x, y, z) - will be normalized

        Example:
            # Move formation to (50, 0, 50) facing north
            navmesh.set_formation_target(formation_id, (50, 0, 50), (0, 0, 1))
        """
        self._navmesh.set_formation_target(
            formation_id,
            list(target_pos),
            list(target_dir)
        )

    def set_formation_leader(self, formation_id: int, agent_idx: int) -> None:
        """
        Set the leader of a formation.

        Args:
            formation_id: Formation ID
            agent_idx: Agent index (must be in formation)

        Note:
            The leader's position can be used for formation calculations.
        """
        self._navmesh.set_formation_leader(formation_id, agent_idx)

    def get_formation_agents(self, formation_id: int) -> List[int]:
        """
        Get list of agent indices in a formation.

        Args:
            formation_id: Formation ID

        Returns:
            List of agent indices
        """
        return self._navmesh.get_formation_agents(formation_id)

    def get_formation_info(self, formation_id: int) -> Dict[str, float]:
        """
        Get information about a formation.

        Args:
            formation_id: Formation ID

        Returns:
            Dictionary with formation info:
                - id: Formation ID
                - type: Formation type (0-4)
                - spacing: Agent spacing
                - leader_idx: Leader agent index (-1 if none)
                - agent_count: Number of agents
                - has_target: Whether formation has a target (0 or 1)
                - target_x, target_y, target_z: Target position
                - dir_x, dir_y, dir_z: Target direction
        """
        return self._navmesh.get_formation_info(formation_id)

    def update_formations(self, dt: float) -> None:
        """
        Update all formations and set agent targets.

        Args:
            dt: Delta time in seconds

        Note:
            Call this each frame to update formation positions.
            This automatically sets targets for all agents in formations.

        Example:
            # In game loop
            navmesh.update_crowd(dt)
            navmesh.update_formations(dt)
        """
        self._navmesh.update_formations(dt)

    def get_formation_count(self) -> int:
        """
        Get total number of formations.

        Returns:
            Formation count
        """
        return self._navmesh.get_formation_count()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_default_agent_params() -> Dict[str, Any]:
    """
    Create a dictionary with default agent parameters for crowd simulation.

    Returns:
        dict: Default agent parameters

    Example:
        params = create_default_agent_params()
        params["maxSpeed"] = 5.0  # Override specific values
        agent_id = navmesh.add_agent((0, 0, 0), params)
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


def create_vehicle_params() -> Dict[str, Any]:
    """
    Create a dictionary with default vehicle parameters.
    Vehicle agents have larger radius, higher speeds, and different movement characteristics.

    Returns:
        dict: Default vehicle parameters

    Example:
        vehicle_params = create_vehicle_params()
        vehicle_id = navmesh.add_agent((10, 0, 10), vehicle_params)
    """
    return {
        "radius": 2.5,
        "height": 2.0,
        "maxSpeed": 15.0,
        "maxAcceleration": 3.0,
        "collisionQueryRange": 30.0,
        "pathOptimizationRange": 75.0,
        "separationWeight": 3.0,
        "updateFlags": CROWD_ANTICIPATE_TURNS | CROWD_OBSTACLE_AVOIDANCE
    }


def create_obstacle_avoidance_params(profile: str = "default") -> Dict[str, float]:
    """
    Create obstacle avoidance parameters for different behavior profiles.

    Args:
        profile: One of "default", "aggressive", "passive", "defensive"

    Returns:
        dict: Obstacle avoidance parameters

    Profiles:
        - default: Balanced behavior
        - aggressive: More direct pathfinding, less cautious
        - passive: More cautious, avoids other agents more
        - defensive: Very cautious, maintains large distances

    Example:
        # Set up aggressive avoidance for soldiers
        navmesh.set_obstacle_avoidance_params(0, create_obstacle_avoidance_params("aggressive"))

        # Agent uses profile 0
        agent_params = create_default_agent_params()
        agent_params["obstacleAvoidanceType"] = 0
        soldier_id = navmesh.add_agent((5, 0, 5), agent_params)
    """
    profiles = {
        "default": {
            "velBias": 0.4,
            "weightDesVel": 2.0,
            "weightCurVel": 0.75,
            "weightSide": 0.75,
            "weightToi": 2.5,
            "horizTime": 2.5,
            "gridSize": 33,
            "adaptiveDivs": 7,
            "adaptiveRings": 2,
            "adaptiveDepth": 5
        },
        "aggressive": {
            "velBias": 0.5,
            "weightDesVel": 2.5,
            "weightCurVel": 1.0,
            "weightSide": 0.5,
            "weightToi": 3.0,
            "horizTime": 2.0,
            "gridSize": 33,
            "adaptiveDivs": 7,
            "adaptiveRings": 3,
            "adaptiveDepth": 6
        },
        "passive": {
            "velBias": 0.3,
            "weightDesVel": 1.0,
            "weightCurVel": 0.5,
            "weightSide": 1.0,
            "weightToi": 1.5,
            "horizTime": 3.5,
            "gridSize": 20,
            "adaptiveDivs": 5,
            "adaptiveRings": 2,
            "adaptiveDepth": 3
        },
        "defensive": {
            "velBias": 0.2,
            "weightDesVel": 1.0,
            "weightCurVel": 0.3,
            "weightSide": 1.5,
            "weightToi": 1.0,
            "horizTime": 4.0,
            "gridSize": 25,
            "adaptiveDivs": 6,
            "adaptiveRings": 2,
            "adaptiveDepth": 4
        }
    }

    return profiles.get(profile, profiles["default"])


def setup_query_filter_infantry(navmesh: Navmesh, filter_index: int = 0) -> None:
    """
    Configure a query filter for infantry units (can walk, cannot swim).

    Args:
        navmesh: Navmesh instance
        filter_index: Filter index to configure (0-15)

    Example:
        setup_query_filter_infantry(navmesh, 0)

        agent_params = create_default_agent_params()
        agent_params["queryFilterType"] = 0
        infantry_id = navmesh.add_agent((5, 0, 5), agent_params)
    """
    navmesh.set_query_filter_area_cost(filter_index, POLYAREA_GROUND, 1.0)
    navmesh.set_query_filter_area_cost(filter_index, POLYAREA_ROAD, 0.5)    # Prefer roads
    navmesh.set_query_filter_area_cost(filter_index, POLYAREA_GRASS, 1.5)   # Grass slows down
    navmesh.set_query_filter_area_cost(filter_index, POLYAREA_WATER, 10.0)  # Avoid water
    navmesh.set_query_filter_area_cost(filter_index, POLYAREA_DANGER, 5.0)  # Avoid danger
    navmesh.set_query_filter_include_flags(filter_index, POLYFLAGS_WALK | POLYFLAGS_JUMP | POLYFLAGS_DOOR)
    navmesh.set_query_filter_exclude_flags(filter_index, POLYFLAGS_SWIM | POLYFLAGS_DISABLED)


def setup_query_filter_amphibious(navmesh: Navmesh, filter_index: int = 1) -> None:
    """
    Configure a query filter for amphibious units (can walk and swim).

    Args:
        navmesh: Navmesh instance
        filter_index: Filter index to configure (0-15)

    Example:
        setup_query_filter_amphibious(navmesh, 1)

        agent_params = create_default_agent_params()
        agent_params["queryFilterType"] = 1
        amphibious_id = navmesh.add_agent((5, 0, 5), agent_params)
    """
    navmesh.set_query_filter_area_cost(filter_index, POLYAREA_GROUND, 1.0)
    navmesh.set_query_filter_area_cost(filter_index, POLYAREA_ROAD, 0.8)
    navmesh.set_query_filter_area_cost(filter_index, POLYAREA_WATER, 0.7)   # Prefer water
    navmesh.set_query_filter_area_cost(filter_index, POLYAREA_DANGER, 5.0)
    navmesh.set_query_filter_include_flags(filter_index, POLYFLAGS_WALK | POLYFLAGS_SWIM | POLYFLAGS_JUMP)
    navmesh.set_query_filter_exclude_flags(filter_index, POLYFLAGS_DISABLED)


def setup_query_filter_flying(navmesh: Navmesh, filter_index: int = 2) -> None:
    """
    Configure a query filter for flying units (ignores terrain type).

    Args:
        navmesh: Navmesh instance
        filter_index: Filter index to configure (0-15)

    Example:
        setup_query_filter_flying(navmesh, 2)

        agent_params = create_default_agent_params()
        agent_params["queryFilterType"] = 2
        flying_id = navmesh.add_agent((5, 5, 5), agent_params)
    """
    # All areas have same cost for flying units
    for area in range(8):
        navmesh.set_query_filter_area_cost(filter_index, area, 1.0)
    navmesh.set_query_filter_include_flags(filter_index, POLYFLAGS_ALL)
    navmesh.set_query_filter_exclude_flags(filter_index, POLYFLAGS_DISABLED)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Core class
    'Navmesh',

    # Helper functions
    'create_default_agent_params',
    'create_vehicle_params',
    'create_obstacle_avoidance_params',
    'setup_query_filter_infantry',
    'setup_query_filter_amphibious',
    'setup_query_filter_flying',

    # Crowd constants
    'CROWD_ANTICIPATE_TURNS',
    'CROWD_OBSTACLE_AVOIDANCE',
    'CROWD_SEPARATION',
    'CROWD_OPTIMIZE_VIS',
    'CROWD_OPTIMIZE_TOPO',

    # Agent states
    'CROWDAGENT_STATE_INVALID',
    'CROWDAGENT_STATE_WALKING',
    'CROWDAGENT_STATE_OFFMESH',

    # Target states
    'CROWDAGENT_TARGET_NONE',
    'CROWDAGENT_TARGET_FAILED',
    'CROWDAGENT_TARGET_VALID',
    'CROWDAGENT_TARGET_REQUESTING',
    'CROWDAGENT_TARGET_WAITING_FOR_QUEUE',
    'CROWDAGENT_TARGET_WAITING_FOR_PATH',
    'CROWDAGENT_TARGET_VELOCITY',

    # Partition types
    'PARTITION_WATERSHED',
    'PARTITION_MONOTONE',
    'PARTITION_LAYERS',

    # Area types
    'POLYAREA_GROUND',
    'POLYAREA_WATER',
    'POLYAREA_ROAD',
    'POLYAREA_DOOR',
    'POLYAREA_GRASS',
    'POLYAREA_JUMP',
    'POLYAREA_CLIMB',
    'POLYAREA_DANGER',

    # Poly flags
    'POLYFLAGS_WALK',
    'POLYFLAGS_SWIM',
    'POLYFLAGS_DOOR',
    'POLYFLAGS_JUMP',
    'POLYFLAGS_CLIMB',
    'POLYFLAGS_DISABLED',
    'POLYFLAGS_ALL',

    # Formation types
    'FORMATION_LINE',
    'FORMATION_COLUMN',
    'FORMATION_WEDGE',
    'FORMATION_BOX',
    'FORMATION_CIRCLE',
]

__version__ = "1.1.0"
