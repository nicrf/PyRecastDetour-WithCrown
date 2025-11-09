# PyRecastDetour - Python API Reference

Documentation complète de l'API Python pour PyRecastDetour.

## Table des matières

- [Installation](#installation)
- [Classe Navmesh](#classe-navmesh)
  - [Initialisation](#initialisation)
  - [Configuration](#configuration)
  - [Construction du Navmesh](#construction-du-navmesh)
  - [Pathfinding](#pathfinding)
  - [Gestion du Crowd](#gestion-du-crowd)
  - [Requêtes Spatiales](#requêtes-spatiales)
  - [Export/Import](#exportimport)
- [Constantes](#constantes)
- [Fonctions Utilitaires](#fonctions-utilitaires)
- [Exemples Complets](#exemples-complets)

---

## Installation

```bash
# Copier le dossier dist/ dans votre projet
cp -r dist/ votre_projet/PyRecastDetour

# Ou ajouter au PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/path/to/PyRecastDetour-Sources/dist
```

```python
from PyRecastDetour import Navmesh
```

---

## Classe Navmesh

La classe principale pour gérer la navigation mesh et la simulation de foule.

### Initialisation

#### `Navmesh()`
Constructeur de la classe Navmesh.

**Exemple:**
```python
navmesh = Navmesh()
```

#### `init_by_obj(file_path: str) -> None`
Initialise la géométrie à partir d'un fichier OBJ.

**Paramètres:**
- `file_path` (str): Chemin vers le fichier .obj

**Exemple:**
```python
navmesh.init_by_obj("level.obj")
```

#### `init_by_raw(vertices: list[float], faces: list[int]) -> None`
Initialise la géométrie à partir de données brutes.

**Paramètres:**
- `vertices` (list[float]): Liste de coordonnées de sommets [x1, y1, z1, x2, y2, z2, ...]
- `faces` (list[int]): Liste d'indices de triangles [i1, i2, i3, i4, i5, i6, ...]

**Exemple:**
```python
vertices = [0, 0, 0,  10, 0, 0,  10, 0, 10,  0, 0, 10]
faces = [0, 1, 2,  0, 2, 3]
navmesh.init_by_raw(vertices, faces)
```

---

### Configuration

#### `get_settings() -> dict[str, float]`
Récupère les paramètres de construction du navmesh.

**Retourne:** Dictionnaire avec les paramètres

**Exemple:**
```python
settings = navmesh.get_settings()
print(settings["cellSize"])  # 0.3
```

#### `set_settings(settings: dict[str, float]) -> None`
Définit les paramètres de construction du navmesh.

**Paramètres disponibles:**
- `cellSize` (float): Taille de cellule de voxelisation (défaut: 0.3)
- `cellHeight` (float): Hauteur de cellule (défaut: 0.2)
- `agentHeight` (float): Hauteur de l'agent (défaut: 2.0)
- `agentRadius` (float): Rayon de l'agent (défaut: 0.6)
- `agentMaxClimb` (float): Hauteur max montable (défaut: 0.9)
- `agentMaxSlope` (float): Pente max en degrés (défaut: 45.0)
- `regionMinSize` (float): Taille min de région (défaut: 8)
- `regionMergeSize` (float): Taille de fusion de région (défaut: 20)
- `edgeMaxLen` (float): Longueur max d'arête (défaut: 12.0)
- `edgeMaxError` (float): Erreur max d'arête (défaut: 1.3)
- `vertsPerPoly` (float): Sommets par polygone [3-6] (défaut: 6)
- `detailSampleDist` (float): Distance d'échantillonnage détail (défaut: 6.0)
- `detailSampleMaxError` (float): Erreur max détail (défaut: 1.0)

**Exemple:**
```python
settings = {
    "cellSize": 0.2,
    "agentHeight": 1.8,
    "agentRadius": 0.4
}
navmesh.set_settings(settings)
```

#### `get_partition_type() -> int`
Récupère le type de partitionnement utilisé.

**Retourne:** 0 (WATERSHED), 1 (MONOTONE), ou 2 (LAYERS)

#### `set_partition_type(type: int) -> None`
Définit le type de partitionnement.

**Paramètres:**
- `type` (int): 0=WATERSHED (défaut), 1=MONOTONE, 2=LAYERS

---

### Construction du Navmesh

#### `build_navmesh() -> None`
Construit le navigation mesh à partir de la géométrie et des paramètres.

**Exemple:**
```python
navmesh.build_navmesh()
log = navmesh.get_log()
if "error" in log.lower():
    print("Erreur:", log)
```

#### `get_log() -> str`
Récupère les messages de log de construction et les efface.

**Retourne:** String contenant les logs

**Exemple:**
```python
log = navmesh.get_log()
print(log)
```

#### `get_bounding_box() -> list[float]`
Récupère la boîte englobante de la géométrie.

**Retourne:** [min_x, min_y, min_z, max_x, max_y, max_z]

**Exemple:**
```python
bbox = navmesh.get_bounding_box()
print(f"Bounds: {bbox[0:3]} to {bbox[3:6]}")
```

---

### Pathfinding

#### `pathfind_straight(start: list[float], end: list[float], vertex_mode: int = 0) -> list[float]`
Trouve le chemin le plus court entre deux points.

**Paramètres:**
- `start` (list[float]): Position de départ [x, y, z]
- `end` (list[float]): Position d'arrivée [x, y, z]
- `vertex_mode` (int): Mode de génération de sommets (0 par défaut)

**Retourne:** Liste de coordonnées [x1, y1, z1, x2, y2, z2, ...]

**Exemple:**
```python
path = navmesh.pathfind_straight([0, 0, 0], [10, 0, 10])
# path = [0, 0, 0, 5, 0, 5, 10, 0, 10]
for i in range(0, len(path), 3):
    print(f"Point: ({path[i]}, {path[i+1]}, {path[i+2]})")
```

#### `pathfind_straight_batch(coordinates: list[float], vertex_mode: int = 0) -> list[float]`
Trouve plusieurs chemins en une seule fois.

**Paramètres:**
- `coordinates` (list[float]): [start1_x, y, z, end1_x, y, z, start2_x, y, z, end2_x, y, z, ...]
- `vertex_mode` (int): Mode de génération de sommets

**Retourne:** [nb_points1, points1..., nb_points2, points2..., ...]

**Exemple:**
```python
coords = [0, 0, 0, 10, 0, 10,  5, 0, 5, 15, 0, 15]
results = navmesh.pathfind_straight_batch(coords)
```

#### `raycast(start: list[float], end: list[float]) -> list[float]`
Lance un rayon à travers le navmesh.

**Paramètres:**
- `start` (list[float]): Point de départ [x, y, z]
- `end` (list[float]): Point d'arrivée [x, y, z]

**Retourne:** Point d'impact ou point final

**Exemple:**
```python
hit = navmesh.raycast([0, 1, 0], [10, 1, 0])
```

#### `distance_to_wall(point: list[float]) -> float`
Calcule la distance au mur le plus proche.

**Paramètres:**
- `point` (list[float]): Position [x, y, z]

**Retourne:** Distance en unités

**Exemple:**
```python
dist = navmesh.distance_to_wall([5, 0, 5])
print(f"Distance to wall: {dist}")
```

#### `hit_mesh(start: list[float], end: list[float]) -> list[float]`
Intersecte un rayon avec la géométrie d'entrée.

**Paramètres:**
- `start` (list[float]): Point de départ [x, y, z]
- `end` (list[float]): Point d'arrivée [x, y, z]

**Retourne:** Point d'intersection [x, y, z]

---

### Gestion du Crowd

#### `init_crowd(maxAgents: int, maxAgentRadius: float) -> bool`
Initialise le système de gestion de foule.

**Paramètres:**
- `maxAgents` (int): Nombre maximum d'agents
- `maxAgentRadius` (float): Rayon maximum d'un agent

**Retourne:** True si succès, False sinon

**Exemple:**
```python
if navmesh.init_crowd(100, 1.0):
    print("Crowd initialized")
else:
    print("Error:", navmesh.get_log())
```

#### `add_agent(pos: list[float], params: dict[str, float]) -> int`
Ajoute un agent à la foule.

**Paramètres:**
- `pos` (list[float]): Position initiale [x, y, z]
- `params` (dict[str, float]): Paramètres de l'agent (voir section Paramètres d'Agent)

**Retourne:** Index de l'agent (>= 0) ou -1 en cas d'erreur

**Exemple:**
```python
from PyRecastDetour import create_default_agent_params

params = create_default_agent_params()
params["maxSpeed"] = 5.0
agent_id = navmesh.add_agent([0, 0, 0], params)
```

#### `remove_agent(idx: int) -> None`
Retire un agent de la foule.

**Paramètres:**
- `idx` (int): Index de l'agent

**Exemple:**
```python
navmesh.remove_agent(agent_id)
```

#### `update_crowd(dt: float) -> None`
Met à jour la simulation de foule.

**Paramètres:**
- `dt` (float): Delta time en secondes

**Exemple:**
```python
# Dans votre boucle de jeu (60 FPS)
navmesh.update_crowd(0.016)
```

#### `set_agent_target(idx: int, pos: list[float]) -> bool`
Définit la cible de navigation d'un agent.

**Paramètres:**
- `idx` (int): Index de l'agent
- `pos` (list[float]): Position cible [x, y, z]

**Retourne:** True si succès

**Exemple:**
```python
if navmesh.set_agent_target(agent_id, [10, 0, 10]):
    print("Target set")
```

#### `set_agent_velocity(idx: int, vel: list[float]) -> bool`
Définit la vélocité directe d'un agent (contrôle manuel).

**Paramètres:**
- `idx` (int): Index de l'agent
- `vel` (list[float]): Vélocité [x, y, z]

**Retourne:** True si succès

**Exemple:**
```python
navmesh.set_agent_velocity(agent_id, [1.0, 0, 0])
```

#### `reset_agent_target(idx: int) -> bool`
Annule la cible de l'agent.

**Paramètres:**
- `idx` (int): Index de l'agent

**Retourne:** True si succès

#### `get_agent_position(idx: int) -> list[float]`
Récupère la position actuelle d'un agent.

**Paramètres:**
- `idx` (int): Index de l'agent

**Retourne:** Position [x, y, z]

**Exemple:**
```python
pos = navmesh.get_agent_position(agent_id)
print(f"Agent at: {pos}")
```

#### `get_agent_velocity(idx: int) -> list[float]`
Récupère la vélocité actuelle d'un agent.

**Paramètres:**
- `idx` (int): Index de l'agent

**Retourne:** Vélocité [x, y, z]

**Exemple:**
```python
vel = navmesh.get_agent_velocity(agent_id)
speed = (vel[0]**2 + vel[1]**2 + vel[2]**2)**0.5
```

#### `get_agent_state(idx: int) -> dict[str, float]`
Récupère l'état complet d'un agent.

**Paramètres:**
- `idx` (int): Index de l'agent

**Retourne:** Dictionnaire avec:
- Position: `posX`, `posY`, `posZ`
- Vélocité actuelle: `velX`, `velY`, `velZ`
- Vélocité désirée: `dvelX`, `dvelY`, `dvelZ`
- Vélocité ajustée: `nvelX`, `nvelY`, `nvelZ`
- Paramètres: `radius`, `height`, `maxSpeed`, `maxAcceleration`, etc.
- État: `active`, `state`, `partial`, `targetState`
- Cible: `targetPosX`, `targetPosY`, `targetPosZ`
- Vitesse: `desiredSpeed`

**Exemple:**
```python
state = navmesh.get_agent_state(agent_id)
print(f"Speed: {state['desiredSpeed']}")
print(f"Target state: {state['targetState']}")  # 2 = VALID
```

#### `get_agent_count() -> int`
Récupère le nombre total d'agents dans la foule.

**Retourne:** Nombre d'agents

**Exemple:**
```python
count = navmesh.get_agent_count()
print(f"Active agents: {count}")
```

#### `update_agent_parameters(idx: int, params: dict[str, float]) -> None`
Met à jour les paramètres d'un agent à la volée.

**Paramètres:**
- `idx` (int): Index de l'agent
- `params` (dict[str, float]): Paramètres à modifier

**Exemple:**
```python
# Accélérer l'agent
navmesh.update_agent_parameters(agent_id, {
    "maxSpeed": 10.0,
    "maxAcceleration": 15.0
})
```

---

### Paramètres d'Agent

Dictionnaire de paramètres pour `add_agent()` et `update_agent_parameters()`:

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `radius` | float | 0.6 | Rayon de collision |
| `height` | float | 2.0 | Hauteur de l'agent |
| `maxAcceleration` | float | 8.0 | Accélération maximum |
| `maxSpeed` | float | 3.5 | Vitesse maximum |
| `collisionQueryRange` | float | radius*12 | Portée de détection collision |
| `pathOptimizationRange` | float | radius*30 | Portée d'optimisation de chemin |
| `separationWeight` | float | 2.0 | Poids de séparation entre agents |
| `updateFlags` | int | 15 | Flags de comportement (voir Flags) |
| `obstacleAvoidanceType` | int | 3 | Type d'évitement [0-7] |
| `queryFilterType` | int | 0 | Type de filtre de requête |

**Flags de comportement (`updateFlags`):**
- `1` - CROWD_ANTICIPATE_TURNS: Anticiper les virages
- `2` - CROWD_OBSTACLE_AVOIDANCE: Évitement d'obstacles
- `4` - CROWD_SEPARATION: Séparation entre agents
- `8` - CROWD_OPTIMIZE_VIS: Optimiser visibilité
- `16` - CROWD_OPTIMIZE_TOPO: Optimiser topologie
- Défaut: `15` (tous sauf SEPARATION)

**Exemple:**
```python
params = {
    "radius": 0.5,
    "height": 1.8,
    "maxSpeed": 4.0,
    "maxAcceleration": 10.0,
    "updateFlags": 1 | 2 | 8 | 16,  # ANTICIPATE + AVOID + OPTIMIZE
    "separationWeight": 3.0
}
```

---

### Requêtes Spatiales

Voir sections [Pathfinding](#pathfinding) pour les requêtes de chemin et distance.

---

### Export/Import

#### `save_navmesh(file_path: str) -> None`
Sauvegarde le navmesh dans un fichier binaire.

**Paramètres:**
- `file_path` (str): Chemin du fichier (extension .bin requise)

**Exemple:**
```python
navmesh.save_navmesh("level_navmesh.bin")
```

#### `load_navmesh(file_path: str) -> None`
Charge un navmesh depuis un fichier binaire.

**Paramètres:**
- `file_path` (str): Chemin du fichier .bin

**Exemple:**
```python
navmesh.load_navmesh("level_navmesh.bin")
```

#### `get_navmesh_trianglulation() -> tuple[list[float], list[int]]`
Exporte le navmesh en triangles.

**Retourne:** (vertices, triangles)
- `vertices`: [x1, y1, z1, x2, y2, z2, ...]
- `triangles`: [i1, i2, i3, i4, i5, i6, ...]

**Exemple:**
```python
verts, tris = navmesh.get_navmesh_trianglulation()
```

#### `get_navmesh_polygonization() -> tuple[list[float], list[int], list[int]]`
Exporte le navmesh en polygones.

**Retourne:** (vertices, polygons, sizes)
- `vertices`: [x1, y1, z1, ...]
- `polygons`: [i1, i2, i3, i4, ...]
- `sizes`: [3, 4, 6, ...] (nombre de sommets par polygone)

**Exemple:**
```python
verts, polys, sizes = navmesh.get_navmesh_polygonization()
```

---

## Constantes

Importées depuis le module:

```python
from PyRecastDetour import (
    # Flags crowd
    CROWD_ANTICIPATE_TURNS,
    CROWD_OBSTACLE_AVOIDANCE,
    CROWD_SEPARATION,
    CROWD_OPTIMIZE_VIS,
    CROWD_OPTIMIZE_TOPO,

    # États agent
    CROWDAGENT_STATE_INVALID,
    CROWDAGENT_STATE_WALKING,
    CROWDAGENT_STATE_OFFMESH,

    # États cible
    CROWDAGENT_TARGET_NONE,
    CROWDAGENT_TARGET_FAILED,
    CROWDAGENT_TARGET_VALID,
    CROWDAGENT_TARGET_REQUESTING,
    CROWDAGENT_TARGET_WAITING_FOR_QUEUE,
    CROWDAGENT_TARGET_WAITING_FOR_PATH,
    CROWDAGENT_TARGET_VELOCITY,

    # Types de partition
    PARTITION_WATERSHED,
    PARTITION_MONOTONE,
    PARTITION_LAYERS
)
```

---

## Fonctions Utilitaires

#### `create_default_agent_params() -> dict[str, float]`
Crée un dictionnaire avec les paramètres d'agent par défaut.

**Retourne:** Dictionnaire de paramètres

**Exemple:**
```python
from PyRecastDetour import create_default_agent_params

params = create_default_agent_params()
params["maxSpeed"] = 5.0  # Personnaliser
agent_id = navmesh.add_agent([0, 0, 0], params)
```

---

## Exemples Complets

### Exemple 1: Pathfinding Simple

```python
from PyRecastDetour import Navmesh

# Créer et construire navmesh
navmesh = Navmesh()
navmesh.init_by_obj("level.obj")
navmesh.build_navmesh()

# Trouver un chemin
start = [0, 0, 0]
end = [10, 0, 10]
path = navmesh.pathfind_straight(start, end)

# Afficher le chemin
print(f"Path has {len(path)//3} points")
for i in range(0, len(path), 3):
    print(f"  Point {i//3}: ({path[i]:.2f}, {path[i+1]:.2f}, {path[i+2]:.2f})")
```

### Exemple 2: Simulation de Foule

```python
from PyRecastDetour import Navmesh, create_default_agent_params

# Initialiser
navmesh = Navmesh()
navmesh.init_by_obj("level.obj")
navmesh.build_navmesh()
navmesh.init_crowd(100, 1.0)

# Créer des agents
agents = []
for i in range(10):
    params = create_default_agent_params()
    params["maxSpeed"] = 3.0 + i * 0.5  # Vitesses variées

    pos = [i * 2.0, 0, 0]
    agent_id = navmesh.add_agent(pos, params)
    agents.append(agent_id)

    # Définir cible
    navmesh.set_agent_target(agent_id, [50, 0, 50])

# Boucle de simulation
import time
for frame in range(1000):
    # Mettre à jour (60 FPS)
    navmesh.update_crowd(0.016)

    # Afficher positions
    if frame % 60 == 0:  # Chaque seconde
        for agent_id in agents:
            pos = navmesh.get_agent_position(agent_id)
            state = navmesh.get_agent_state(agent_id)
            print(f"Agent {agent_id}: pos={pos}, speed={state['desiredSpeed']:.2f}")

    time.sleep(0.016)
```

### Exemple 3: Configuration Avancée

```python
from PyRecastDetour import Navmesh

navmesh = Navmesh()
navmesh.init_by_obj("complex_level.obj")

# Configuration pour petit agent
settings = {
    "cellSize": 0.1,           # Haute résolution
    "cellHeight": 0.05,
    "agentHeight": 1.0,        # Agent petit
    "agentRadius": 0.3,
    "agentMaxClimb": 0.3,      # Peut monter 30cm
    "agentMaxSlope": 60.0,     # Pentes raides OK
    "vertsPerPoly": 6          # Polygones complexes
}
navmesh.set_settings(settings)
navmesh.build_navmesh()

# Vérifier le log
log = navmesh.get_log()
if log:
    print("Build log:", log)
```

### Exemple 4: Gestion des Erreurs

```python
from PyRecastDetour import Navmesh

navmesh = Navmesh()

try:
    navmesh.init_by_obj("level.obj")
    navmesh.build_navmesh()

    log = navmesh.get_log()
    if "error" in log.lower() or "fail" in log.lower():
        raise Exception(f"Build failed: {log}")

    # Initialiser crowd
    if not navmesh.init_crowd(100, 1.0):
        raise Exception(f"Crowd init failed: {navmesh.get_log()}")

    # Ajouter agent
    params = create_default_agent_params()
    agent_id = navmesh.add_agent([0, 0, 0], params)
    if agent_id == -1:
        raise Exception(f"Add agent failed: {navmesh.get_log()}")

    # Utiliser agent
    if not navmesh.set_agent_target(agent_id, [10, 0, 10]):
        print("Warning: Could not set target")

except Exception as e:
    print(f"Error: {e}")
```

---

## Notes Importantes

1. **Ordre d'appel obligatoire:**
   - `init_by_obj()` ou `init_by_raw()`
   - Optionnel: `set_settings()`
   - `build_navmesh()`
   - Optionnel: `init_crowd()`

2. **Gestion d'erreurs:**
   - Toujours vérifier `get_log()` après les opérations critiques
   - `add_agent()` retourne -1 en cas d'erreur
   - Les fonctions `set_*` retournent des booléens

3. **Performance:**
   - Construire le navmesh une seule fois
   - Sauvegarder/charger avec `save_navmesh()`/`load_navmesh()`
   - Limiter le nombre d'agents pour de meilleures performances
   - `update_crowd()` peut être coûteux avec beaucoup d'agents

4. **Unités:**
   - Toutes les distances/positions sont en unités du monde
   - `dt` pour `update_crowd()` est en secondes

---

## Support et Ressources

- **Documentation Recast Navigation:** https://github.com/recastnavigation/recastnavigation
- **Fichiers sources:** CLAUDE.md et BUILD_INSTRUCTIONS.md
- **Exemples:** example.py

Pour plus d'informations sur les algorithmes et concepts sous-jacents, consultez la documentation officielle de Recast Navigation.
