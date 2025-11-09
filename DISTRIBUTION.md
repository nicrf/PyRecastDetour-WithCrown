# Distribution Guide - PyRecastDetour

This guide explains how to create and distribute a compiled PyRecastDetour package.

## Distribution Package Structure

The `dist/` folder contains everything needed to use PyRecastDetour:

```
dist/
├── __init__.py                           # Main Python module
├── Py310RecastDetour.cp313-win_amd64.pyd # Compiled module (Windows)
├── example.py                            # Usage examples
└── README.md                             # Installation instructions
```

On Linux/Mac, the compiled file will be `.so` instead of `.pyd`.

## Creating the Package

### 1. Compile the Module

Use the appropriate build script:

**Windows with MSVC (recommended):**
```batch
build_msvc.bat
```

**Windows with MinGW:**
```batch
build.bat
```

**Linux/Mac:**
```bash
chmod +x build.sh
./build.sh
```

The script will automatically:
1. Compile all C++ source files
2. Create the Python `.pyd` or `.so` module
3. Copy the compiled module to `dist/`
4. Copy `__init__.py` and `example.py` to `dist/`

### 2. Verify Contents

```bash
ls -la dist/
```

You should see:
- `__init__.py` ✓
- `example.py` ✓
- `Py*RecastDetour.*.pyd` (or `.so`) ✓
- `README.md` ✓

### 3. Test the Package

```bash
cd dist
python example.py
```

Or test the import:
```python
python -c "from PyRecastDetour import Navmesh; print('OK')"
```

## Distributing the Package

### Option 1: Simple Distribution

Compress the `dist/` folder and share it:

```bash
cd ..
tar -czf PyRecastDetour-win64-py313.tar.gz dist/
# or
zip -r PyRecastDetour-win64-py313.zip dist/
```

Users can then:
```bash
# Decompress
tar -xzf PyRecastDetour-win64-py313.tar.gz
cd dist

# Test
python example.py
```

### Option 2: Installation via PYTHONPATH

Users add the folder to their PYTHONPATH:

**Linux/Mac:**
```bash
export PYTHONPATH=$PYTHONPATH:/path/to/PyRecastDetour/dist
```

**Windows:**
```batch
set PYTHONPATH=%PYTHONPATH%;C:\path\to\PyRecastDetour\dist
```

### Option 3: Copy to site-packages

For system-wide installation:

```bash
# Find site-packages
python -c "import site; print(site.getsitepackages()[0])"

# Copy the package
cp -r dist/* /path/to/site-packages/PyRecastDetour/
```

### Option 4: Setup.py (Advanced)

Create a `setup.py` file at the root to enable `pip install`:

```python
from setuptools import setup
import shutil
import os

# Copy dist/ to build/
# ...

setup(
    name="PyRecastDetour",
    version="1.0.0",
    packages=["PyRecastDetour"],
    package_data={
        "PyRecastDetour": ["*.pyd", "*.so"]
    }
)
```

## Multi-platform

To distribute across multiple platforms:

### Windows
```
PyRecastDetour-win32-py310.zip
PyRecastDetour-win64-py310.zip
PyRecastDetour-win64-py311.zip
PyRecastDetour-win64-py312.zip
PyRecastDetour-win64-py313.zip
```

### Linux
```
PyRecastDetour-linux-x86_64-py310.tar.gz
PyRecastDetour-linux-x86_64-py311.tar.gz
```

### macOS
```
PyRecastDetour-macos-x86_64-py310.tar.gz
PyRecastDetour-macos-arm64-py310.tar.gz  (Apple Silicon)
```

## Version Naming

Recommended format:
```
PyRecastDetour-{platform}-{arch}-py{version}.{ext}
```

Examples:
- `PyRecastDetour-win64-x64-py313.zip`
- `PyRecastDetour-linux-x86_64-py311.tar.gz`
- `PyRecastDetour-macos-arm64-py312.tar.gz`

## Distribution Checklist

Before distributing, verify:

- [ ] Module compiles without errors
- [ ] `example.py` runs correctly
- [ ] Imports work: `from PyRecastDetour import Navmesh`
- [ ] Pathfinding works with a simple navmesh
- [ ] Crowd simulation works
- [ ] README.md in dist/ is up to date
- [ ] Python version is clearly indicated
- [ ] Platform (Windows/Linux/Mac) is indicated
- [ ] Architecture (x86/x64/arm64) is indicated

## Documentation to Include

Attach these files to your distribution (optional):

- `PYTHON_API.md` - Complete API documentation
- `example.py` - Examples (already in dist/)
- `LICENSE` - Project license
- `CHANGELOG.md` - Version history

## Multiple Python Versions

To support multiple Python versions, compile for each version:

```bash
# Python 3.10
python3.10 -m pip install pybind11
# Compile with Python 3.10...

# Python 3.11
python3.11 -m pip install pybind11
# Compile with Python 3.11...

# etc.
```

Each version generates a different file:
- `Py310RecastDetour.cp310-win_amd64.pyd`
- `Py311RecastDetour.cp311-win_amd64.pyd`

The `__init__.py` automatically detects the version and loads the correct module.

## Dependencies

The package requires **no external Python dependencies**.

Recast/Detour libraries are statically linked into the `.pyd`/`.so`.

## Package Size

Approximate size:
- Compiled module: 500KB - 2MB
- `__init__.py`: 4KB
- `example.py`: 13KB
- Total: ~500KB - 2MB

To reduce size:
- Compile in Release mode (already done)
- Strip symbols: `strip *.so` (Linux/Mac)
- Compress: use `.tar.gz` or `.zip`

## Support and Maintenance

When distributing, indicate:
- PyRecastDetour version
- Recast Navigation version used
- Supported platforms
- Supported Python versions
- Support contact

Example README for end users:

```markdown
# PyRecastDetour v1.0.0

Navigation mesh and crowd simulation for Python.

**Based on:** Recast Navigation 1.6.0
**Platform:** Windows x64
**Python:** 3.10, 3.11, 3.12, 3.13

## Installation
See dist/README.md

## Documentation
See PYTHON_API.md

## Support
GitHub Issues: https://github.com/...
```

---

For any questions about distribution, consult the PyBind11 documentation:
https://pybind11.readthedocs.io/en/stable/compiling.html
