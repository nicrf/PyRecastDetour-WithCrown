#!/bin/bash
# Clean build artifacts and temporary files

echo "Cleaning build artifacts..."

# Remove build directories
rm -rf build/
rm -rf build_msvc/
rm -rf build_mingw/

# Remove compiled binaries from dist (keep source files)
rm -f dist/*.pyd
rm -f dist/*.so

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Remove temporary test files
rm -f test_*.py
rm -f test_*.txt
rm -f py37_paths.txt

# Remove downloaded dependencies (optional - uncomment to clean)
# rm -rf pybind11_src/
# rm -f pybind11.zip

# Remove virtual environments (optional - uncomment to clean)
# rm -rf venv37/
# rm -rf venv*/

echo ""
echo "Cleanup complete!"
echo ""
echo "Kept:"
echo "  - Source files"
echo "  - Documentation"
echo "  - dist/__init__.py and examples"
echo "  - pybind11_src/ (uncomment in script to remove)"
echo "  - venv37/ (uncomment in script to remove)"
echo ""
