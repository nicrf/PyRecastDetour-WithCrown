#ifndef NAVMESHCLASS_H
#define NAVMESHCLASS_H

#include <iostream>
#include <vector>
#include <map>
#include "SampleInterfaces.h"
#include "InputGeom.h"
#include "Sample_SoloMesh.h"
#include "Sample_TileMesh.h"
#include "Sample_TempObstacles.h"
#include "Sample_Debug.h"

#include "NavMeshTesterTool.h"
#include "DetourCrowd.h"

class Navmesh
{
public:
	Navmesh();
	~Navmesh();

	void init_by_obj(std::string file_path);
	void init_by_raw(std::vector<float> vertices, std::vector<int> faces);
	void build_navmesh();
	std::string get_log();  // clear ctx log after call this function
	std::vector<float> pathfind_straight(std::vector<float> start, std::vector<float> end, int vertex_mode = 0);  // return array of path point coordinates
	std::vector<float> pathfind_straight_batch(std::vector<float> coordinates, int vertex_mode = 0);
	float distance_to_wall(std::vector<float> point);
	std::vector<float> raycast(std::vector<float> start, std::vector<float> end);
	std::map<std::string, float> get_settings();
	void set_settings(std::map<std::string, float> settings);
	int get_partition_type();
	void set_partition_type(int type);
	std::vector<float> get_bounding_box();  // return 6-tuple of floats with geometry bounding box
	void save_navmesh(std::string file_path);
	void load_navmesh(std::string file_path);
	std::tuple<std::vector<float>, std::vector<int>> get_navmesh_trianglulation();  // return the pair ([vertices coordinates], [triangles point indexes])
	std::tuple<std::vector<float>, std::vector<int>> get_navmesh_trianglulation_sample();
	std::tuple<std::vector<float>, std::vector<int>, std::vector<int>> get_navmesh_polygonization();  // return the tripple ([vertex coordinates], [polygon vertex indexes], [polygon sizes])
	std::tuple<std::vector<float>, std::vector<int>, std::vector<int>> get_navmesh_polygonization_sample();
	std::vector<float> hit_mesh(std::vector<float> start, std::vector<float> end);

	// Crowd management
	bool init_crowd(int maxAgents, float maxAgentRadius);
	int add_agent(std::vector<float> pos, std::map<std::string, float> params);
	void remove_agent(int idx);
	void update_crowd(float dt);
	bool set_agent_target(int idx, std::vector<float> pos);
	bool set_agent_velocity(int idx, std::vector<float> vel);
	bool reset_agent_target(int idx);
	std::vector<float> get_agent_position(int idx);
	std::vector<float> get_agent_velocity(int idx);
	std::map<std::string, float> get_agent_state(int idx);
	int get_agent_count();
	void update_agent_parameters(int idx, std::map<std::string, float> params);

	// Crowd Advanced Features
	void set_obstacle_avoidance_params(int idx, std::map<std::string, float> params);
	std::map<std::string, float> get_obstacle_avoidance_params(int idx);
	void set_query_filter_area_cost(int filter_index, int area_id, float cost);
	float get_query_filter_area_cost(int filter_index, int area_id);
	void set_query_filter_include_flags(int filter_index, unsigned short flags);
	void set_query_filter_exclude_flags(int filter_index, unsigned short flags);
	std::vector<int> get_agent_neighbors(int agent_idx);
	std::vector<float> get_agent_corners(int agent_idx);
	std::vector<int> get_active_agents();
	int get_max_agent_count();
	std::vector<float> get_query_half_extents();
	bool is_agent_active(int idx);
	std::map<std::string, float> get_agent_parameters(int idx);

	// Convex Volumes (Nav Volumes for area marking)
	void add_convex_volume(std::vector<float> verts, float minh, float maxh, unsigned char area);
	void delete_convex_volume(int index);
	int get_convex_volume_count();
	std::map<std::string, std::vector<float>> get_convex_volume(int index);
	std::vector<std::map<std::string, std::vector<float>>> get_all_convex_volumes();

	// Off-Mesh Connections (Climbing, Jumping, etc.)
	void add_offmesh_connection(std::vector<float> start_pos, std::vector<float> end_pos,
	                            float radius, bool bidirectional, unsigned char area,
	                            unsigned short flags);
	void delete_offmesh_connection(int index);
	int get_offmesh_connection_count();
	std::map<std::string, std::vector<float>> get_offmesh_connection(int index);
	std::vector<std::map<std::string, std::vector<float>>> get_all_offmesh_connections();

	// Auto-Markup System (Area marking based on geometry)
	void mark_walkable_triangles(float walkable_slope_angle);
	void mark_box_area(std::vector<float> bmin, std::vector<float> bmax, unsigned char area_id);
	void mark_cylinder_area(std::vector<float> pos, float radius, float height, unsigned char area_id);
	void mark_convex_poly_area(std::vector<float> verts, float hmin, float hmax, unsigned char area_id);
	void erode_walkable_area(int radius);
	void median_filter_walkable_area();

	// Formations & Group Behaviors
	int create_formation(int formation_type, float spacing);
	void delete_formation(int formation_id);
	bool add_agent_to_formation(int formation_id, int agent_idx);
	bool remove_agent_from_formation(int agent_idx);
	void set_formation_target(int formation_id, std::vector<float> target_pos, std::vector<float> target_dir);
	void set_formation_leader(int formation_id, int agent_idx);
	std::vector<int> get_formation_agents(int formation_id);
	std::map<std::string, float> get_formation_info(int formation_id);
	void update_formations(float dt);
	int get_formation_count();

private:
	InputGeom* geom;
	Sample_SoloMesh* sample;
	BuildContext ctx;
	NavMeshTesterTool* tool;
	dtCrowd* crowd;

	void clear();

	bool is_init;
	bool is_build;
	bool is_crowd_init;

	// Formation management structures
	struct Formation {
		int id;
		int type;  // 0=line, 1=column, 2=wedge, 3=box, 4=circle
		float spacing;
		int leader_idx;
		std::vector<int> agent_indices;
		float target_pos[3];
		float target_dir[3];
		bool has_target;
	};
	std::map<int, Formation> formations;
	int next_formation_id;
};

#endif