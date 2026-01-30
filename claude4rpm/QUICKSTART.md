# Quick Start Guide

## Installation

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Verify installation
./main.py --help
```

## Quick Demo

Run the demo to see the tool in action without a Go project:

```bash
./demo.py
```

This will demonstrate:
- RPM naming conventions
- Dependency structure
- SPEC file generation

## Basic Usage

### Example 1: Analyze a Go Project

```bash
# Clone a sample Go project
git clone https://github.com/gin-gonic/gin /tmp/gin-example
cd /tmp/gin-example

# Analyze dependencies
/root/claude4rpm/main.py analyze . -l
```

### Example 2: Generate SPEC Files

```bash
# Generate SPEC files for all dependencies
/root/claude4rpm/main.py generate-specs /tmp/gin-example

# Check the output
ls -lh /root/claude4rpm/output/specs/
```

### Example 3: Full Build Pipeline

```bash
# Run complete pipeline (requires Docker)
/root/claude4rpm/main.py build /tmp/gin-example

# Check results
ls -lh /root/claude4rpm/output/
```

## Testing Without Go Project

If you don't have a Go project handy, you can test with the demo:

```bash
# Run demo
./demo.py

# Check generated files
cat output/demo/*.spec
```

## Docker Setup

### Build the Docker Image

```bash
cd docker
docker build -t claude4rpm-builder .
```

### Test Docker Environment

```bash
docker run -it --rm claude4rpm-builder /bin/bash

# Inside container:
rpmbuild --version
go version
```

## Common Commands

```bash
# Analyze only
./main.py analyze /path/to/project -o ./my-output

# Generate SPECs only
./main.py generate-specs /path/to/project

# Build with verbose logging
./main.py build /path/to/project -v

# Visualize dependencies (requires graphviz)
./main.py visualize /path/to/project

# Validate existing SPECs
./main.py validate --specs-dir ./output/specs
```

## Troubleshooting

### Missing Dependencies

```bash
# Install all Python dependencies
pip install -r requirements.txt

# For visualization support
pip install graphviz
sudo apt-get install graphviz  # or yum install graphviz
```

### Docker Issues

```bash
# Check Docker is running
docker ps

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in

# Test Docker
docker run hello-world
```

### Go Module Issues

```bash
# Initialize Go module if needed
cd /path/to/project
go mod init github.com/yourname/project
go mod tidy
```

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Check the [templates/](templates/) directory to customize SPEC files
3. Review [src/](src/) for implementation details
4. Run tests: `python -m pytest tests/`

## Example Output

After running `./main.py build /path/to/project`, you'll get:

```
output/
├── dependencies.json          # Full dependency analysis
├── specs/                     # Generated SPEC files
│   ├── golang-github-gin-gonic-gin.spec
│   ├── golang-github-go-playground-validator-v10.spec
│   └── ...
├── rpms/                      # Built RPM packages (if Docker build succeeds)
│   └── ...
└── reports/                   # Validation reports
    └── validation_report.json
```

## Support

For issues or questions:
1. Check the logs: `cat claude4rpm.log`
2. Run with verbose mode: `./main.py <command> -v`
3. Review the README.md for detailed documentation
