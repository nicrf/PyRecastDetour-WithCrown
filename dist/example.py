#!/usr/bin/env python3
"""
PyRecastDetour - Usage Examples
"""

from Py37RecastDetour import (
    Navmesh,
    create_default_agent_params,
    CROWD_ANTICIPATE_TURNS,
    CROWD_OBSTACLE_AVOIDANCE,
    CROWD_OPTIMIZE_VIS,
    CROWD_OPTIMIZE_TOPO,
    CROWDAGENT_TARGET_VALID
)
import time


def example_1_basic_pathfinding():
    """
    Example 1: Basic Pathfinding
    Finds a path between two points
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Pathfinding")
    print("="*60)

    # Create navmesh
    navmesh = Navmesh()

    # Load geometry (replace with your .obj file)
    # navmesh.init_by_obj("level.obj")

    # Alternative: create simple geometry (plane)
    vertices = [
        0, 0, 0,    100, 0, 0,    100, 0, 100,   0, 0, 100
    ]
    faces = [0, 1, 2,  0, 2, 3]
    navmesh.init_by_raw(vertices, faces)

    # Build navmesh
    navmesh.build_navmesh()

    # Check log
    log = navmesh.get_log()
    if log:
        print(f"Build log:\n{log}")

    # Find a path
    start = [10.0, 0.0, 10.0]
    end = [90.0, 0.0, 90.0]

    print(f"\nFinding path from {start} to {end}...")
    path = navmesh.pathfind_straight(start, end)

    if path:
        print(f"Path found with {len(path)//3} points:")
        for i in range(0, min(len(path), 15), 3):  # Display max 5 points
            print(f"  Point {i//3}: ({path[i]:.2f}, {path[i+1]:.2f}, {path[i+2]:.2f})")
        if len(path) > 15:
            print(f"  ... ({len(path)//3 - 5} more points)")
    else:
        print("No path found!")


def example_2_custom_settings():
    """
    Example 2: Custom Configuration
    Configures navmesh parameters before building
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Custom Configuration")
    print("="*60)

    navmesh = Navmesh()

    # Simple geometry
    vertices = [
        0, 0, 0,    50, 0, 0,    50, 0, 50,   0, 0, 50
    ]
    faces = [0, 1, 2,  0, 2, 3]
    navmesh.init_by_raw(vertices, faces)

    # Get default settings
    settings = navmesh.get_settings()
    print("\nDefault settings:")
    for key, value in sorted(settings.items()):
        print(f"  {key}: {value}")

    # Customize for small agent
    custom_settings = {
        "cellSize": 0.2,           # Higher resolution
        "cellHeight": 0.1,
        "agentHeight": 1.0,        # 1m tall agent
        "agentRadius": 0.3,        # 30cm radius
        "agentMaxClimb": 0.3,      # Can climb 30cm
        "agentMaxSlope": 45.0      # Slopes up to 45°
    }

    print("\nApplying custom settings...")
    navmesh.set_settings(custom_settings)
    navmesh.build_navmesh()

    # Check applied settings
    new_settings = navmesh.get_settings()
    print("\nUpdated settings:")
    print(f"  Agent height: {new_settings['agentHeight']}")
    print(f"  Agent radius: {new_settings['agentRadius']}")
    print(f"  Cell size: {new_settings['cellSize']}")

    # Get bounding box
    bbox = navmesh.get_bounding_box()
    print(f"\nBounding box:")
    print(f"  Min: ({bbox[0]:.2f}, {bbox[1]:.2f}, {bbox[2]:.2f})")
    print(f"  Max: ({bbox[3]:.2f}, {bbox[4]:.2f}, {bbox[5]:.2f})")


def example_3_crowd_simulation():
    """
    Example 3: Crowd Simulation
    Creates multiple agents and makes them navigate
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Crowd Simulation")
    print("="*60)

    navmesh = Navmesh()

    # Create large terrain
    vertices = [
        0, 0, 0,    100, 0, 0,    100, 0, 100,   0, 0, 100
    ]
    faces = [0, 1, 2,  0, 2, 3]
    navmesh.init_by_raw(vertices, faces)
    navmesh.build_navmesh()

    # Initialize crowd
    print("\nInitializing crowd manager...")
    if not navmesh.init_crowd(maxAgents=50, maxAgentRadius=1.0):
        print("ERROR: Failed to initialize crowd")
        print(navmesh.get_log())
        return

    # Create agents with different parameters
    agents = []
    print("\nCreating agents...")

    for i in range(5):
        params = create_default_agent_params()
        params["radius"] = 0.5
        params["height"] = 2.0
        params["maxSpeed"] = 3.0 + i * 0.5  # Varied speeds
        params["maxAcceleration"] = 8.0

        # Starting position in a line
        start_pos = [10.0 + i * 3.0, 0.0, 10.0]

        agent_id = navmesh.add_agent(start_pos, params)
        if agent_id >= 0:
            agents.append(agent_id)
            print(f"  Agent {agent_id} created at {start_pos}")

            # Set target
            target = [90.0, 0.0, 90.0]
            navmesh.set_agent_target(agent_id, target)
        else:
            print(f"  Failed to create agent {i}")

    # Simulate for a few seconds
    print(f"\nSimulating {len(agents)} agents for 5 seconds...")
    print("(Update interval: 0.1s)\n")

    dt = 0.016  # 60 FPS
    frames = 0
    display_interval = 60  # Display every 60 frames (1 second)

    for _ in range(300):  # 5 seconds at 60 FPS
        navmesh.update_crowd(dt)
        frames += 1

        # Display state every 60 frames
        if frames % display_interval == 0:
            print(f"Frame {frames} (t={frames*dt:.1f}s):")
            for agent_id in agents:
                pos = navmesh.get_agent_position(agent_id)
                vel = navmesh.get_agent_velocity(agent_id)
                state = navmesh.get_agent_state(agent_id)

                speed = (vel[0]**2 + vel[1]**2 + vel[2]**2)**0.5
                target_state = int(state['targetState'])

                status = "VALID" if target_state == CROWDAGENT_TARGET_VALID else "OTHER"
                print(f"  Agent {agent_id}: pos=({pos[0]:.1f}, {pos[2]:.1f}) "
                      f"speed={speed:.2f} target={status}")
            print()

        time.sleep(dt)

    print("Simulation complete!")


def example_4_dynamic_agents():
    """
    Example 4: Dynamic Agent Management
    Adds/removes agents during simulation
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Dynamic Agent Management")
    print("="*60)

    navmesh = Navmesh()

    # Setup navmesh
    vertices = [
        0, 0, 0,    100, 0, 0,    100, 0, 100,   0, 0, 100
    ]
    faces = [0, 1, 2,  0, 2, 3]
    navmesh.init_by_raw(vertices, faces)
    navmesh.build_navmesh()
    navmesh.init_crowd(100, 1.0)

    agents = []

    # Add some initial agents
    print("\nAdding initial agents...")
    for i in range(3):
        params = create_default_agent_params()
        agent_id = navmesh.add_agent([20.0 + i*5, 0, 20.0], params)
        agents.append(agent_id)
        navmesh.set_agent_target(agent_id, [80, 0, 80])
        print(f"  Added agent {agent_id}")

    # Simulate
    for frame in range(120):
        navmesh.update_crowd(0.016)

        # Add an agent every 30 frames
        if frame % 30 == 0 and frame > 0:
            params = create_default_agent_params()
            new_agent = navmesh.add_agent([10, 0, 10], params)
            if new_agent >= 0:
                agents.append(new_agent)
                navmesh.set_agent_target(new_agent, [90, 0, 90])
                print(f"Frame {frame}: Added agent {new_agent}")

        # Remove first agent at mid-simulation
        if frame == 60 and agents:
            removed = agents.pop(0)
            navmesh.remove_agent(removed)
            print(f"Frame {frame}: Removed agent {removed}")

        time.sleep(0.016)

    # Final state
    print(f"\nFinal agent count: {navmesh.get_agent_count()}")
    print(f"Active agents: {agents}")


def example_5_agent_parameters():
    """
    Example 5: Modifying Agent Parameters
    Changes agent parameters during simulation
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Parameter Modification")
    print("="*60)

    navmesh = Navmesh()

    # Setup
    vertices = [
        0, 0, 0,    100, 0, 0,    100, 0, 100,   0, 0, 100
    ]
    faces = [0, 1, 2,  0, 2, 3]
    navmesh.init_by_raw(vertices, faces)
    navmesh.build_navmesh()
    navmesh.init_crowd(10, 1.0)

    # Create agent
    params = create_default_agent_params()
    params["maxSpeed"] = 2.0
    agent_id = navmesh.add_agent([10, 0, 10], params)
    navmesh.set_agent_target(agent_id, [90, 0, 90])

    print(f"\nAgent {agent_id} created with maxSpeed=2.0")

    # Simulate for 2 seconds
    print("Simulating for 2 seconds...")
    for _ in range(120):
        navmesh.update_crowd(0.016)
        time.sleep(0.016)

    state = navmesh.get_agent_state(agent_id)
    pos1 = navmesh.get_agent_position(agent_id)
    print(f"Position after 2s: ({pos1[0]:.1f}, {pos1[2]:.1f})")
    print(f"Max speed: {state['maxSpeed']:.1f}")

    # Increase speed
    print("\nIncreasing speed to 10.0...")
    navmesh.update_agent_parameters(agent_id, {
        "maxSpeed": 10.0,
        "maxAcceleration": 20.0
    })

    # Simulate for 2 more seconds
    print("Simulating for 2 more seconds...")
    for _ in range(120):
        navmesh.update_crowd(0.016)
        time.sleep(0.016)

    state = navmesh.get_agent_state(agent_id)
    pos2 = navmesh.get_agent_position(agent_id)
    print(f"Position after 4s: ({pos2[0]:.1f}, {pos2[2]:.1f})")
    print(f"Max speed: {state['maxSpeed']:.1f}")

    distance_moved = ((pos2[0]-pos1[0])**2 + (pos2[2]-pos1[2])**2)**0.5
    print(f"\nDistance moved in last 2s: {distance_moved:.1f} (faster!)")


def example_6_save_load():
    """
    Example 6: Save and Load
    Saves the built navmesh and reloads it
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: Save and Load")
    print("="*60)

    # Build and save
    print("\nBuilding navmesh...")
    navmesh = Navmesh()
    vertices = [
        0, 0, 0,    50, 0, 0,    50, 0, 50,   0, 0, 50
    ]
    faces = [0, 1, 2,  0, 2, 3]
    navmesh.init_by_raw(vertices, faces)
    navmesh.build_navmesh()

    filename = "test_navmesh.bin"
    print(f"Saving to {filename}...")
    navmesh.save_navmesh(filename)
    print("Saved successfully!")

    # Create new navmesh and load
    print(f"\nLoading from {filename}...")
    navmesh2 = Navmesh()
    navmesh2.init_by_raw(vertices, faces)  # Geometry needed
    navmesh2.load_navmesh(filename)
    print("Loaded successfully!")

    # Test pathfinding
    path = navmesh2.pathfind_straight([5, 0, 5], [45, 0, 45])
    print(f"Path from loaded navmesh: {len(path)//3} points")

    import os
    if os.path.exists(filename):
        os.remove(filename)
        print(f"\nCleaned up {filename}")


def example_7_spatial_queries():
    """
    Example 7: Spatial Queries
    Raycast, distance to wall, etc.
    """
    print("\n" + "="*60)
    print("EXAMPLE 7: Spatial Queries")
    print("="*60)

    navmesh = Navmesh()
    vertices = [
        0, 0, 0,    50, 0, 0,    50, 0, 50,   0, 0, 50
    ]
    faces = [0, 1, 2,  0, 2, 3]
    navmesh.init_by_raw(vertices, faces)
    navmesh.build_navmesh()

    # Raycast through navmesh
    print("\nRaycast test:")
    start = [5, 0, 5]
    end = [45, 0, 5]
    hit = navmesh.raycast(start, end)
    print(f"  Ray from {start} to {end}")
    print(f"  Hit point: {hit}")

    # Distance to wall
    print("\nDistance to wall:")
    points = [
        [25, 0, 25],  # Center
        [5, 0, 25],   # Near left edge
        [45, 0, 25]   # Near right edge
    ]
    for point in points:
        dist = navmesh.distance_to_wall(point)
        print(f"  At {point}: {dist:.2f} units to wall")

    # Hit mesh (original geometry)
    print("\nMesh intersection test:")
    mesh_hit = navmesh.hit_mesh([25, 10, 25], [25, -10, 25])
    print(f"  Ray intersects mesh at: {mesh_hit}")


def main():
    """
    Main function - runs all examples
    """
    print("\n" + "="*60)
    print("PyRecastDetour - Usage Examples")
    print("="*60)
    print("\nThese examples demonstrate the main features.")
    print("Some require .obj files - modify the code if necessary.")

    try:
        # Quick examples (no sleep)
        example_1_basic_pathfinding()
        example_2_custom_settings()
        example_6_save_load()
        example_7_spatial_queries()

        # Examples with simulation (commented by default as they take time)
        # Uncomment to run them:

        # example_3_crowd_simulation()
        # example_4_dynamic_agents()
        # example_5_agent_parameters()

        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
