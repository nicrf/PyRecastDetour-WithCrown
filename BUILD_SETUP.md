# PyRecastDetour - Build Setup Guide

Guide for compiling PyRecastDetour for Python 3.7 (or other versions).

## Prerequisites

### Windows (MSVC - Recommended)
1. **Visual Studio 2017/2019/2022** with C++ build tools
2. **Python 3.7+** (full version with headers and libs)
3. **PyBind11** (will be downloaded automatically)

### Linux / macOS
1. **GCC/Clang** with C++14 support
2. **Python 3.7+** with development headers
3. **PyBind11** (will be downloaded automatically)

## Configuration for Python 3.7

### Step 1: Create a virtual environment

```bash
# With virtualenv (recommended)
python -m virtualenv -p /path/to/python3.7 venv37

# Or with standard venv (if available)
python3.7 -m venv venv37
```

### Step 2: Download PyBind11

```bash
curl -L -o pybind11.zip https://github.com/pybind/pybind11/archive/refs/tags/v2.13.6.zip
unzip pybind11.zip
mv pybind11-2.13.6 pybind11_src
```

### Step 3: Compile

**Windows (MSVC):**
```batch
build_msvc.bat
```

**Linux/macOS:**
```bash
chmod +x build.sh
./build.sh
```

## Compiling for another Python version

The `build_msvc.bat` script automatically detects Python from the venv. To change version:

1. Create a venv with the desired version:
   ```bash
   python -m virtualenv -p /path/to/python3.X venvXX
   ```

2. Modify `build_msvc.bat` line 22:
   ```batch
   set PYTHON_PATH=venvXX\\Scripts\\python.exe
   ```

3. Modify the module name on line 40:
   ```batch
   set MODULE_NAME=PyXXRecastDetour
   ```

4. Compile:
   ```batch
   build_msvc.bat
   ```

## Project structure after compilation

```
PyRecastDetour-Sources-main/
├── dist/                           # Distribution package
│   ├── __init__.py                # Python wrapper
│   ├── Py37RecastDetour.pyd      # Compiled module (Windows)
│   ├── example.py                # Examples
│   └── README.md                 # Installation instructions
├── build_msvc/                    # Temporary build folder (ignored by git)
├── venv37/                        # Virtual environment (ignored by git)
├── pybind11_src/                  # PyBind11 source (ignored by git)
└── ...
```

## Files ignored by Git

The following files are automatically ignored (see `.gitignore`):
- `build_msvc/` - Temporary compilation files
- `venv37/` or `venv*/` - Virtual environments
- `pybind11_src/` - Downloaded PyBind11 source
- `*.pyd`, `*.so` in dist/ - Compiled binaries
- Temporary test files

## Distribution

The `dist/` folder contains everything needed to use PyRecastDetour:
- The compiled `.pyd` or `.so` file
- The Python wrapper `__init__.py`
- Examples and documentation

To distribute:
```bash
cd dist
zip -r PyRecastDetour-python37-win64.zip *
```

## Common Issues

### Python libs not found
The script automatically detects the path via `sys.base_prefix`. If this fails:
- Verify Python is installed with development libs
- On Windows: `python.exe` must be in PATH
- On Linux: install `python3.7-dev`

### PyBind11 not found
The script looks for `pybind11_src/include`. Make sure to:
1. Download PyBind11 v2.13.6 (compatible with Python 3.7)
2. Extract to `pybind11_src/`

### Linking errors
- Windows: Use Visual Studio 2017+ with MSVC
- The `.lib` files in `lib/` must be compiled with the same compiler
- If errors persist, recompile Recast/Detour sources (the script does this automatically)

## Multi-version support

To support multiple Python versions, compile for each version and create separate packages:
- `PyRecastDetour-python37-win64.zip`
- `PyRecastDetour-python38-win64.zip`
- `PyRecastDetour-python39-win64.zip`
- etc.

The `__init__.py` automatically detects the version and loads the correct module.
