#include "Navmesh.h"
#include <algorithm>
#include <cstring>

Navmesh::Navmesh()
{
	//constructor
	geom = 0;
	sample = 0;
	tool = 0;
	crowd = 0;
	is_build = false;
	is_init = false;
	is_crowd_init = false;
	next_formation_id = 0;
}

Navmesh::~Navmesh()
{
	//destructor
	clear();
}

void Navmesh::clear()
{
	if (crowd)
	{
		dtFreeCrowd(crowd);
		crowd = 0;
	}
	delete geom;
	geom = 0;
	delete sample;
	sample = 0;
	ctx.resetLog();
	is_init = false;
	is_build = false;
	is_crowd_init = false;
}

std::string Navmesh::get_log()
{
	std::string to_return;
	for (size_t i = 0; i < ctx.getLogCount(); i++)
	{
		to_return += ctx.getLogText(i) + (i < ctx.getLogCount() - 1 ? std::string("\n") : "");
	}
	ctx.resetLog();

	return to_return;
}

std::map<std::string, float> Navmesh::get_settings()
{
	std::map<std::string, float> to_return;
	if (is_init)
	{
		BuildSettings settings;
		sample->collectSettings(settings);

		to_return["cellSize"] = settings.cellSize;
		to_return["cellHeight"] = settings.cellHeight;
		to_return["agentHeight"] = settings.agentHeight;
		to_return["agentRadius"] = settings.agentRadius;
		to_return["agentMaxClimb"] = settings.agentMaxClimb;
		to_return["agentMaxSlope"] = settings.agentMaxSlope;
		to_return["regionMinSize"] = settings.regionMinSize;
		to_return["regionMergeSize"] = settings.regionMergeSize;
		to_return["edgeMaxLen"] = settings.edgeMaxLen;
		to_return["edgeMaxError"] = settings.edgeMaxError;
		to_return["vertsPerPoly"] = settings.vertsPerPoly;  // this value should be <= 6 and >= 3
		to_return["detailSampleDist"] = settings.detailSampleDist;
		to_return["detailSampleMaxError"] = settings.detailSampleMaxError;
	}
	else
	{
		ctx.log(RC_LOG_ERROR, "Get settings: geometry is not initialized.");
	}
	return to_return;
}

void Navmesh::set_settings(std::map<std::string, float> settings)
{
	if (is_init)
	{
		std::map<std::string, float>::iterator it;

		for (it = settings.begin(); it != settings.end(); it++)
		{
			std::string k = it->first;
			float v = it->second;

			if (k == "cellSize") { sample->set_cell_size(std::max(v, 0.0001f)); }
			if (k == "cellHeight") { sample->set_cell_height(std::max(v, 0.0001f)); }
			if (k == "agentHeight") { sample->set_agent_height(std::max(v, 0.0f)); }
			if (k == "agentRadius") { sample->set_agent_radius(std::max(v, 0.0f)); }
			if (k == "agentMaxClimb") { sample->set_agent_max_climb(v); }
			if (k == "agentMaxSlope") { sample->set_agent_max_slope(v); }
			if (k == "regionMinSize") { sample->set_region_min_size(v); }
			if (k == "regionMergeSize") { sample->set_region_merge_size(v); }
			if (k == "edgeMaxLen") { sample->set_edge_max_len(v); }
			if (k == "edgeMaxError") { sample->set_edge_max_error(v); }
			if (k == "vertsPerPoly") { sample->set_verts_per_poly(std::max(3.0f, std::min(v, 6.0f))); }
			if (k == "detailSampleDist") { sample->set_detail_sample_dist(v); }
			if (k == "detailSampleMaxError") { sample->set_detail_sample_max_error(v); }
		}
	}
	else
	{
		ctx.log(RC_LOG_ERROR, "Set settings: geometry is not initialized.");
	}
}

int Navmesh::get_partition_type()
{
	if (is_init)
	{
		BuildSettings settings;
		sample->collectSettings(settings);
		return settings.partitionType;
	}
	else
	{
		ctx.log(RC_LOG_ERROR, "Get partition type: geometry is not initialized.");
	}
	return 0;
}

void Navmesh::set_partition_type(int type)
{
	if (is_init)
	{
		sample->set_partition_type(type);
	}
	else
	{
		ctx.log(RC_LOG_ERROR, "Set partition type: geometry is not initialized.");
	}
}

std::vector<float> Navmesh::get_bounding_box()
{
	std::vector<float> to_return(0);
	if (is_init)
	{
		to_return.resize(6);
		const float* min = geom->getMeshBoundsMin();
		const float* max = geom->getMeshBoundsMax();

		to_return[0] = min[0];
		to_return[1] = min[1];
		to_return[2] = min[2];

		to_return[3] = max[0];
		to_return[4] = max[1];
		to_return[5] = max[2];

		return to_return;
	}
	else
	{
		ctx.log(RC_LOG_ERROR, "Get navmesh bounding box: geometry is not initialized.");
		return to_return;
	}
}

void Navmesh::save_navmesh(std::string file_path)
{
	if (is_build)
	{
		//check is extension is *.bin
		size_t extensionPos = file_path.find_last_of('.');
		if (extensionPos == std::string::npos)
		{
			ctx.log(RC_LOG_ERROR, "Save navmesh: invalid file path.");
		}
		else
		{
			std::string extension = file_path.substr(extensionPos);
			std::transform(extension.begin(), extension.end(), extension.begin(), tolower);
			if (extension == ".bin")
			{
				sample->save_to_file(file_path.c_str());
			}
			else
			{
				ctx.log(RC_LOG_ERROR, "Save navmesh: invalid file extension (it should be *.bin).");
			}
		}
	}
	else
	{
		ctx.log(RC_LOG_ERROR, "Save navmesh: navmesh is not builded.");
	}
}

void Navmesh::load_navmesh(std::string file_path)
{
	if (is_init)
	{
		sample->load_from_file(file_path.c_str());
	}
	else
	{
		ctx.log(RC_LOG_ERROR, "Load navmesh: geometry is not initialized.");
	}
}

std::tuple<std::vector<float>, std::vector<int>> Navmesh::get_navmesh_trianglulation()
{
	if (is_build)
	{
		std::vector<float> vertices(0);
		std::vector<int> triangles(0);

		rcPolyMesh* pmesh = sample->get_m_pmesh();
		for (int v_index = 0; v_index < pmesh->nverts; v_index++) {
			vertices.push_back(pmesh->bmin[0] + pmesh->cs * pmesh->verts[3 * v_index]);
			vertices.push_back(pmesh->bmin[1] + pmesh->ch * pmesh->verts[3 * v_index + 1]);
			vertices.push_back(pmesh->bmin[2] + pmesh->cs * pmesh->verts[3 * v_index + 2]);
		}

		for (int p_index = 0; p_index < pmesh->npolys; p_index++) {
			int pv = p_index * 2 * pmesh->nvp;
			unsigned short v_start = pmesh->polys[pv];

			for (int j = 2; j < pmesh->nvp; j++) {
				unsigned short v = pmesh->polys[pv + j];
				if (v == 0xffff) {
					break;
				}
				unsigned short v_prev = pmesh->polys[pv + j - 1];
				triangles.push_back(v_start);
				triangles.push_back(v_prev);
				triangles.push_back(v);
			}
		}

		std::tuple<std::vector<float>, std::vector<int>> to_return = std::make_tuple(vertices, triangles);
		return to_return;
	}
	else
	{
		ctx.log(RC_LOG_ERROR, "Get navmesh trianglulation: navmesh is not builded.");
		std::vector<float> vertices(0);
		std::vector<int> triangles(0);
		std::tuple<std::vector<float>, std::vector<int>> to_return = std::make_tuple(vertices, triangles);
		return to_return;
	}
}

std::tuple<std::vector<float>, std::vector<int>> Navmesh::get_navmesh_trianglulation_sample()
{
	if (is_build)
	{
		std::vector<float> vertices(0);
		std::vector<int> triangles(0);

		const dtNavMesh* navmesh = sample->getNavMesh();
		int max_tiles = navmesh->getMaxTiles();
		int start_tile_index = 0;
		for (size_t i = 0; i < max_tiles; i++)
		{
			const dtMeshTile* tile = navmesh->getTile(i);
			if (!tile->header) continue;

			for (size_t j = 0; j < tile->header->vertCount; j++)
			{
				vertices.push_back(tile->verts[3 * j]);
				vertices.push_back(tile->verts[3 * j + 1]);
				vertices.push_back(tile->verts[3 * j + 2]);
			}

			for (int j = 0; j < tile->header->polyCount; ++j)
			{
				const dtPoly* p = &tile->polys[j];
				if (p->getType() == DT_POLYTYPE_OFFMESH_CONNECTION)	// skip off-mesh links.
					continue;

				const dtPolyDetail* pd = &tile->detailMeshes[j];
				for (int k = 0; k < pd->triCount; ++k)
				{
					const unsigned char* t = &tile->detailTris[(pd->triBase + k) * 4];
					triangles.push_back(p->verts[t[0]] + start_tile_index);
					triangles.push_back(p->verts[t[1]] + start_tile_index);
					triangles.push_back(p->verts[t[2]] + start_tile_index);
				}
			}
			start_tile_index += tile->header->vertCount;
		}

		std::tuple<std::vector<float>, std::vector<int>> to_return = std::make_tuple(vertices, triangles);
		return to_return;
	}
	else
	{
		ctx.log(RC_LOG_ERROR, "Get navmesh trianglulation: navmesh is not builded.");
		std::vector<float> vertices(0);
		std::vector<int> triangles(0);
		std::tuple<std::vector<float>, std::vector<int>> to_return = std::make_tuple(vertices, triangles);
		return to_return;
	}
}

std::tuple<std::vector<float>, std::vector<int>, std::vector<int>> Navmesh::get_navmesh_polygonization()
{
	if (is_build)
	{
		std::vector<float> vertices(0);
		std::vector<int> polygons(0);
		std::vector<int> sizes(0);

		rcPolyMesh* pmesh = sample->get_m_pmesh();
		for (int v_index = 0; v_index < pmesh->nverts; v_index++) {
			vertices.push_back(pmesh->bmin[0] + pmesh->cs * pmesh->verts[3 * v_index]);
			vertices.push_back(pmesh->bmin[1] + pmesh->ch * pmesh->verts[3 * v_index + 1]);
			vertices.push_back(pmesh->bmin[2] + pmesh->cs * pmesh->verts[3 * v_index + 2]);
		}

		for (int p_index = 0; p_index < pmesh->npolys; p_index++) {
			int pv = p_index * 2 * pmesh->nvp;
			unsigned short p_size = 0;
			for (int j = 0; j < pmesh->nvp; j++) {
				unsigned short v = pmesh->polys[pv + j];
				if (v == 0xffff) {
					break;
				}
				polygons.push_back(v);
				p_size++;
			}
			sizes.push_back(p_size);
		}

		std::tuple<std::vector<float>, std::vector<int>, std::vector<int>> to_return = std::make_tuple(vertices, polygons, sizes);
		return to_return;
	}
	else
	{
		ctx.log(RC_LOG_ERROR, "Get navmesh polygonization: navmesh is not builded.");
		std::vector<float> vertices(0);
		std::vector<int> polygons(0);
		std::vector<int> sizes(0);
		std::tuple<std::vector<float>, std::vector<int>, std::vector<int>> to_return = std::make_tuple(vertices, polygons, sizes);
		return to_return;
	}
}

std::tuple<std::vector<float>, std::vector<int>, std::vector<int>> Navmesh::get_navmesh_polygonization_sample()
{
	if (is_build)
	{
		std::vector<float> vertices(0);
		std::vector<int> polygons(0);
		std::vector<int> sizes(0);

		const dtNavMesh* navmesh = sample->getNavMesh();
		int max_tiles = navmesh->getMaxTiles();
		for (size_t i = 0; i < max_tiles; i++)
		{
			const dtMeshTile* tile = navmesh->getTile(i);
			if (!tile->header) continue;

			for (size_t j = 0; j < tile->header->vertCount; j++)
			{
				vertices.push_back(tile->verts[3 * j]);
				vertices.push_back(tile->verts[3 * j + 1]);
				vertices.push_back(tile->verts[3 * j + 2]);
			}

			for (int j = 0; j < tile->header->polyCount; ++j)
			{
				const dtPoly* p = &tile->polys[j];
				if (p->getType() == DT_POLYTYPE_OFFMESH_CONNECTION)	// skip off-mesh links.
					continue;

				for (int k = 0; k < p->vertCount; k++)
				{
					polygons.push_back(p->verts[k]);
				}
				sizes.push_back(p->vertCount);
			}
		}

		std::tuple<std::vector<float>, std::vector<int>, std::vector<int>> to_return = std::make_tuple(vertices, polygons, sizes);
		return to_return;
	}
	else
	{
		ctx.log(RC_LOG_ERROR, "Get navmesh polygonization: navmesh is not builded.");
		std::vector<float> vertices(0);
		std::vector<int> polygons(0);
		std::vector<int> sizes(0);
		std::tuple<std::vector<float>, std::vector<int>, std::vector<int>> to_return = std::make_tuple(vertices, polygons, sizes);
		return to_return;
	}
}

void Navmesh::init_by_raw(std::vector<float> vertices, std::vector<int> faces)
{
	if (is_init)
	{
		clear();
	}

	geom = new InputGeom;
	if (!geom->loadMesh_raw(&ctx, vertices, faces))
	{
		ctx.log(RC_LOG_ERROR, "Fail to load geometry from raw data.");
		clear();
	}
	else
	{
		sample = new Sample_SoloMesh();
		sample->setContext(&ctx);
		sample->handleMeshChanged(geom);
		sample->resetCommonSettings();
		tool = new NavMeshTesterTool();
		sample->setTool(tool);

		is_init = true;
	}
}

void Navmesh::init_by_obj(std::string file_path)
{
	if (is_init)
	{
		clear();
	}

	geom = new InputGeom;
	if (!geom->load(&ctx, file_path))
	{
		ctx.log(RC_LOG_ERROR, "Fail to load geometry.");
		clear();
	}
	else
	{
		sample = new Sample_SoloMesh();
		sample->setContext(&ctx);
		sample->handleMeshChanged(geom);
		sample->resetCommonSettings();
		tool = new NavMeshTesterTool();
		sample->setTool(tool);

		is_init = true;
	}
}

void Navmesh::build_navmesh()
{
	sample->handleSettings();
	if (!sample->handleBuild())
	{
		ctx.log(RC_LOG_ERROR, "Fail to build navmesh.");
		is_build = false;
	}
	else
	{
		is_build = true;
	}
}

std::vector<float> Navmesh::pathfind_straight(std::vector<float> start, std::vector<float> end, int vertex_mode)
{
	if (start.size() == 3 && end.size() == 3 && is_build)
	{
		tool->set_mode_streight(vertex_mode);

		tool->set_points(&start[0], &end[0]);

		int length = tool->get_path_points_count();
		float* coordinates = tool->get_path();
		std::vector<float> to_return(3 * length);
		for (size_t i = 0; i < length; i++)
		{
			to_return[3 * i] = coordinates[3 * i];
			to_return[3 * i + 1] = coordinates[3 * i + 1];
			to_return[3 * i + 2] = coordinates[3 * i + 2];
		}
		return to_return;
	}
	else
	{
		if (!is_build)
		{
			ctx.log(RC_LOG_ERROR, "Find straight path: navmesh is not builded.");
		}
		else
		{
			ctx.log(RC_LOG_ERROR, "Find straight path: invalid input vectors.");
		}
		
		std::vector<float> to_return(0);
		return to_return;
	}
}

std::vector<float> Navmesh::pathfind_straight_batch(std::vector<float> coordinates, int vertex_mode)
{
	if (coordinates.size() % 6 == 0 && is_build)
	{
		std::vector<float> to_return(0);
		// we assume that first 6 coordinates in the array define the first pair of start and end point, next 6 coordinates defines the second pair and so on
		for (size_t step = 0; step < coordinates.size() / 6; step++)
		{
			std::vector<float> start(3);
			std::vector<float> end(3);
			copy(coordinates.begin() + 6 * step, coordinates.begin() + 6 * step + 3, start.begin());
			copy(coordinates.begin() + 6 * step + 3, coordinates.begin() + 6 * step + 6, end.begin());

			// calculate the path
			std::vector<float> path = pathfind_straight(start, end, vertex_mode);

			// add calculated coordinates to the one output array
			// each result starts from the number of points (and then x3 floats for actual coordinates)
			to_return.push_back(path.size() / 3);
			to_return.insert(to_return.end(), path.begin(), path.end());
		}

		return to_return;
	}
	else
	{
		if (!is_build)
		{
			ctx.log(RC_LOG_ERROR, "Find straight path batch: navmesh is not builded.");
		}
		else
		{
			ctx.log(RC_LOG_ERROR, "Find straight path batch: invalid input vector with coordinates.");
		}

		std::vector<float> to_return(0);
		return to_return;
	}
}

float Navmesh::distance_to_wall(std::vector<float> point)
{
	if (is_build && point.size() == 3)
	{
		tool->set_mode_distance();
		tool->set_point(&point[0]);

		float to_return = tool->get_distance_to_wall();
		return to_return;
	}
	else
	{
		if (!is_build)
		{
			ctx.log(RC_LOG_ERROR, "Distance to wall: navmesh is not builded.");
		}
		else
		{
			ctx.log(RC_LOG_ERROR, "Distance to wall: invalid input vector.");
		}
	}
	return 0.0f;
}

std::vector<float> Navmesh::raycast(std::vector<float> start, std::vector<float> end)
{
	if (start.size() == 3 && end.size() == 3 && is_build)
	{
		tool->set_mode_raycast();

		tool->set_points(&start[0], &end[0]);

		int length = tool->get_path_points_count();
		float* coordinates = tool->get_path();
		std::vector<float> to_return(3 * length);
		for (size_t i = 0; i < length; i++)
		{
			to_return[3 * i] = coordinates[3 * i];
			to_return[3 * i + 1] = coordinates[3 * i + 1];
			to_return[3 * i + 2] = coordinates[3 * i + 2];
		}
		return to_return;
	}
	else
	{
		if (is_build)
		{
			ctx.log(RC_LOG_ERROR, "Raycast: navmesh is not builded.");
		}
		else
		{
			ctx.log(RC_LOG_ERROR, "Raycast: invalid input vectors.");
		}

		std::vector<float> to_return(0);
		return to_return;
	}
}

std::vector<float> Navmesh::hit_mesh(std::vector<float> start, std::vector<float> end)
{
	if (start.size() == 3 && end.size() == 3)
	{
		if (is_init)
		{
			float hit_time;
			bool hit = geom->raycastMesh(&start[0], &end[0], hit_time);
			if (hit)
			{
				std::vector<float> to_return(3);
				for (int i = 0; i < to_return.size(); i++)
				{
					to_return[i] = start[i] + (end[i] - start[i]) * hit_time;
				}
				return to_return;
			}
			else
			{
				return end;
			}
		}
		else
		{
			ctx.log(RC_LOG_ERROR, "Hit mesh: geometry is not initialized.");
		}
	}
	else
	{
		ctx.log(RC_LOG_ERROR, "Hit mesh: invalid input vectors.");
	}
}

// Crowd management implementation
bool Navmesh::init_crowd(int maxAgents, float maxAgentRadius)
{
	if (!is_build)
	{
		ctx.log(RC_LOG_ERROR, "Init crowd: navmesh is not built.");
		return false;
	}

	if (crowd)
	{
		dtFreeCrowd(crowd);
		crowd = 0;
	}

	crowd = dtAllocCrowd();
	if (!crowd)
	{
		ctx.log(RC_LOG_ERROR, "Init crowd: failed to allocate crowd.");
		return false;
	}

	dtNavMesh* navmesh = sample->getNavMesh();
	if (!navmesh)
	{
		ctx.log(RC_LOG_ERROR, "Init crowd: navmesh not available.");
		dtFreeCrowd(crowd);
		crowd = 0;
		return false;
	}

	if (!crowd->init(maxAgents, maxAgentRadius, navmesh))
	{
		ctx.log(RC_LOG_ERROR, "Init crowd: failed to initialize crowd.");
		dtFreeCrowd(crowd);
		crowd = 0;
		return false;
	}

	is_crowd_init = true;
	return true;
}

int Navmesh::add_agent(std::vector<float> pos, std::map<std::string, float> params)
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Add agent: crowd is not initialized.");
		return -1;
	}

	if (pos.size() != 3)
	{
		ctx.log(RC_LOG_ERROR, "Add agent: invalid position vector (must have 3 elements).");
		return -1;
	}

	dtCrowdAgentParams ap;
	memset(&ap, 0, sizeof(ap));

	// Set default values
	ap.radius = 0.6f;
	ap.height = 2.0f;
	ap.maxAcceleration = 8.0f;
	ap.maxSpeed = 3.5f;
	ap.collisionQueryRange = ap.radius * 12.0f;
	ap.pathOptimizationRange = ap.radius * 30.0f;
	ap.separationWeight = 2.0f;
	ap.updateFlags = 0;
	ap.updateFlags |= DT_CROWD_ANTICIPATE_TURNS;
	ap.updateFlags |= DT_CROWD_OPTIMIZE_VIS;
	ap.updateFlags |= DT_CROWD_OPTIMIZE_TOPO;
	ap.updateFlags |= DT_CROWD_OBSTACLE_AVOIDANCE;
	ap.obstacleAvoidanceType = 3;
	ap.queryFilterType = 0;
	ap.userData = 0;

	// Override with provided parameters
	std::map<std::string, float>::iterator it;
	for (it = params.begin(); it != params.end(); it++)
	{
		std::string k = it->first;
		float v = it->second;

		if (k == "radius") { ap.radius = v; }
		else if (k == "height") { ap.height = v; }
		else if (k == "maxAcceleration") { ap.maxAcceleration = v; }
		else if (k == "maxSpeed") { ap.maxSpeed = v; }
		else if (k == "collisionQueryRange") { ap.collisionQueryRange = v; }
		else if (k == "pathOptimizationRange") { ap.pathOptimizationRange = v; }
		else if (k == "separationWeight") { ap.separationWeight = v; }
		else if (k == "updateFlags") { ap.updateFlags = (unsigned char)v; }
		else if (k == "obstacleAvoidanceType") { ap.obstacleAvoidanceType = (unsigned char)v; }
		else if (k == "queryFilterType") { ap.queryFilterType = (unsigned char)v; }
	}

	float p[3] = { pos[0], pos[1], pos[2] };
	int idx = crowd->addAgent(p, &ap);

	if (idx == -1)
	{
		ctx.log(RC_LOG_ERROR, "Add agent: failed to add agent to crowd.");
	}

	return idx;
}

void Navmesh::remove_agent(int idx)
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Remove agent: crowd is not initialized.");
		return;
	}

	crowd->removeAgent(idx);
}

void Navmesh::update_crowd(float dt)
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Update crowd: crowd is not initialized.");
		return;
	}

	crowd->update(dt, 0);
}

bool Navmesh::set_agent_target(int idx, std::vector<float> pos)
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Set agent target: crowd is not initialized.");
		return false;
	}

	if (pos.size() != 3)
	{
		ctx.log(RC_LOG_ERROR, "Set agent target: invalid position vector (must have 3 elements).");
		return false;
	}

	// Find nearest point on navmesh
	dtNavMeshQuery* navquery = sample->getNavMeshQuery();
	if (!navquery)
	{
		ctx.log(RC_LOG_ERROR, "Set agent target: navmesh query not available.");
		return false;
	}

	const float ext[3] = { 2.0f, 4.0f, 2.0f };
	dtQueryFilter filter;
	dtPolyRef targetRef;
	float targetPos[3] = { pos[0], pos[1], pos[2] };
	float nearestPt[3];

	navquery->findNearestPoly(targetPos, ext, &filter, &targetRef, nearestPt);

	if (!targetRef)
	{
		ctx.log(RC_LOG_ERROR, "Set agent target: could not find nearest polygon.");
		return false;
	}

	return crowd->requestMoveTarget(idx, targetRef, nearestPt);
}

bool Navmesh::set_agent_velocity(int idx, std::vector<float> vel)
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Set agent velocity: crowd is not initialized.");
		return false;
	}

	if (vel.size() != 3)
	{
		ctx.log(RC_LOG_ERROR, "Set agent velocity: invalid velocity vector (must have 3 elements).");
		return false;
	}

	float v[3] = { vel[0], vel[1], vel[2] };
	return crowd->requestMoveVelocity(idx, v);
}

bool Navmesh::reset_agent_target(int idx)
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Reset agent target: crowd is not initialized.");
		return false;
	}

	return crowd->resetMoveTarget(idx);
}

std::vector<float> Navmesh::get_agent_position(int idx)
{
	std::vector<float> to_return(0);

	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Get agent position: crowd is not initialized.");
		return to_return;
	}

	const dtCrowdAgent* ag = crowd->getAgent(idx);
	if (!ag || !ag->active)
	{
		ctx.log(RC_LOG_ERROR, "Get agent position: invalid agent index or agent not active.");
		return to_return;
	}

	to_return.resize(3);
	to_return[0] = ag->npos[0];
	to_return[1] = ag->npos[1];
	to_return[2] = ag->npos[2];

	return to_return;
}

std::vector<float> Navmesh::get_agent_velocity(int idx)
{
	std::vector<float> to_return(0);

	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Get agent velocity: crowd is not initialized.");
		return to_return;
	}

	const dtCrowdAgent* ag = crowd->getAgent(idx);
	if (!ag || !ag->active)
	{
		ctx.log(RC_LOG_ERROR, "Get agent velocity: invalid agent index or agent not active.");
		return to_return;
	}

	to_return.resize(3);
	to_return[0] = ag->vel[0];
	to_return[1] = ag->vel[1];
	to_return[2] = ag->vel[2];

	return to_return;
}

std::map<std::string, float> Navmesh::get_agent_state(int idx)
{
	std::map<std::string, float> to_return;

	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Get agent state: crowd is not initialized.");
		return to_return;
	}

	const dtCrowdAgent* ag = crowd->getAgent(idx);
	if (!ag || !ag->active)
	{
		ctx.log(RC_LOG_ERROR, "Get agent state: invalid agent index or agent not active.");
		return to_return;
	}

	to_return["active"] = ag->active ? 1.0f : 0.0f;
	to_return["state"] = (float)ag->state;
	to_return["partial"] = ag->partial ? 1.0f : 0.0f;

	to_return["posX"] = ag->npos[0];
	to_return["posY"] = ag->npos[1];
	to_return["posZ"] = ag->npos[2];

	to_return["velX"] = ag->vel[0];
	to_return["velY"] = ag->vel[1];
	to_return["velZ"] = ag->vel[2];

	to_return["dvelX"] = ag->dvel[0];
	to_return["dvelY"] = ag->dvel[1];
	to_return["dvelZ"] = ag->dvel[2];

	to_return["nvelX"] = ag->nvel[0];
	to_return["nvelY"] = ag->nvel[1];
	to_return["nvelZ"] = ag->nvel[2];

	to_return["desiredSpeed"] = ag->desiredSpeed;
	to_return["radius"] = ag->params.radius;
	to_return["height"] = ag->params.height;
	to_return["maxAcceleration"] = ag->params.maxAcceleration;
	to_return["maxSpeed"] = ag->params.maxSpeed;
	to_return["collisionQueryRange"] = ag->params.collisionQueryRange;
	to_return["pathOptimizationRange"] = ag->params.pathOptimizationRange;
	to_return["separationWeight"] = ag->params.separationWeight;

	to_return["targetState"] = (float)ag->targetState;
	to_return["targetPosX"] = ag->targetPos[0];
	to_return["targetPosY"] = ag->targetPos[1];
	to_return["targetPosZ"] = ag->targetPos[2];

	return to_return;
}

int Navmesh::get_agent_count()
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Get agent count: crowd is not initialized.");
		return 0;
	}

	return crowd->getAgentCount();
}

void Navmesh::update_agent_parameters(int idx, std::map<std::string, float> params)
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Update agent parameters: crowd is not initialized.");
		return;
	}

	dtCrowdAgent* ag = crowd->getEditableAgent(idx);
	if (!ag || !ag->active)
	{
		ctx.log(RC_LOG_ERROR, "Update agent parameters: invalid agent index or agent not active.");
		return;
	}

	dtCrowdAgentParams ap = ag->params;

	// Update with provided parameters
	std::map<std::string, float>::iterator it;
	for (it = params.begin(); it != params.end(); it++)
	{
		std::string k = it->first;
		float v = it->second;

		if (k == "radius") { ap.radius = v; }
		else if (k == "height") { ap.height = v; }
		else if (k == "maxAcceleration") { ap.maxAcceleration = v; }
		else if (k == "maxSpeed") { ap.maxSpeed = v; }
		else if (k == "collisionQueryRange") { ap.collisionQueryRange = v; }
		else if (k == "pathOptimizationRange") { ap.pathOptimizationRange = v; }
		else if (k == "separationWeight") { ap.separationWeight = v; }
		else if (k == "updateFlags") { ap.updateFlags = (unsigned char)v; }
		else if (k == "obstacleAvoidanceType") { ap.obstacleAvoidanceType = (unsigned char)v; }
		else if (k == "queryFilterType") { ap.queryFilterType = (unsigned char)v; }
	}

	crowd->updateAgentParameters(idx, &ap);
}

// ============================================================================
// CROWD ADVANCED FEATURES IMPLEMENTATION
// ============================================================================

void Navmesh::set_obstacle_avoidance_params(int idx, std::map<std::string, float> params)
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Set obstacle avoidance params: crowd is not initialized.");
		return;
	}

	if (idx < 0 || idx >= DT_CROWD_MAX_OBSTAVOIDANCE_PARAMS)
	{
		ctx.log(RC_LOG_ERROR, "Set obstacle avoidance params: invalid index.");
		return;
	}

	dtObstacleAvoidanceParams oap;
	const dtObstacleAvoidanceParams* currentParams = crowd->getObstacleAvoidanceParams(idx);
	if (currentParams)
	{
		oap = *currentParams;
	}

	// Update with provided parameters
	std::map<std::string, float>::iterator it;
	for (it = params.begin(); it != params.end(); it++)
	{
		std::string k = it->first;
		float v = it->second;

		if (k == "velBias") { oap.velBias = v; }
		else if (k == "weightDesVel") { oap.weightDesVel = v; }
		else if (k == "weightCurVel") { oap.weightCurVel = v; }
		else if (k == "weightSide") { oap.weightSide = v; }
		else if (k == "weightToi") { oap.weightToi = v; }
		else if (k == "horizTime") { oap.horizTime = v; }
		else if (k == "gridSize") { oap.gridSize = (unsigned char)v; }
		else if (k == "adaptiveDivs") { oap.adaptiveDivs = (unsigned char)v; }
		else if (k == "adaptiveRings") { oap.adaptiveRings = (unsigned char)v; }
		else if (k == "adaptiveDepth") { oap.adaptiveDepth = (unsigned char)v; }
	}

	crowd->setObstacleAvoidanceParams(idx, &oap);
}

std::map<std::string, float> Navmesh::get_obstacle_avoidance_params(int idx)
{
	std::map<std::string, float> to_return;

	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Get obstacle avoidance params: crowd is not initialized.");
		return to_return;
	}

	if (idx < 0 || idx >= DT_CROWD_MAX_OBSTAVOIDANCE_PARAMS)
	{
		ctx.log(RC_LOG_ERROR, "Get obstacle avoidance params: invalid index.");
		return to_return;
	}

	const dtObstacleAvoidanceParams* oap = crowd->getObstacleAvoidanceParams(idx);
	if (!oap)
	{
		ctx.log(RC_LOG_ERROR, "Get obstacle avoidance params: failed to get params.");
		return to_return;
	}

	to_return["velBias"] = oap->velBias;
	to_return["weightDesVel"] = oap->weightDesVel;
	to_return["weightCurVel"] = oap->weightCurVel;
	to_return["weightSide"] = oap->weightSide;
	to_return["weightToi"] = oap->weightToi;
	to_return["horizTime"] = oap->horizTime;
	to_return["gridSize"] = (float)oap->gridSize;
	to_return["adaptiveDivs"] = (float)oap->adaptiveDivs;
	to_return["adaptiveRings"] = (float)oap->adaptiveRings;
	to_return["adaptiveDepth"] = (float)oap->adaptiveDepth;

	return to_return;
}

void Navmesh::set_query_filter_area_cost(int filter_index, int area_id, float cost)
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Set query filter area cost: crowd is not initialized.");
		return;
	}

	if (filter_index < 0 || filter_index >= DT_CROWD_MAX_QUERY_FILTER_TYPE)
	{
		ctx.log(RC_LOG_ERROR, "Set query filter area cost: invalid filter index.");
		return;
	}

	dtQueryFilter* filter = crowd->getEditableFilter(filter_index);
	if (filter)
	{
		filter->setAreaCost(area_id, cost);
	}
}

float Navmesh::get_query_filter_area_cost(int filter_index, int area_id)
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Get query filter area cost: crowd is not initialized.");
		return 0.0f;
	}

	if (filter_index < 0 || filter_index >= DT_CROWD_MAX_QUERY_FILTER_TYPE)
	{
		ctx.log(RC_LOG_ERROR, "Get query filter area cost: invalid filter index.");
		return 0.0f;
	}

	const dtQueryFilter* filter = crowd->getFilter(filter_index);
	if (filter)
	{
		return filter->getAreaCost(area_id);
	}

	return 0.0f;
}

void Navmesh::set_query_filter_include_flags(int filter_index, unsigned short flags)
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Set query filter include flags: crowd is not initialized.");
		return;
	}

	if (filter_index < 0 || filter_index >= DT_CROWD_MAX_QUERY_FILTER_TYPE)
	{
		ctx.log(RC_LOG_ERROR, "Set query filter include flags: invalid filter index.");
		return;
	}

	dtQueryFilter* filter = crowd->getEditableFilter(filter_index);
	if (filter)
	{
		filter->setIncludeFlags(flags);
	}
}

void Navmesh::set_query_filter_exclude_flags(int filter_index, unsigned short flags)
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Set query filter exclude flags: crowd is not initialized.");
		return;
	}

	if (filter_index < 0 || filter_index >= DT_CROWD_MAX_QUERY_FILTER_TYPE)
	{
		ctx.log(RC_LOG_ERROR, "Set query filter exclude flags: invalid filter index.");
		return;
	}

	dtQueryFilter* filter = crowd->getEditableFilter(filter_index);
	if (filter)
	{
		filter->setExcludeFlags(flags);
	}
}

std::vector<int> Navmesh::get_agent_neighbors(int agent_idx)
{
	std::vector<int> to_return;

	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Get agent neighbors: crowd is not initialized.");
		return to_return;
	}

	const dtCrowdAgent* ag = crowd->getAgent(agent_idx);
	if (!ag || !ag->active)
	{
		ctx.log(RC_LOG_ERROR, "Get agent neighbors: invalid agent index or agent not active.");
		return to_return;
	}

	for (int i = 0; i < ag->nneis; i++)
	{
		to_return.push_back(ag->neis[i].idx);
	}

	return to_return;
}

std::vector<float> Navmesh::get_agent_corners(int agent_idx)
{
	std::vector<float> to_return;

	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Get agent corners: crowd is not initialized.");
		return to_return;
	}

	const dtCrowdAgent* ag = crowd->getAgent(agent_idx);
	if (!ag || !ag->active)
	{
		ctx.log(RC_LOG_ERROR, "Get agent corners: invalid agent index or agent not active.");
		return to_return;
	}

	for (int i = 0; i < ag->ncorners; i++)
	{
		to_return.push_back(ag->cornerVerts[i * 3]);
		to_return.push_back(ag->cornerVerts[i * 3 + 1]);
		to_return.push_back(ag->cornerVerts[i * 3 + 2]);
	}

	return to_return;
}

std::vector<int> Navmesh::get_active_agents()
{
	std::vector<int> to_return;

	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Get active agents: crowd is not initialized.");
		return to_return;
	}

	int maxAgents = crowd->getAgentCount();
	for (int i = 0; i < maxAgents; i++)
	{
		const dtCrowdAgent* ag = crowd->getAgent(i);
		if (ag && ag->active)
		{
			to_return.push_back(i);
		}
	}

	return to_return;
}

int Navmesh::get_max_agent_count()
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Get max agent count: crowd is not initialized.");
		return 0;
	}

	return crowd->getAgentCount();
}

std::vector<float> Navmesh::get_query_half_extents()
{
	std::vector<float> to_return;

	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Get query half extents: crowd is not initialized.");
		return to_return;
	}

	const float* ext = crowd->getQueryHalfExtents();
	if (ext)
	{
		to_return.push_back(ext[0]);
		to_return.push_back(ext[1]);
		to_return.push_back(ext[2]);
	}

	return to_return;
}

bool Navmesh::is_agent_active(int idx)
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Is agent active: crowd is not initialized.");
		return false;
	}

	const dtCrowdAgent* ag = crowd->getAgent(idx);
	return (ag && ag->active);
}

std::map<std::string, float> Navmesh::get_agent_parameters(int idx)
{
	std::map<std::string, float> to_return;

	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Get agent parameters: crowd is not initialized.");
		return to_return;
	}

	const dtCrowdAgent* ag = crowd->getAgent(idx);
	if (!ag || !ag->active)
	{
		ctx.log(RC_LOG_ERROR, "Get agent parameters: invalid agent index or agent not active.");
		return to_return;
	}

	to_return["radius"] = ag->params.radius;
	to_return["height"] = ag->params.height;
	to_return["maxAcceleration"] = ag->params.maxAcceleration;
	to_return["maxSpeed"] = ag->params.maxSpeed;
	to_return["collisionQueryRange"] = ag->params.collisionQueryRange;
	to_return["pathOptimizationRange"] = ag->params.pathOptimizationRange;
	to_return["separationWeight"] = ag->params.separationWeight;
	to_return["updateFlags"] = (float)ag->params.updateFlags;
	to_return["obstacleAvoidanceType"] = (float)ag->params.obstacleAvoidanceType;
	to_return["queryFilterType"] = (float)ag->params.queryFilterType;

	return to_return;
}

// ============================================================================
// CONVEX VOLUMES IMPLEMENTATION
// ============================================================================

void Navmesh::add_convex_volume(std::vector<float> verts, float minh, float maxh, unsigned char area)
{
	if (!is_init)
	{
		ctx.log(RC_LOG_ERROR, "Add convex volume: geometry is not initialized.");
		return;
	}

	if (verts.size() % 3 != 0 || verts.size() < 9)
	{
		ctx.log(RC_LOG_ERROR, "Add convex volume: invalid vertices (must be multiple of 3 with at least 3 points).");
		return;
	}

	int nverts = verts.size() / 3;
	if (nverts > MAX_CONVEXVOL_PTS)
	{
		ctx.log(RC_LOG_ERROR, "Add convex volume: too many vertices (max is 12).");
		return;
	}

	geom->addConvexVolume(&verts[0], nverts, minh, maxh, area);
}

void Navmesh::delete_convex_volume(int index)
{
	if (!is_init)
	{
		ctx.log(RC_LOG_ERROR, "Delete convex volume: geometry is not initialized.");
		return;
	}

	geom->deleteConvexVolume(index);
}

int Navmesh::get_convex_volume_count()
{
	if (!is_init)
	{
		ctx.log(RC_LOG_ERROR, "Get convex volume count: geometry is not initialized.");
		return 0;
	}

	return geom->getConvexVolumeCount();
}

std::map<std::string, std::vector<float>> Navmesh::get_convex_volume(int index)
{
	std::map<std::string, std::vector<float>> to_return;

	if (!is_init)
	{
		ctx.log(RC_LOG_ERROR, "Get convex volume: geometry is not initialized.");
		return to_return;
	}

	const ConvexVolume* vols = geom->getConvexVolumes();
	int count = geom->getConvexVolumeCount();

	if (index < 0 || index >= count)
	{
		ctx.log(RC_LOG_ERROR, "Get convex volume: invalid index.");
		return to_return;
	}

	const ConvexVolume& vol = vols[index];

	std::vector<float> verts_list;
	for (int i = 0; i < vol.nverts * 3; i++)
	{
		verts_list.push_back(vol.verts[i]);
	}

	to_return["verts"] = verts_list;
	to_return["hmin"] = std::vector<float>{vol.hmin};
	to_return["hmax"] = std::vector<float>{vol.hmax};
	to_return["area"] = std::vector<float>{(float)vol.area};

	return to_return;
}

std::vector<std::map<std::string, std::vector<float>>> Navmesh::get_all_convex_volumes()
{
	std::vector<std::map<std::string, std::vector<float>>> to_return;

	if (!is_init)
	{
		ctx.log(RC_LOG_ERROR, "Get all convex volumes: geometry is not initialized.");
		return to_return;
	}

	int count = geom->getConvexVolumeCount();
	for (int i = 0; i < count; i++)
	{
		to_return.push_back(get_convex_volume(i));
	}

	return to_return;
}

// ============================================================================
// OFF-MESH CONNECTIONS IMPLEMENTATION
// ============================================================================

void Navmesh::add_offmesh_connection(std::vector<float> start_pos, std::vector<float> end_pos,
                                     float radius, bool bidirectional, unsigned char area,
                                     unsigned short flags)
{
	if (!is_init)
	{
		ctx.log(RC_LOG_ERROR, "Add off-mesh connection: geometry is not initialized.");
		return;
	}

	if (start_pos.size() != 3 || end_pos.size() != 3)
	{
		ctx.log(RC_LOG_ERROR, "Add off-mesh connection: invalid positions (must have 3 elements each).");
		return;
	}

	geom->addOffMeshConnection(&start_pos[0], &end_pos[0], radius, bidirectional ? 1 : 0, area, flags);
}

void Navmesh::delete_offmesh_connection(int index)
{
	if (!is_init)
	{
		ctx.log(RC_LOG_ERROR, "Delete off-mesh connection: geometry is not initialized.");
		return;
	}

	geom->deleteOffMeshConnection(index);
}

int Navmesh::get_offmesh_connection_count()
{
	if (!is_init)
	{
		ctx.log(RC_LOG_ERROR, "Get off-mesh connection count: geometry is not initialized.");
		return 0;
	}

	return geom->getOffMeshConnectionCount();
}

std::map<std::string, std::vector<float>> Navmesh::get_offmesh_connection(int index)
{
	std::map<std::string, std::vector<float>> to_return;

	if (!is_init)
	{
		ctx.log(RC_LOG_ERROR, "Get off-mesh connection: geometry is not initialized.");
		return to_return;
	}

	int count = geom->getOffMeshConnectionCount();
	if (index < 0 || index >= count)
	{
		ctx.log(RC_LOG_ERROR, "Get off-mesh connection: invalid index.");
		return to_return;
	}

	const float* verts = geom->getOffMeshConnectionVerts();
	const float* rads = geom->getOffMeshConnectionRads();
	const unsigned char* dirs = geom->getOffMeshConnectionDirs();
	const unsigned char* areas = geom->getOffMeshConnectionAreas();
	const unsigned short* flags = geom->getOffMeshConnectionFlags();

	std::vector<float> start_pos = {verts[index * 6], verts[index * 6 + 1], verts[index * 6 + 2]};
	std::vector<float> end_pos = {verts[index * 6 + 3], verts[index * 6 + 4], verts[index * 6 + 5]};

	to_return["start"] = start_pos;
	to_return["end"] = end_pos;
	to_return["radius"] = std::vector<float>{rads[index]};
	to_return["bidirectional"] = std::vector<float>{(float)dirs[index]};
	to_return["area"] = std::vector<float>{(float)areas[index]};
	to_return["flags"] = std::vector<float>{(float)flags[index]};

	return to_return;
}

std::vector<std::map<std::string, std::vector<float>>> Navmesh::get_all_offmesh_connections()
{
	std::vector<std::map<std::string, std::vector<float>>> to_return;

	if (!is_init)
	{
		ctx.log(RC_LOG_ERROR, "Get all off-mesh connections: geometry is not initialized.");
		return to_return;
	}

	int count = geom->getOffMeshConnectionCount();
	for (int i = 0; i < count; i++)
	{
		to_return.push_back(get_offmesh_connection(i));
	}

	return to_return;
}

// ============================================================================
// AUTO-MARKUP SYSTEM IMPLEMENTATION
// ============================================================================

void Navmesh::mark_walkable_triangles(float walkable_slope_angle)
{
	if (!is_init)
	{
		ctx.log(RC_LOG_ERROR, "Mark walkable triangles: geometry is not initialized.");
		return;
	}

	// This functionality would require access to rcContext and heightfield during build
	// For now, we log that this should be set via build settings
	ctx.log(RC_LOG_WARNING, "Mark walkable triangles: use set_settings with 'agentMaxSlope' instead.");

	std::map<std::string, float> settings = get_settings();
	settings["agentMaxSlope"] = walkable_slope_angle;
	set_settings(settings);
}

void Navmesh::mark_box_area(std::vector<float> bmin, std::vector<float> bmax, unsigned char area_id)
{
	if (!is_init)
	{
		ctx.log(RC_LOG_ERROR, "Mark box area: geometry is not initialized.");
		return;
	}

	if (bmin.size() != 3 || bmax.size() != 3)
	{
		ctx.log(RC_LOG_ERROR, "Mark box area: invalid bounds (must have 3 elements each).");
		return;
	}

	// Create a box convex volume
	std::vector<float> verts = {
		bmin[0], bmin[1], bmin[2],
		bmax[0], bmin[1], bmin[2],
		bmax[0], bmin[1], bmax[2],
		bmin[0], bmin[1], bmax[2]
	};

	add_convex_volume(verts, bmin[1], bmax[1], area_id);
}

void Navmesh::mark_cylinder_area(std::vector<float> pos, float radius, float height, unsigned char area_id)
{
	if (!is_init)
	{
		ctx.log(RC_LOG_ERROR, "Mark cylinder area: geometry is not initialized.");
		return;
	}

	if (pos.size() != 3)
	{
		ctx.log(RC_LOG_ERROR, "Mark cylinder area: invalid position (must have 3 elements).");
		return;
	}

	// Approximate cylinder with octagon
	const int segments = 8;
	std::vector<float> verts;
	for (int i = 0; i < segments; i++)
	{
		float angle = (float)i / (float)segments * 3.14159f * 2.0f;
		verts.push_back(pos[0] + cosf(angle) * radius);
		verts.push_back(pos[1]);
		verts.push_back(pos[2] + sinf(angle) * radius);
	}

	add_convex_volume(verts, pos[1], pos[1] + height, area_id);
}

void Navmesh::mark_convex_poly_area(std::vector<float> verts, float hmin, float hmax, unsigned char area_id)
{
	add_convex_volume(verts, hmin, hmax, area_id);
}

void Navmesh::erode_walkable_area(int radius)
{
	if (!is_init)
	{
		ctx.log(RC_LOG_ERROR, "Erode walkable area: geometry is not initialized.");
		return;
	}

	// This would require access to the compactheightfield during build
	// Store as a setting to apply during build
	ctx.log(RC_LOG_WARNING, "Erode walkable area: this should be applied during navmesh build process.");
}

void Navmesh::median_filter_walkable_area()
{
	if (!is_init)
	{
		ctx.log(RC_LOG_ERROR, "Median filter walkable area: geometry is not initialized.");
		return;
	}

	// This would require access to the compactheightfield during build
	ctx.log(RC_LOG_WARNING, "Median filter walkable area: this should be applied during navmesh build process.");
}

// ============================================================================
// FORMATIONS & GROUP BEHAVIORS
// ============================================================================

int Navmesh::create_formation(int formation_type, float spacing)
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Create formation: crowd is not initialized.");
		return -1;
	}

	Formation formation;
	formation.id = next_formation_id++;
	formation.type = formation_type;
	formation.spacing = spacing;
	formation.leader_idx = -1;
	formation.has_target = false;
	formation.target_pos[0] = formation.target_pos[1] = formation.target_pos[2] = 0.0f;
	formation.target_dir[0] = 0.0f;
	formation.target_dir[1] = 0.0f;
	formation.target_dir[2] = 1.0f;  // Default forward direction

	formations[formation.id] = formation;

	ctx.log(RC_LOG_PROGRESS, "Created formation %d with type %d and spacing %.2f",
	        formation.id, formation_type, spacing);

	return formation.id;
}

void Navmesh::delete_formation(int formation_id)
{
	if (formations.find(formation_id) == formations.end())
	{
		ctx.log(RC_LOG_ERROR, "Delete formation: formation %d not found.", formation_id);
		return;
	}

	// Remove all agents from formation
	Formation& formation = formations[formation_id];
	for (int agent_idx : formation.agent_indices)
	{
		// Just remove them from the formation, don't remove from crowd
	}

	formations.erase(formation_id);
	ctx.log(RC_LOG_PROGRESS, "Deleted formation %d", formation_id);
}

bool Navmesh::add_agent_to_formation(int formation_id, int agent_idx)
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Add agent to formation: crowd is not initialized.");
		return false;
	}

	if (formations.find(formation_id) == formations.end())
	{
		ctx.log(RC_LOG_ERROR, "Add agent to formation: formation %d not found.", formation_id);
		return false;
	}

	if (agent_idx < 0 || agent_idx >= crowd->getAgentCount())
	{
		ctx.log(RC_LOG_ERROR, "Add agent to formation: invalid agent index %d.", agent_idx);
		return false;
	}

	Formation& formation = formations[formation_id];

	// Check if agent already in this formation
	if (std::find(formation.agent_indices.begin(), formation.agent_indices.end(), agent_idx) != formation.agent_indices.end())
	{
		ctx.log(RC_LOG_WARNING, "Agent %d already in formation %d.", agent_idx, formation_id);
		return true;
	}

	formation.agent_indices.push_back(agent_idx);

	ctx.log(RC_LOG_PROGRESS, "Added agent %d to formation %d", agent_idx, formation_id);
	return true;
}

bool Navmesh::remove_agent_from_formation(int agent_idx)
{
	if (!is_crowd_init)
	{
		ctx.log(RC_LOG_ERROR, "Remove agent from formation: crowd is not initialized.");
		return false;
	}

	// Find which formation this agent belongs to
	for (auto& pair : formations)
	{
		Formation& formation = pair.second;
		auto it = std::find(formation.agent_indices.begin(), formation.agent_indices.end(), agent_idx);
		if (it != formation.agent_indices.end())
		{
			formation.agent_indices.erase(it);

			// If this was the leader, clear leader
			if (formation.leader_idx == agent_idx)
			{
				formation.leader_idx = -1;
			}

			ctx.log(RC_LOG_PROGRESS, "Removed agent %d from formation %d", agent_idx, formation.id);
			return true;
		}
	}

	ctx.log(RC_LOG_WARNING, "Agent %d not found in any formation.", agent_idx);
	return false;
}

void Navmesh::set_formation_target(int formation_id, std::vector<float> target_pos, std::vector<float> target_dir)
{
	if (formations.find(formation_id) == formations.end())
	{
		ctx.log(RC_LOG_ERROR, "Set formation target: formation %d not found.", formation_id);
		return;
	}

	if (target_pos.size() < 3)
	{
		ctx.log(RC_LOG_ERROR, "Set formation target: target_pos must have 3 components.");
		return;
	}

	if (target_dir.size() < 3)
	{
		ctx.log(RC_LOG_ERROR, "Set formation target: target_dir must have 3 components.");
		return;
	}

	Formation& formation = formations[formation_id];
	formation.has_target = true;
	formation.target_pos[0] = target_pos[0];
	formation.target_pos[1] = target_pos[1];
	formation.target_pos[2] = target_pos[2];

	// Normalize direction
	float len = sqrtf(target_dir[0]*target_dir[0] + target_dir[1]*target_dir[1] + target_dir[2]*target_dir[2]);
	if (len > 0.001f)
	{
		formation.target_dir[0] = target_dir[0] / len;
		formation.target_dir[1] = target_dir[1] / len;
		formation.target_dir[2] = target_dir[2] / len;
	}
	else
	{
		formation.target_dir[0] = 0.0f;
		formation.target_dir[1] = 0.0f;
		formation.target_dir[2] = 1.0f;
	}

	ctx.log(RC_LOG_PROGRESS, "Set formation %d target to (%.2f, %.2f, %.2f)",
	        formation_id, target_pos[0], target_pos[1], target_pos[2]);
}

void Navmesh::set_formation_leader(int formation_id, int agent_idx)
{
	if (formations.find(formation_id) == formations.end())
	{
		ctx.log(RC_LOG_ERROR, "Set formation leader: formation %d not found.", formation_id);
		return;
	}

	Formation& formation = formations[formation_id];

	// Check if agent is in this formation
	if (std::find(formation.agent_indices.begin(), formation.agent_indices.end(), agent_idx) == formation.agent_indices.end())
	{
		ctx.log(RC_LOG_ERROR, "Set formation leader: agent %d not in formation %d.", agent_idx, formation_id);
		return;
	}

	formation.leader_idx = agent_idx;
	ctx.log(RC_LOG_PROGRESS, "Set agent %d as leader of formation %d", agent_idx, formation_id);
}

std::vector<int> Navmesh::get_formation_agents(int formation_id)
{
	if (formations.find(formation_id) == formations.end())
	{
		ctx.log(RC_LOG_ERROR, "Get formation agents: formation %d not found.", formation_id);
		return std::vector<int>();
	}

	return formations[formation_id].agent_indices;
}

std::map<std::string, float> Navmesh::get_formation_info(int formation_id)
{
	std::map<std::string, float> info;

	if (formations.find(formation_id) == formations.end())
	{
		ctx.log(RC_LOG_ERROR, "Get formation info: formation %d not found.", formation_id);
		return info;
	}

	Formation& formation = formations[formation_id];

	info["id"] = (float)formation.id;
	info["type"] = (float)formation.type;
	info["spacing"] = formation.spacing;
	info["leader_idx"] = (float)formation.leader_idx;
	info["agent_count"] = (float)formation.agent_indices.size();
	info["has_target"] = formation.has_target ? 1.0f : 0.0f;
	info["target_x"] = formation.target_pos[0];
	info["target_y"] = formation.target_pos[1];
	info["target_z"] = formation.target_pos[2];
	info["dir_x"] = formation.target_dir[0];
	info["dir_y"] = formation.target_dir[1];
	info["dir_z"] = formation.target_dir[2];

	return info;
}

void Navmesh::update_formations(float dt)
{
	if (!is_crowd_init)
	{
		return;
	}

	for (auto& pair : formations)
	{
		Formation& formation = pair.second;

		if (!formation.has_target || formation.agent_indices.empty())
		{
			continue;
		}

		// Calculate formation positions based on type
		const float* center = formation.target_pos;
		const float* dir = formation.target_dir;

		// Right vector (perpendicular to direction)
		float right[3];
		right[0] = dir[2];
		right[1] = 0.0f;
		right[2] = -dir[0];

		// Normalize right vector
		float right_len = sqrtf(right[0]*right[0] + right[2]*right[2]);
		if (right_len > 0.001f)
		{
			right[0] /= right_len;
			right[2] /= right_len;
		}

		int num_agents = (int)formation.agent_indices.size();

		for (int i = 0; i < num_agents; i++)
		{
			int agent_idx = formation.agent_indices[i];
			if (agent_idx < 0 || agent_idx >= crowd->getAgentCount())
			{
				continue;
			}

			float offset_x = 0.0f;
			float offset_z = 0.0f;

			switch (formation.type)
			{
				case 0: // Line formation
				{
					int center_idx = num_agents / 2;
					offset_x = (i - center_idx) * formation.spacing * right[0];
					offset_z = (i - center_idx) * formation.spacing * right[2];
					break;
				}

				case 1: // Column formation
				{
					offset_x = -i * formation.spacing * dir[0];
					offset_z = -i * formation.spacing * dir[2];
					break;
				}

				case 2: // Wedge formation
				{
					int row = (int)sqrtf((float)i);
					int col = i - row * row;
					offset_x = (col - row * 0.5f) * formation.spacing * right[0] - row * formation.spacing * dir[0];
					offset_z = (col - row * 0.5f) * formation.spacing * right[2] - row * formation.spacing * dir[2];
					break;
				}

				case 3: // Box formation
				{
					int side_len = (int)ceil(sqrtf((float)num_agents));
					int row = i / side_len;
					int col = i % side_len;
					offset_x = (col - side_len * 0.5f) * formation.spacing * right[0] - row * formation.spacing * dir[0];
					offset_z = (col - side_len * 0.5f) * formation.spacing * right[2] - row * formation.spacing * dir[2];
					break;
				}

				case 4: // Circle formation
				{
					float angle = (float)i / (float)num_agents * 2.0f * 3.14159f;
					float radius = formation.spacing * num_agents / (2.0f * 3.14159f);
					offset_x = radius * cosf(angle) * right[0] + radius * sinf(angle) * dir[0];
					offset_z = radius * cosf(angle) * right[2] + radius * sinf(angle) * dir[2];
					break;
				}
			}

			// Set agent target to formation position
			float target[3];
			target[0] = center[0] + offset_x;
			target[1] = center[1];
			target[2] = center[2] + offset_z;

			const dtCrowdAgent* ag = crowd->getAgent(agent_idx);
			if (ag && ag->active)
			{
				crowd->requestMoveTarget(agent_idx, 0, target);
			}
		}
	}
}

int Navmesh::get_formation_count()
{
	return (int)formations.size();
}

#ifdef _MAIN_APP
void main() {
	Navmesh* navmesh = new Navmesh();
	navmesh->init_by_obj("disc.obj");
	std::map<std::string, float> settings = navmesh->get_settings();
	settings["vertsPerPoly"] = 12;
	settings["cellSize"] = 0.1;

	navmesh->set_settings(settings);
	navmesh->build_navmesh();

	std::tuple<std::vector<float>, std::vector<int>, std::vector<int>> mesh = navmesh->get_navmesh_polygonization();

	std::string verts_str = "vertices: ";
	std::vector<float> vertices = std::get<0>(mesh);
	for (size_t i = 0; i < vertices.size(); i++) {
		verts_str += std::to_string(vertices[i]) + ", ";
	}
	//std::cout << verts_str << std::endl;

	std::string polys_str = "polygons: ";
	std::vector<int> polygons = std::get<1>(mesh);
	for (size_t i = 0; i < polygons.size(); i++) {
		polys_str += std::to_string(polygons[i]) + ", ";
	}
	//std::cout << polys_str << std::endl;

	std::string sizes_str = "sizes: ";
	std::vector<int> sizes = std::get<2>(mesh);
	for (size_t i = 0; i < sizes.size(); i++) {
		sizes_str += std::to_string(sizes[i]) + ", ";
	}
	std::cout << sizes_str << std::endl;
}
#endif // _MAIN_APP