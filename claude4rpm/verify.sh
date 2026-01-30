#!/bin/bash
# Simple test script to verify basic functionality

set -e

echo "================================"
echo "Claude4RPM Basic Verification"
echo "================================"
echo

# Check Python
echo "Checking Python..."
python3 --version

# Check required commands
echo "Checking required commands..."
which go || echo "Warning: go not found (needed for analyzing projects)"
which docker || echo "Warning: docker not found (needed for building RPMs)"

# Check project structure
echo
echo "Checking project structure..."
for dir in src templates docker output tests; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir/"
    else
        echo "  ✗ $dir/ missing"
        exit 1
    fi
done

# Check main files
echo
echo "Checking main files..."
for file in main.py demo.py requirements.txt README.md; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file missing"
        exit 1
    fi
done

# Check Python modules
echo
echo "Checking Python modules..."
for module in dependency_analyzer spec_generator docker_builder validator; do
    if [ -f "src/${module}.py" ]; then
        echo "  ✓ src/${module}.py"
    else
        echo "  ✗ src/${module}.py missing"
        exit 1
    fi
done

# Try importing modules
echo
echo "Testing Python imports..."
python3 -c "import sys; sys.path.insert(0, 'src'); from dependency_analyzer import DependencyAnalyzer" && echo "  ✓ dependency_analyzer" || echo "  ✗ dependency_analyzer import failed"
python3 -c "import sys; sys.path.insert(0, 'src'); from spec_generator import SpecGenerator" && echo "  ✓ spec_generator" || echo "  ✗ spec_generator import failed"
python3 -c "import sys; sys.path.insert(0, 'src'); from docker_builder import DockerBuilder" && echo "  ✓ docker_builder" || echo "  ✗ docker_builder import failed"
python3 -c "import sys; sys.path.insert(0, 'src'); from validator import Validator" && echo "  ✓ validator" || echo "  ✗ validator import failed"

# Check help
echo
echo "Testing CLI help..."
./main.py --help > /dev/null && echo "  ✓ CLI help works" || echo "  ✗ CLI help failed"

# Run demo if requested
if [ "$1" = "--demo" ]; then
    echo
    echo "Running demo..."
    ./demo.py
fi

echo
echo "================================"
echo "✓ Basic verification complete!"
echo "================================"
echo
echo "Next steps:"
echo "  1. Install dependencies: pip install -r requirements.txt"
echo "  2. Run demo: ./demo.py"
echo "  3. Try with a Go project: ./main.py analyze /path/to/project"
echo
