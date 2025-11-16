#!/usr/bin/env python3
"""
Script de diagnostic pour tester le mouvement des agents
"""

from Py37RecastDetour import Navmesh, create_default_agent_params, CROWDAGENT_TARGET_VALID

print("="*60)
print("DIAGNOSTIC: Test de Mouvement des Agents")
print("="*60)

# Étape 1: Créer et construire le navmesh
print("\n[1/8] Construction du navmesh...")
navmesh = Navmesh()
vertices = [0, 0, 0,  100, 0, 0,  100, 0, 100,  0, 0, 100]
faces = [0, 1, 2,  0, 2, 3]

navmesh.init_by_raw(vertices, faces)
navmesh.build_navmesh()
log = navmesh.get_log()
if log:
    print(f"   Build log: {log}")
else:
    print("   ✓ Navmesh construit avec succès")

# Étape 2: Vérifier bounding box
print("\n[2/8] Vérification du bounding box...")
bbox = navmesh.get_bounding_box()
print(f"   Min: ({bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f})")
print(f"   Max: ({bbox[3]:.1f}, {bbox[4]:.1f}, {bbox[5]:.1f})")

# Étape 3: Initialiser le crowd
print("\n[3/8] Initialisation du crowd...")
success = navmesh.init_crowd(maxAgents=10, maxAgentRadius=1.0)
if not success:
    print("   ✗ ERREUR: init_crowd a échoué!")
    print(f"   Log: {navmesh.get_log()}")
    exit(1)
else:
    print("   ✓ Crowd initialisé avec succès")

# Étape 4: Créer un agent
print("\n[4/8] Création d'un agent...")
params = create_default_agent_params()
print(f"   Paramètres par défaut:")
print(f"     - radius: {params.get('radius', 'N/A')}")
print(f"     - height: {params.get('height', 'N/A')}")
print(f"     - maxSpeed: {params.get('maxSpeed', 'N/A')}")
print(f"     - maxAcceleration: {params.get('maxAcceleration', 'N/A')}")

start_pos = [50.0, 0.0, 50.0]
agent_id = navmesh.add_agent(start_pos, params)
if agent_id < 0:
    print(f"   ✗ ERREUR: Impossible de créer l'agent! ID={agent_id}")
    exit(1)
else:
    print(f"   ✓ Agent créé avec succès: ID={agent_id}")
    print(f"   Position de départ: {start_pos}")

# Étape 5: Définir une cible
print("\n[5/8] Définition de la cible...")
target_pos = [90.0, 0.0, 90.0]
result = navmesh.set_agent_target(agent_id, target_pos)
if not result:
    print("   ✗ ERREUR: Impossible de définir la cible!")
    exit(1)
else:
    print(f"   ✓ Cible définie: {target_pos}")

# Étape 6: Vérifier l'état initial
print("\n[6/8] État initial de l'agent...")
state = navmesh.get_agent_state(agent_id)
print(f"   Position: ({state['posX']:.2f}, {state['posY']:.2f}, {state['posZ']:.2f})")
print(f"   Velocity: ({state['velX']:.2f}, {state['velY']:.2f}, {state['velZ']:.2f})")
print(f"   Target State: {state['targetState']} (2=VALID)")
print(f"   Agent State: {state['state']} (1=WALKING)")
print(f"   Active: {state['active']}")
print(f"   Max Speed: {state['maxSpeed']:.2f}")
print(f"   Max Accel: {state['maxAcceleration']:.2f}")

# Étape 7: Vérifier les paramètres
print("\n[7/8] Vérification des paramètres critiques...")
errors = []
if state['maxSpeed'] <= 0:
    errors.append(f"maxSpeed est {state['maxSpeed']} (doit être > 0)")
if state['maxAcceleration'] <= 0:
    errors.append(f"maxAcceleration est {state['maxAcceleration']} (doit être > 0)")
if not state['active']:
    errors.append("Agent n'est pas actif")
if state['targetState'] != CROWDAGENT_TARGET_VALID:
    errors.append(f"Target state invalide: {state['targetState']} (devrait être {CROWDAGENT_TARGET_VALID})")

if errors:
    print("   ✗ ERREURS détectées:")
    for err in errors:
        print(f"     - {err}")
else:
    print("   ✓ Tous les paramètres sont corrects")

# Étape 8: Simuler le mouvement
print("\n[8/8] Simulation du mouvement (10 frames)...")
print("   Frame | Position (X, Z)  | Velocity (X, Z) | Speed | Target")
print("   " + "-"*70)

dt = 0.1  # 10 FPS pour mieux voir le mouvement
has_moved = False
initial_pos = navmesh.get_agent_position(agent_id)

for frame in range(10):
    # APPEL CRITIQUE: Sans ceci, les agents ne bougent PAS!
    navmesh.update_crowd(dt)

    pos = navmesh.get_agent_position(agent_id)
    vel = navmesh.get_agent_velocity(agent_id)
    state = navmesh.get_agent_state(agent_id)

    speed = (vel[0]**2 + vel[1]**2 + vel[2]**2)**0.5
    target_state = state['targetState']

    target_status = "VALID" if target_state == CROWDAGENT_TARGET_VALID else f"OTHER({target_state})"

    print(f"   {frame:5d} | ({pos[0]:6.2f}, {pos[2]:6.2f}) | ({vel[0]:6.2f}, {vel[2]:6.2f}) | {speed:5.2f} | {target_status}")

    # Vérifier si l'agent a bougé
    distance_moved = ((pos[0]-initial_pos[0])**2 + (pos[2]-initial_pos[2])**2)**0.5
    if distance_moved > 0.01:
        has_moved = True

# Résultat final
print("\n" + "="*60)
print("RÉSULTAT DU DIAGNOSTIC")
print("="*60)

final_pos = navmesh.get_agent_position(agent_id)
total_distance = ((final_pos[0]-initial_pos[0])**2 + (final_pos[2]-initial_pos[2])**2)**0.5

print(f"\nPosition initiale: ({initial_pos[0]:.2f}, {initial_pos[2]:.2f})")
print(f"Position finale:   ({final_pos[0]:.2f}, {final_pos[2]:.2f})")
print(f"Distance parcourue: {total_distance:.2f} unités")

if has_moved and total_distance > 0.1:
    print("\n✓ SUCCÈS: Les agents bougent correctement!")
    print("  Votre problème vient probablement de votre code de test.")
    print("  Vérifiez que vous appelez update_crowd(dt) dans une boucle.")
else:
    print("\n✗ ÉCHEC: Les agents ne bougent PAS!")
    print("  Problèmes possibles:")
    print("  1. Le module C++ n'est pas compilé correctement")
    print("  2. Les bibliothèques Recast/Detour ont un problème")
    print("  3. La méthode update_crowd() n'est pas implémentée")

print("\n" + "="*60)
