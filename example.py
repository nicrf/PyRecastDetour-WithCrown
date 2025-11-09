#!/usr/bin/env python3
"""
PyRecastDetour - Exemples d'utilisation
"""

from PyRecastDetour import (
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
    Exemple 1: Pathfinding basique
    Trouve un chemin entre deux points
    """
    print("\n" + "="*60)
    print("EXEMPLE 1: Pathfinding Basique")
    print("="*60)

    # Créer navmesh
    navmesh = Navmesh()

    # Charger géométrie (remplacer par votre fichier .obj)
    # navmesh.init_by_obj("level.obj")

    # Alternative: créer une géométrie simple (plan)
    vertices = [
        0, 0, 0,    100, 0, 0,    100, 0, 100,   0, 0, 100
    ]
    faces = [0, 1, 2,  0, 2, 3]
    navmesh.init_by_raw(vertices, faces)

    # Construire navmesh
    navmesh.build_navmesh()

    # Vérifier le log
    log = navmesh.get_log()
    if log:
        print(f"Build log:\n{log}")

    # Trouver un chemin
    start = [10.0, 0.0, 10.0]
    end = [90.0, 0.0, 90.0]

    print(f"\nFinding path from {start} to {end}...")
    path = navmesh.pathfind_straight(start, end)

    if path:
        print(f"Path found with {len(path)//3} points:")
        for i in range(0, min(len(path), 15), 3):  # Afficher max 5 points
            print(f"  Point {i//3}: ({path[i]:.2f}, {path[i+1]:.2f}, {path[i+2]:.2f})")
        if len(path) > 15:
            print(f"  ... ({len(path)//3 - 5} more points)")
    else:
        print("No path found!")


def example_2_custom_settings():
    """
    Exemple 2: Configuration personnalisée
    Configure les paramètres du navmesh avant construction
    """
    print("\n" + "="*60)
    print("EXEMPLE 2: Configuration Personnalisée")
    print("="*60)

    navmesh = Navmesh()

    # Géométrie simple
    vertices = [
        0, 0, 0,    50, 0, 0,    50, 0, 50,   0, 0, 50
    ]
    faces = [0, 1, 2,  0, 2, 3]
    navmesh.init_by_raw(vertices, faces)

    # Récupérer settings par défaut
    settings = navmesh.get_settings()
    print("\nDefault settings:")
    for key, value in sorted(settings.items()):
        print(f"  {key}: {value}")

    # Personnaliser pour petit agent
    custom_settings = {
        "cellSize": 0.2,           # Plus haute résolution
        "cellHeight": 0.1,
        "agentHeight": 1.0,        # Agent de 1m de haut
        "agentRadius": 0.3,        # Rayon de 30cm
        "agentMaxClimb": 0.3,      # Peut monter 30cm
        "agentMaxSlope": 45.0      # Pentes jusqu'à 45°
    }

    print("\nApplying custom settings...")
    navmesh.set_settings(custom_settings)
    navmesh.build_navmesh()

    # Vérifier settings appliqués
    new_settings = navmesh.get_settings()
    print("\nUpdated settings:")
    print(f"  Agent height: {new_settings['agentHeight']}")
    print(f"  Agent radius: {new_settings['agentRadius']}")
    print(f"  Cell size: {new_settings['cellSize']}")

    # Obtenir bounding box
    bbox = navmesh.get_bounding_box()
    print(f"\nBounding box:")
    print(f"  Min: ({bbox[0]:.2f}, {bbox[1]:.2f}, {bbox[2]:.2f})")
    print(f"  Max: ({bbox[3]:.2f}, {bbox[4]:.2f}, {bbox[5]:.2f})")


def example_3_crowd_simulation():
    """
    Exemple 3: Simulation de foule
    Crée plusieurs agents et les fait naviguer
    """
    print("\n" + "="*60)
    print("EXEMPLE 3: Simulation de Foule")
    print("="*60)

    navmesh = Navmesh()

    # Créer un grand terrain
    vertices = [
        0, 0, 0,    100, 0, 0,    100, 0, 100,   0, 0, 100
    ]
    faces = [0, 1, 2,  0, 2, 3]
    navmesh.init_by_raw(vertices, faces)
    navmesh.build_navmesh()

    # Initialiser crowd
    print("\nInitializing crowd manager...")
    if not navmesh.init_crowd(maxAgents=50, maxAgentRadius=1.0):
        print("ERROR: Failed to initialize crowd")
        print(navmesh.get_log())
        return

    # Créer agents avec paramètres différents
    agents = []
    print("\nCreating agents...")

    for i in range(5):
        params = create_default_agent_params()
        params["radius"] = 0.5
        params["height"] = 2.0
        params["maxSpeed"] = 3.0 + i * 0.5  # Vitesses variées
        params["maxAcceleration"] = 8.0

        # Position de départ en ligne
        start_pos = [10.0 + i * 3.0, 0.0, 10.0]

        agent_id = navmesh.add_agent(start_pos, params)
        if agent_id >= 0:
            agents.append(agent_id)
            print(f"  Agent {agent_id} created at {start_pos}")

            # Définir cible
            target = [90.0, 0.0, 90.0]
            navmesh.set_agent_target(agent_id, target)
        else:
            print(f"  Failed to create agent {i}")

    # Simuler pendant quelques secondes
    print(f"\nSimulating {len(agents)} agents for 5 seconds...")
    print("(Update interval: 0.1s)\n")

    dt = 0.016  # 60 FPS
    frames = 0
    display_interval = 60  # Afficher tous les 60 frames (1 seconde)

    for _ in range(300):  # 5 secondes à 60 FPS
        navmesh.update_crowd(dt)
        frames += 1

        # Afficher état tous les 60 frames
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
    Exemple 4: Gestion dynamique d'agents
    Ajoute/retire des agents pendant la simulation
    """
    print("\n" + "="*60)
    print("EXEMPLE 4: Gestion Dynamique d'Agents")
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

    # Ajouter quelques agents initiaux
    print("\nAdding initial agents...")
    for i in range(3):
        params = create_default_agent_params()
        agent_id = navmesh.add_agent([20.0 + i*5, 0, 20.0], params)
        agents.append(agent_id)
        navmesh.set_agent_target(agent_id, [80, 0, 80])
        print(f"  Added agent {agent_id}")

    # Simuler
    for frame in range(120):
        navmesh.update_crowd(0.016)

        # Ajouter un agent toutes les 30 frames
        if frame % 30 == 0 and frame > 0:
            params = create_default_agent_params()
            new_agent = navmesh.add_agent([10, 0, 10], params)
            if new_agent >= 0:
                agents.append(new_agent)
                navmesh.set_agent_target(new_agent, [90, 0, 90])
                print(f"Frame {frame}: Added agent {new_agent}")

        # Retirer le premier agent à mi-simulation
        if frame == 60 and agents:
            removed = agents.pop(0)
            navmesh.remove_agent(removed)
            print(f"Frame {frame}: Removed agent {removed}")

        time.sleep(0.016)

    # État final
    print(f"\nFinal agent count: {navmesh.get_agent_count()}")
    print(f"Active agents: {agents}")


def example_5_agent_parameters():
    """
    Exemple 5: Modification des paramètres d'agent
    Change les paramètres d'un agent pendant la simulation
    """
    print("\n" + "="*60)
    print("EXEMPLE 5: Modification des Paramètres")
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

    # Créer agent
    params = create_default_agent_params()
    params["maxSpeed"] = 2.0
    agent_id = navmesh.add_agent([10, 0, 10], params)
    navmesh.set_agent_target(agent_id, [90, 0, 90])

    print(f"\nAgent {agent_id} created with maxSpeed=2.0")

    # Simuler 2 secondes
    print("Simulating for 2 seconds...")
    for _ in range(120):
        navmesh.update_crowd(0.016)
        time.sleep(0.016)

    state = navmesh.get_agent_state(agent_id)
    pos1 = navmesh.get_agent_position(agent_id)
    print(f"Position after 2s: ({pos1[0]:.1f}, {pos1[2]:.1f})")
    print(f"Max speed: {state['maxSpeed']:.1f}")

    # Augmenter la vitesse
    print("\nIncreasing speed to 10.0...")
    navmesh.update_agent_parameters(agent_id, {
        "maxSpeed": 10.0,
        "maxAcceleration": 20.0
    })

    # Simuler 2 secondes de plus
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
    Exemple 6: Sauvegarde et chargement
    Sauvegarde le navmesh construit et le recharge
    """
    print("\n" + "="*60)
    print("EXEMPLE 6: Sauvegarde et Chargement")
    print("="*60)

    # Construire et sauvegarder
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

    # Créer nouveau navmesh et charger
    print(f"\nLoading from {filename}...")
    navmesh2 = Navmesh()
    navmesh2.init_by_raw(vertices, faces)  # Géométrie nécessaire
    navmesh2.load_navmesh(filename)
    print("Loaded successfully!")

    # Tester pathfinding
    path = navmesh2.pathfind_straight([5, 0, 5], [45, 0, 45])
    print(f"Path from loaded navmesh: {len(path)//3} points")

    import os
    if os.path.exists(filename):
        os.remove(filename)
        print(f"\nCleaned up {filename}")


def example_7_spatial_queries():
    """
    Exemple 7: Requêtes spatiales
    Raycast, distance au mur, etc.
    """
    print("\n" + "="*60)
    print("EXEMPLE 7: Requêtes Spatiales")
    print("="*60)

    navmesh = Navmesh()
    vertices = [
        0, 0, 0,    50, 0, 0,    50, 0, 50,   0, 0, 50
    ]
    faces = [0, 1, 2,  0, 2, 3]
    navmesh.init_by_raw(vertices, faces)
    navmesh.build_navmesh()

    # Raycast à travers le navmesh
    print("\nRaycast test:")
    start = [5, 0, 5]
    end = [45, 0, 5]
    hit = navmesh.raycast(start, end)
    print(f"  Ray from {start} to {end}")
    print(f"  Hit point: {hit}")

    # Distance au mur
    print("\nDistance to wall:")
    points = [
        [25, 0, 25],  # Centre
        [5, 0, 25],   # Près du bord gauche
        [45, 0, 25]   # Près du bord droit
    ]
    for point in points:
        dist = navmesh.distance_to_wall(point)
        print(f"  At {point}: {dist:.2f} units to wall")

    # Hit mesh (géométrie originale)
    print("\nMesh intersection test:")
    mesh_hit = navmesh.hit_mesh([25, 10, 25], [25, -10, 25])
    print(f"  Ray intersects mesh at: {mesh_hit}")


def main():
    """
    Fonction principale - exécute tous les exemples
    """
    print("\n" + "="*60)
    print("PyRecastDetour - Exemples d'Utilisation")
    print("="*60)
    print("\nCes exemples démontrent les fonctionnalités principales.")
    print("Certains nécessitent des fichiers .obj - modifiez le code si nécessaire.")

    try:
        # Exemples rapides (pas de sleep)
        example_1_basic_pathfinding()
        example_2_custom_settings()
        example_6_save_load()
        example_7_spatial_queries()

        # Exemples avec simulation (commentés par défaut car ils prennent du temps)
        # Décommentez pour les exécuter:

        # example_3_crowd_simulation()
        # example_4_dynamic_agents()
        # example_5_agent_parameters()

        print("\n" + "="*60)
        print("Tous les exemples terminés avec succès!")
        print("="*60)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
