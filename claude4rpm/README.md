# Claude4RPM

Go dependency analysis and RPM packaging tool for openEuler 24.03 LTS.

## Features

- **Dependency Analysis**: Recursively analyze all Go module dependencies
- **SPEC Generation**: Automatically generate RPM SPEC files following openEuler standards
- **Docker Integration**: Build and test RPMs in isolated openEuler containers
- **Validation**: Comprehensive validation with rpmlint and installation tests
- **Visualization**: Generate dependency graphs

## Installation

### Prerequisites

- Python 3.8+
- Docker (for building RPMs)
- Go 1.20+ (for analyzing Go projects)

### Setup

```bash
# Clone or navigate to the project
cd claude4rpm

# Install Python dependencies
pip install -r requirements.txt
```

## Usage

### Basic Commands

#### 1. Analyze Dependencies

Analyze a Go project and list all dependencies:

```bash
./main.py analyze /path/to/go/project
```

Options:
- `-o, --output`: Output directory (default: ./output)
- `-l, --list`: Print dependency list
- `-v, --verbose`: Enable verbose logging

#### 2. Generate SPEC Files

Generate RPM SPEC files for all dependencies:

```bash
./main.py generate-specs /path/to/go/project
```

This will create SPEC files in `./output/specs/`

#### 3. Full Build Pipeline

Run the complete pipeline (analyze + generate + build):

```bash
./main.py build /path/to/go/project
```

Options:
- `--skip-build`: Skip Docker build step (only analyze and generate SPECs)
- `--keep-container`: Keep Docker container running for debugging

#### 4. Validate SPEC Files

Validate generated SPEC files and test RPM builds:

```bash
./main.py validate --specs-dir ./output/specs
```

#### 5. Visualize Dependencies

Generate a dependency graph visualization:

```bash
./main.py visualize /path/to/go/project
```

Requires `graphviz` to be installed.

## Example Workflow

```bash
# 1. Analyze a Go project
./main.py analyze ~/projects/my-go-app -l

# 2. Generate SPEC files
./main.py generate-specs ~/projects/my-go-app

# 3. Build RPMs in Docker
./main.py build ~/projects/my-go-app

# 4. Validate the results
./main.py validate --specs-dir ./output/specs

# 5. Visualize dependencies
./main.py visualize ~/projects/my-go-app
```

## Output Structure

```
output/
├── dependencies.json          # Dependency analysis results
├── specs/                     # Generated SPEC files
│   ├── golang-github-gin-gonic-gin.spec
│   └── ...
├── rpms/                      # Built RPM packages
│   ├── golang-github-gin-gonic-gin-1.9.1-1.noarch.rpm
│   └── ...
└── reports/                   # Validation reports
    └── validation_report.json
```

## Docker Environment

The tool uses a Docker container based on openEuler 24.03 LTS with:
- rpm-build, rpmdevtools, rpmlint
- Go 1.20+
- Git, wget, tar, spectool
- GOPROXY configured for China (goproxy.cn)

### Building the Docker Image

The image is built automatically on first use, or manually:

```bash
cd docker
docker build -t claude4rpm-builder .
```

## SPEC File Template

The tool generates SPEC files following openEuler Go packaging guidelines:

- Package naming: `golang-<import-path-with-hyphens>`
- Automatic license detection from GitHub
- Support for replace directives
- Proper BuildRequires handling
- Standard devel subpackage

## Configuration

### Go Proxy

The default GOPROXY is set to `https://goproxy.cn,direct` for better performance in China. You can modify this in:
- `docker/Dockerfile` (for container builds)
- Environment variables (for local analysis)

### Template Customization

Edit `templates/spec_template.j2` to customize the SPEC file format.

## Troubleshooting

### Docker Issues

If Docker commands fail:
```bash
# Check Docker is running
docker ps

# Check permissions
sudo usermod -aG docker $USER
# Then log out and back in
```

### Go Module Issues

If dependency analysis fails:
```bash
# Ensure go.mod exists
cd /path/to/project
go mod init  # if needed
go mod tidy

# Update dependencies
go get -u ./...
```

### Build Failures

Check the logs:
```bash
# View detailed logs
./main.py build /path/to/project -v

# Check individual SPEC file
rpmlint output/specs/package-name.spec
```

## Limitations

- Only supports Go modules (requires go.mod)
- GitHub-hosted packages get better metadata
- Some packages may require manual SPEC adjustments
- Network access required for downloading sources

## Development

### Project Structure

```
claude4rpm/
├── main.py                    # CLI entry point
├── src/
│   ├── dependency_analyzer.py # Dependency analysis
│   ├── spec_generator.py      # SPEC file generation
│   ├── docker_builder.py      # Docker container management
│   └── validator.py           # Validation and testing
├── templates/
│   └── spec_template.j2       # SPEC file template
├── docker/
│   ├── Dockerfile             # openEuler build environment
│   └── build.sh               # Container build script
└── tests/                     # Unit tests
```

### Running Tests

```bash
python -m pytest tests/
```

## Contributing

Contributions are welcome! Please:
1. Follow the existing code style
2. Add tests for new features
3. Update documentation

## License

MIT License

## Acknowledgments

- Inspired by go2rpm and other Go packaging tools
- Built for openEuler 24.03 LTS
- Uses Jinja2 for templating
- Docker for isolated builds
