# PyRecastDetour v1.1.0 - Package de Distribution

Package Python professionnel pour la navigation et simulation de foule basé sur Recast Navigation.

## 🎯 Nouvelles Fonctionnalités v1.1.0

Cette version ajoute des fonctionnalités avancées pour une navigation et simulation de foule de niveau professionnel:

### 1. **Nav Volumes & 3D Navigation**
- Marquage de zones avec propriétés personnalisées (eau, routes, danger)
- Support de volumes convexes (3-12 vertices)
- Requêtes et gestion des volumes

### 2. **Off-Mesh Connections**
- Connexions de saut (unidirectionnelles/bidirectionnelles)
- Échelles et surfaces escaladables
- Téléporteurs et portes
- Jusqu'à 256 connexions

### 3. **Auto-Markup System**
- Marquage automatique de zones géométriques
- Zones en boîte, cylindriques et polygonales
- Configuration de pentes marchables

### 4. **Advanced Crowd Management**
- **8 profils d'évitement d'obstacles** (Agressif, Passif, Défensif, Personnalisé)
- **16 filtres de requêtes** pour différents types d'agents
- **Requêtes avancées**: voisins, coins de chemin, agents actifs
- **Mises à jour en temps réel** des paramètres d'agents

### 5. **Formations & Group Behaviors**
- **5 types de formations**: Ligne, Colonne, Wedge, Boîte, Cercle
- **Gestion de groupes** avec leaders et suiveurs
- **Déplacement coordonné** avec position et direction de formation
- **Mises à jour automatiques** des positions d'agents dans la formation

## 📦 Contenu

### Fichiers Principaux
- `__init__.py` - Module Python avec helpers et constantes (385 lignes)
- `Py37RecastDetour.pyd` - Module compilé C++ (après build)
- `README.md` - Ce fichier

### Exemples
- `example.py` - Exemple de base
- `test_convex_volumes.py` - Démo volumes convexes
- `test_offmesh_connections.py` - Démo connexions spéciales
- `test_crowd_advanced.py` - Démo crowd avancée
- `test_auto_markup.py` - Démo auto-markup
- `test_formations.py` - Démo formations et groupes
- `test_complete_example.py` - Exemple complet intégré
- `diagnostic_test.py` - Tests de diagnostic

## 🚀 Installation Rapide

### 1. Obtenir le Module Compilé

**Windows avec MSVC (recommandé):**
```batch
cd ..
build_msvc.bat
```

**Windows avec MinGW:**
```batch
cd ..
build.bat
```

**Linux/Mac:**
```bash
cd ..
chmod +x build.sh
./build.sh
```

Le fichier `.pyd` ou `.so` sera automatiquement copié dans ce dossier `dist/`.

### 2. Utiliser le Package

**Option A: Copier dans votre projet**
```bash
cp -r dist/ /path/to/your/project/PyRecastDetour
```

**Option B: Ajouter au PYTHONPATH**
```bash
export PYTHONPATH=$PYTHONPATH:/path/to/dist
```

**Option C: Installation pip (si package créé)**
```bash
pip install -e /path/to/dist
```

## 💡 Utilisation

### Exemple de Base

```python
import PyRecastDetour as prd

# 1. Créer et configurer navmesh
navmesh = prd.Navmesh()
navmesh.init_by_obj("level.obj")
navmesh.build_navmesh()

# 2. Pathfinding
path = navmesh.pathfind_straight([0, 0, 0], [10, 0, 10])
print(f"Path: {path}")

# 3. Crowd simulation basique
navmesh.init_crowd(100, 1.0)
params = prd.create_default_agent_params()
agent_id = navmesh.add_agent([5, 0, 5], params)
navmesh.set_agent_target(agent_id, [50, 0, 50])

# 4. Simulation loop
navmesh.update_crowd(0.016)  # 60 FPS
pos = navmesh.get_agent_position(agent_id)
```

### Exemple Avancé - Convex Volumes

```python
import PyRecastDetour as prd

navmesh = prd.Navmesh()
navmesh.init_by_obj("level.obj")

# Marquer une zone d'eau (cylindre)
navmesh.mark_cylinder_area(
    pos=[25.0, 0.0, 25.0],
    radius=10.0,
    height=2.0,
    area_id=prd.POLYAREA_WATER
)

# Marquer une route (boîte)
navmesh.mark_box_area(
    bmin=[0.0, 0.0, 0.0],
    bmax=[100.0, 1.0, 5.0],
    area_id=prd.POLYAREA_ROAD
)

# Construire avec les zones marquées
navmesh.build_navmesh()
```

### Exemple Avancé - Off-Mesh Connections

```python
# Ajouter une connexion de saut
navmesh.add_offmesh_connection(
    start_pos=[5.0, 2.0, 5.0],
    end_pos=[10.0, 3.0, 10.0],
    radius=0.5,
    bidirectional=False,  # Saut unidirectionnel
    area=prd.POLYAREA_JUMP,
    flags=prd.POLYFLAGS_JUMP
)

# Ajouter une échelle
navmesh.add_offmesh_connection(
    start_pos=[15.0, 0.0, 5.0],
    end_pos=[15.0, 5.0, 5.0],
    radius=0.3,
    bidirectional=True,  # Bidirectionnel
    area=prd.POLYAREA_CLIMB,
    flags=prd.POLYFLAGS_CLIMB
)

navmesh.build_navmesh()
```

### Exemple Avancé - Crowd avec Profils

```python
navmesh.init_crowd(100, 1.0)

# Configurer profil d'évitement agressif
navmesh.set_obstacle_avoidance_params(
    0,
    prd.create_obstacle_avoidance_params("aggressive")
)

# Configurer filtre pour infanterie (peut marcher, pas nager)
prd.setup_query_filter_infantry(navmesh, 0)

# Créer agent avec comportement personnalisé
params = prd.create_default_agent_params()
params["obstacleAvoidanceType"] = 0  # Profil agressif
params["queryFilterType"] = 0        # Filtre infanterie
params["maxSpeed"] = 4.0

soldier_id = navmesh.add_agent([5, 0, 5], params)
navmesh.set_agent_target(soldier_id, [50, 0, 50])

# Simulation avec requêtes avancées
navmesh.update_crowd(0.016)

# Obtenir voisins et coins de chemin
neighbors = navmesh.get_agent_neighbors(soldier_id)
corners = navmesh.get_agent_corners(soldier_id)
print(f"Agent a {len(neighbors)} voisins et {len(corners)//3} coins")
```

### Exemple Avancé - Formations

```python
import PyRecastDetour as prd

navmesh = prd.Navmesh()
navmesh.init_by_obj("level.obj")
navmesh.build_navmesh()
navmesh.init_crowd(100, 1.0)

# Créer une formation en ligne avec espacement de 2m
formation_id = navmesh.create_formation(prd.FORMATION_LINE, spacing=2.0)

# Ajouter des agents à la formation
params = prd.create_default_agent_params()
for i in range(5):
    agent_id = navmesh.add_agent((i * 2.0, 0.0, 0.0), params)
    navmesh.add_agent_to_formation(formation_id, agent_id)

# Définir le leader (optionnel)
navmesh.set_formation_leader(formation_id, 0)

# Définir la cible et direction de la formation
navmesh.set_formation_target(
    formation_id,
    target_pos=(50.0, 0.0, 50.0),  # Position cible
    target_dir=(1.0, 0.0, 0.0)      # Direction (vers l'est)
)

# Boucle de simulation
dt = 0.016  # 60 FPS
while True:
    navmesh.update_crowd(dt)
    navmesh.update_formations(dt)  # Met à jour les positions de formation

    # Vérifier l'état de la formation
    info = navmesh.get_formation_info(formation_id)
    print(f"Formation a {int(info['agent_count'])} agents")
```

## 📚 API Complète

### Convex Volumes
```python
# Ajouter volume
navmesh.add_convex_volume(verts, minh, maxh, area)

# Requêtes
count = navmesh.get_convex_volume_count()
volume = navmesh.get_convex_volume(index)
all_volumes = navmesh.get_all_convex_volumes()

# Supprimer
navmesh.delete_convex_volume(index)
```

### Off-Mesh Connections
```python
# Ajouter connexion
navmesh.add_offmesh_connection(start_pos, end_pos, radius, bidirectional, area, flags)

# Requêtes
count = navmesh.get_offmesh_connection_count()
conn = navmesh.get_offmesh_connection(index)
all_conns = navmesh.get_all_offmesh_connections()

# Supprimer
navmesh.delete_offmesh_connection(index)
```

### Auto-Markup
```python
# Marquer zones
navmesh.mark_box_area(bmin, bmax, area_id)
navmesh.mark_cylinder_area(pos, radius, height, area_id)
navmesh.mark_convex_poly_area(verts, hmin, hmax, area_id)

# Configuration
navmesh.mark_walkable_triangles(walkable_slope_angle)
navmesh.erode_walkable_area(radius)
navmesh.median_filter_walkable_area()
```

### Advanced Crowd
```python
# Profils d'évitement
navmesh.set_obstacle_avoidance_params(idx, params)
params = navmesh.get_obstacle_avoidance_params(idx)

# Filtres de requêtes
navmesh.set_query_filter_area_cost(filter_index, area_id, cost)
cost = navmesh.get_query_filter_area_cost(filter_index, area_id)
navmesh.set_query_filter_include_flags(filter_index, flags)
navmesh.set_query_filter_exclude_flags(filter_index, flags)

# Requêtes d'agents
neighbors = navmesh.get_agent_neighbors(agent_idx)
corners = navmesh.get_agent_corners(agent_idx)
active = navmesh.get_active_agents()
is_active = navmesh.is_agent_active(idx)
params = navmesh.get_agent_parameters(idx)

# Mises à jour
navmesh.update_agent_parameters(idx, params)
```

## 🎨 Constantes

### Types de Zones
```python
POLYAREA_GROUND = 0    # Sol normal
POLYAREA_WATER = 1     # Eau (nage requise)
POLYAREA_ROAD = 2      # Route (préférée)
POLYAREA_DOOR = 3      # Porte
POLYAREA_GRASS = 4     # Herbe (ralentit)
POLYAREA_JUMP = 5      # Zone de saut
POLYAREA_CLIMB = 6     # Zone d'escalade
POLYAREA_DANGER = 7    # Zone dangereuse
```

### Drapeaux de Capacités
```python
POLYFLAGS_WALK = 0x01       # Peut marcher
POLYFLAGS_SWIM = 0x02       # Peut nager
POLYFLAGS_DOOR = 0x04       # Peut utiliser portes
POLYFLAGS_JUMP = 0x08       # Peut sauter
POLYFLAGS_CLIMB = 0x10      # Peut escalader
POLYFLAGS_DISABLED = 0x20   # Désactivé
POLYFLAGS_ALL = 0xFFFF      # Toutes capacités
```

### Drapeaux Crowd
```python
CROWD_ANTICIPATE_TURNS = 1      # Anticiper virages
CROWD_OBSTACLE_AVOIDANCE = 2    # Éviter obstacles
CROWD_SEPARATION = 4            # Séparation agents
CROWD_OPTIMIZE_VIS = 8          # Optimiser visibilité
CROWD_OPTIMIZE_TOPO = 16        # Optimiser topologie
```

## 🛠️ Helpers

```python
# Paramètres par défaut
params = create_default_agent_params()

# Paramètres véhicule
vehicle_params = create_vehicle_params()

# Profils d'évitement
aggressive = create_obstacle_avoidance_params("aggressive")
passive = create_obstacle_avoidance_params("passive")
defensive = create_obstacle_avoidance_params("defensive")

# Configuration filtres
setup_query_filter_infantry(navmesh, 0)     # Infanterie
setup_query_filter_amphibious(navmesh, 1)  # Amphibie
setup_query_filter_flying(navmesh, 2)      # Volant
```

## 📖 Documentation Complète

Consultez les fichiers suivants dans le dossier parent:

- **`QUICK_REFERENCE.md`** - Référence rapide (cheat sheet)
- **`FEATURES.md`** - Documentation complète des fonctionnalités
- **`IMPLEMENTATION_SUMMARY.md`** - Détails d'implémentation
- **`examples/README.md`** - Guide des exemples
- **`CLAUDE.md`** - Documentation technique du projet

## 🔧 Versions Python Supportées

- Python 3.6, 3.7, 3.8, 3.9, 3.10+
- Le nom du module varie selon la version:
  - Python 3.6: `Py36RecastDetour`
  - Python 3.7: `Py37RecastDetour`
  - Python 3.8: `Py38RecastDetour`
  - Python 3.9: `Py39RecastDetour`
  - Python 3.10+: `Py310RecastDetour`

Le fichier `__init__.py` gère automatiquement l'import de la bonne version.

## ❓ Problèmes Courants

### Module not found
✅ Vérifiez que le fichier `.pyd`/`.so` est bien présent dans ce dossier.

### ImportError: DLL load failed
✅ Sur Windows, installez Visual C++ Redistributables 2019 ou plus récent.

### Wrong Python version
✅ Recompilez pour votre version de Python spécifique.

### Agent ne suit pas le chemin
✅ Vérifiez que le navmesh est construit: `navmesh.build_navmesh()`
✅ Vérifiez la cible avec `navmesh.get_log()`

### Agent ne traverse pas connexion
✅ Vérifiez que le query filter inclut les flags appropriés
✅ Exemple: `navmesh.set_query_filter_include_flags(0, POLYFLAGS_JUMP)`

### Chemin passe par l'eau
✅ Augmentez le coût de l'eau dans le query filter
✅ Exemple: `navmesh.set_query_filter_area_cost(0, POLYAREA_WATER, 10.0)`

## 🎯 Cas d'Usage

### Jeux Vidéo
- **RTS**: Multiples unités avec comportements différents
- **MOBA**: Pathfinding complexe avec obstacles dynamiques
- **RPG**: Navigation de PNJ avec zones spéciales
- **Stealth**: IA ennemie avec patrouilles et champs de vision

### Robotique
- Navigation multi-robot
- Planification de chemin
- Évitement d'obstacles dynamiques

### Simulation
- Simulation de foules
- Simulation de trafic
- Évacuation de bâtiments

### Recherche
- IA navigation
- Modélisation de comportements
- Algorithmes de pathfinding

## 📊 Performance

### Limites
- **Volumes Convexes**: 256 maximum, 12 vertices par volume
- **Off-Mesh Connections**: 256 maximum
- **Profils d'Évitement**: 8 maximum
- **Filtres de Requêtes**: 16 maximum
- **Agents Crowd**: Limité par `maxAgents` (100-1000+ selon hardware)

### Optimisations
- Requêtes voisins/corners: O(1) - très rapide
- Update crowd: ~0.1-0.5ms par agent
- Construction navmesh: Une fois, pas pendant runtime
- Volumes/connexions: Traités au build, pas de coût runtime

## 🆕 Changelog v1.1.0

### Ajouté
- ✨ Convex volumes pour marquage de zones
- ✨ Off-mesh connections (sauts, échelles, téléports)
- ✨ Auto-markup system (box, cylinder, polygon)
- ✨ 8 profils d'évitement d'obstacles
- ✨ 16 filtres de requêtes pour agents
- ✨ Requêtes avancées d'agents (voisins, corners)
- ✨ Mises à jour runtime des paramètres
- ✨ 35+ constantes pour areas et flags
- ✨ 6 fonctions helper
- ✨ 5 exemples complets
- ✨ Documentation complète (500+ lignes)

### Modifié
- 🔧 `__init__.py` réécriture complète (385 lignes)
- 🔧 API backward compatible

### Performance
- ⚡ Pas d'impact sur code existant
- ⚡ Nouvelles features optimisées

## 🔗 Liens Utiles

- **GitHub Original**: https://github.com/Tugcga/PyRecastDetour
- **Recast Navigation**: https://github.com/recastnavigation/recastnavigation
- **Documentation Recast**: https://recastnav.com/
- **PyBind11**: https://pybind11.readthedocs.io/

## 📝 Licence

Basé sur Recast Navigation par Mikko Mononen.
Python bindings utilisant PyBind11.

Version 1.1.0 - Novembre 2025
