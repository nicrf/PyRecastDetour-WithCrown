#include "Navmesh.h"

#ifndef _MAIN_APP
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#ifdef _Python2
PYBIND11_MODULE(Py2RecastDetour, m)
#else
#ifdef _Python36
PYBIND11_MODULE(Py36RecastDetour, m)
#else
#ifdef _Python37
PYBIND11_MODULE(Py37RecastDetour, m)
#else
#ifdef _Python38
PYBIND11_MODULE(Py38RecastDetour, m)
#else
#ifdef _Python39
PYBIND11_MODULE(Py39RecastDetour, m)
#else
PYBIND11_MODULE(Py310RecastDetour, m)
#endif
#endif
#endif
#endif
#endif
{
	m.doc() = "Class allows to build navmesh from obj or raw vertices and polygons data. Also allows to find the shortest path between two points. Based on RecastNavigation c++ library https://github.com/recastnavigation/recastnavigation";
	py::class_<Navmesh>(m, "Navmesh")
		.def(py::init<>())
		.def("init_by_obj", &Navmesh::init_by_obj, py::arg("file_path"))
		.def("init_by_raw", &Navmesh::init_by_raw, py::arg("vertices"), py::arg("faces"))
		.def("build_navmesh", &Navmesh::build_navmesh)
		.def("get_log", &Navmesh::get_log)
		.def("pathfind_straight", &Navmesh::pathfind_straight, py::arg("start"), py::arg("end"), py::arg("vertex_mode") = 0)
		.def("pathfind_straight_batch", &Navmesh::pathfind_straight_batch, py::arg("coordinates"), py::arg("vertex_mode") = 0)
		.def("distance_to_wall", &Navmesh::distance_to_wall, py::arg("point"))
		.def("raycast", &Navmesh::raycast, py::arg("start"), py::arg("end"))
		.def("get_settings", &Navmesh::get_settings)
		.def("set_settings", &Navmesh::set_settings, py::arg("settings"))
		.def("get_partition_type", &Navmesh::get_partition_type)
		.def("set_partition_type", &Navmesh::set_partition_type, py::arg("type"))
		.def("get_bounding_box", &Navmesh::get_bounding_box)
		.def("save_navmesh", &Navmesh::save_navmesh, py::arg("file_path"))
		.def("load_navmesh", &Navmesh::load_navmesh, py::arg("file_path"))
		.def("get_navmesh_trianglulation", &Navmesh::get_navmesh_trianglulation_sample)
		.def("get_navmesh_polygonization", &Navmesh::get_navmesh_polygonization_sample)
		.def("hit_mesh", &Navmesh::hit_mesh, py::arg("start"), py::arg("end"))
		.def("init_crowd", &Navmesh::init_crowd, py::arg("maxAgents"), py::arg("maxAgentRadius"))
		.def("add_agent", &Navmesh::add_agent, py::arg("pos"), py::arg("params"))
		.def("remove_agent", &Navmesh::remove_agent, py::arg("idx"))
		.def("update_crowd", &Navmesh::update_crowd, py::arg("dt"))
		.def("set_agent_target", &Navmesh::set_agent_target, py::arg("idx"), py::arg("pos"))
		.def("set_agent_velocity", &Navmesh::set_agent_velocity, py::arg("idx"), py::arg("vel"))
		.def("reset_agent_target", &Navmesh::reset_agent_target, py::arg("idx"))
		.def("get_agent_position", &Navmesh::get_agent_position, py::arg("idx"))
		.def("get_agent_velocity", &Navmesh::get_agent_velocity, py::arg("idx"))
		.def("get_agent_state", &Navmesh::get_agent_state, py::arg("idx"))
		.def("get_agent_count", &Navmesh::get_agent_count)
		.def("update_agent_parameters", &Navmesh::update_agent_parameters, py::arg("idx"), py::arg("params"))

		// Crowd Advanced Features
		.def("set_obstacle_avoidance_params", &Navmesh::set_obstacle_avoidance_params, py::arg("idx"), py::arg("params"))
		.def("get_obstacle_avoidance_params", &Navmesh::get_obstacle_avoidance_params, py::arg("idx"))
		.def("set_query_filter_area_cost", &Navmesh::set_query_filter_area_cost, py::arg("filter_index"), py::arg("area_id"), py::arg("cost"))
		.def("get_query_filter_area_cost", &Navmesh::get_query_filter_area_cost, py::arg("filter_index"), py::arg("area_id"))
		.def("set_query_filter_include_flags", &Navmesh::set_query_filter_include_flags, py::arg("filter_index"), py::arg("flags"))
		.def("set_query_filter_exclude_flags", &Navmesh::set_query_filter_exclude_flags, py::arg("filter_index"), py::arg("flags"))
		.def("get_agent_neighbors", &Navmesh::get_agent_neighbors, py::arg("agent_idx"))
		.def("get_agent_corners", &Navmesh::get_agent_corners, py::arg("agent_idx"))
		.def("get_active_agents", &Navmesh::get_active_agents)
		.def("get_max_agent_count", &Navmesh::get_max_agent_count)
		.def("get_query_half_extents", &Navmesh::get_query_half_extents)
		.def("is_agent_active", &Navmesh::is_agent_active, py::arg("idx"))
		.def("get_agent_parameters", &Navmesh::get_agent_parameters, py::arg("idx"))

		// Convex Volumes
		.def("add_convex_volume", &Navmesh::add_convex_volume, py::arg("verts"), py::arg("minh"), py::arg("maxh"), py::arg("area"))
		.def("delete_convex_volume", &Navmesh::delete_convex_volume, py::arg("index"))
		.def("get_convex_volume_count", &Navmesh::get_convex_volume_count)
		.def("get_convex_volume", &Navmesh::get_convex_volume, py::arg("index"))
		.def("get_all_convex_volumes", &Navmesh::get_all_convex_volumes)

		// Off-Mesh Connections
		.def("add_offmesh_connection", &Navmesh::add_offmesh_connection,
		     py::arg("start_pos"), py::arg("end_pos"), py::arg("radius"),
		     py::arg("bidirectional"), py::arg("area"), py::arg("flags"))
		.def("delete_offmesh_connection", &Navmesh::delete_offmesh_connection, py::arg("index"))
		.def("get_offmesh_connection_count", &Navmesh::get_offmesh_connection_count)
		.def("get_offmesh_connection", &Navmesh::get_offmesh_connection, py::arg("index"))
		.def("get_all_offmesh_connections", &Navmesh::get_all_offmesh_connections)

		// Auto-Markup System
		.def("mark_walkable_triangles", &Navmesh::mark_walkable_triangles, py::arg("walkable_slope_angle"))
		.def("mark_box_area", &Navmesh::mark_box_area, py::arg("bmin"), py::arg("bmax"), py::arg("area_id"))
		.def("mark_cylinder_area", &Navmesh::mark_cylinder_area, py::arg("pos"), py::arg("radius"), py::arg("height"), py::arg("area_id"))
		.def("mark_convex_poly_area", &Navmesh::mark_convex_poly_area, py::arg("verts"), py::arg("hmin"), py::arg("hmax"), py::arg("area_id"))
		.def("erode_walkable_area", &Navmesh::erode_walkable_area, py::arg("radius"))
		.def("median_filter_walkable_area", &Navmesh::median_filter_walkable_area)

		// Formations & Group Behaviors
		.def("create_formation", &Navmesh::create_formation, py::arg("formation_type"), py::arg("spacing"))
		.def("delete_formation", &Navmesh::delete_formation, py::arg("formation_id"))
		.def("add_agent_to_formation", &Navmesh::add_agent_to_formation, py::arg("formation_id"), py::arg("agent_idx"))
		.def("remove_agent_from_formation", &Navmesh::remove_agent_from_formation, py::arg("agent_idx"))
		.def("set_formation_target", &Navmesh::set_formation_target, py::arg("formation_id"), py::arg("target_pos"), py::arg("target_dir"))
		.def("set_formation_leader", &Navmesh::set_formation_leader, py::arg("formation_id"), py::arg("agent_idx"))
		.def("get_formation_agents", &Navmesh::get_formation_agents, py::arg("formation_id"))
		.def("get_formation_info", &Navmesh::get_formation_info, py::arg("formation_id"))
		.def("update_formations", &Navmesh::update_formations, py::arg("dt"))
		.def("get_formation_count", &Navmesh::get_formation_count);
}
#endif // !_MAIN_APP