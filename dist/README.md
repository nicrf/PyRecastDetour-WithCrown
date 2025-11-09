# PyRecastDetour - Package de Distribution

Ce dossier contient le package Python prêt à l'emploi pour PyRecastDetour.

## Contenu

- `__init__.py` - Module Python avec helpers et constantes
- `example.py` - Exemples d'utilisation détaillés
- `Py310RecastDetour.cp313-win_amd64.pyd` - Module compilé (après build)

## Obtenir le fichier .pyd

Le fichier `.pyd` (Windows) ou `.so` (Linux/Mac) est le module compilé C++. Pour l'obtenir:

### Option 1: Compiler vous-même

Retournez au dossier parent et lancez le script de build:

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

### Option 2: Obtenir un binaire pré-compilé

Si disponible, téléchargez le binaire pré-compilé pour votre plateforme et placez-le dans ce dossier.

## Installation

Une fois le fichier `.pyd`/`.so` obtenu, copiez ce dossier `dist/` dans votre projet:

```bash
# Copier vers votre projet
cp -r dist/ /path/to/your/project/PyRecastDetour

# Ou ajouter au PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/path/to/dist
```

## Utilisation

```python
from PyRecastDetour import Navmesh, create_default_agent_params

# Créer navmesh
navmesh = Navmesh()
navmesh.init_by_obj("level.obj")
navmesh.build_navmesh()

# Pathfinding
path = navmesh.pathfind_straight([0, 0, 0], [10, 0, 10])
print(f"Path: {path}")

# Crowd simulation
navmesh.init_crowd(100, 1.0)
params = create_default_agent_params()
agent_id = navmesh.add_agent([5, 0, 5], params)
navmesh.set_agent_target(agent_id, [50, 0, 50])
navmesh.update_crowd(0.016)
```

## Documentation

Consultez les fichiers suivants dans le dossier parent:
- `PYTHON_API.md` - Documentation complète de l'API
- `example.py` - Exemples d'utilisation (aussi dans ce dossier)
- `CLAUDE.md` - Documentation technique du projet

## Versions Python supportées

- Python 3.6+
- Le nom du module varie selon la version:
  - Python 3.6: `Py36RecastDetour`
  - Python 3.7: `Py37RecastDetour`
  - Python 3.8: `Py38RecastDetour`
  - Python 3.9: `Py39RecastDetour`
  - Python 3.10+: `Py310RecastDetour`

Le fichier `__init__.py` gère automatiquement l'import de la bonne version.

## Problèmes courants

### Module not found
Vérifiez que le fichier `.pyd`/`.so` est bien présent dans ce dossier.

### ImportError: DLL load failed
Sur Windows, vérifiez que vous avez les Visual C++ Redistributables installés.

### Wrong Python version
Assurez-vous que le fichier compilé correspond à votre version de Python.

## Support

Pour plus d'informations, consultez:
- GitHub: https://github.com/Tugcga/PyRecastDetour
- Recast Navigation: https://github.com/recastnavigation/recastnavigation
