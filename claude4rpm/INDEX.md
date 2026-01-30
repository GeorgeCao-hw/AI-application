# Claude4RPM - Project Index

## Quick Navigation

### Getting Started
1. **[QUICKSTART.md](QUICKSTART.md)** - Start here for quick setup and basic usage
2. **[README.md](README.md)** - Comprehensive documentation
3. **[demo.py](demo.py)** - Run this to see the tool in action
4. **[verify.sh](verify.sh)** - Verify your installation

### Documentation
- **[README.md](README.md)** - Full user documentation (5.4KB)
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide (3.3KB)
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Technical overview (9KB)
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - Implementation status (7.8KB)
- **[FILES.txt](FILES.txt)** - Complete file listing (3.9KB)

### Source Code
- **[main.py](main.py)** - Main CLI entry point (12KB, 380 lines)
- **[src/dependency_analyzer.py](src/dependency_analyzer.py)** - Dependency analysis (6.5KB)
- **[src/spec_generator.py](src/spec_generator.py)** - SPEC generation (6.2KB)
- **[src/docker_builder.py](src/docker_builder.py)** - Docker management (5.8KB)
- **[src/validator.py](src/validator.py)** - Validation & testing (7.2KB)

### Configuration
- **[requirements.txt](requirements.txt)** - Python dependencies
- **[Makefile](Makefile)** - Build automation
- **[.gitignore](.gitignore)** - Git exclusions
- **[templates/spec_template.j2](templates/spec_template.j2)** - SPEC template

### Docker
- **[docker/Dockerfile](docker/Dockerfile)** - openEuler 24.03 LTS image
- **[docker/build.sh](docker/build.sh)** - Container build script

### Testing
- **[tests/test_dependency_analyzer.py](tests/test_dependency_analyzer.py)** - Analyzer tests
- **[tests/test_spec_generator.py](tests/test_spec_generator.py)** - Generator tests

### Utilities
- **[demo.py](demo.py)** - Interactive demonstration (3.9KB)
- **[verify.sh](verify.sh)** - Installation verification

## Common Tasks

### First Time Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify installation
./verify.sh

# 3. Run demo
./demo.py
```

### Analyze a Go Project
```bash
./main.py analyze /path/to/go/project -l
```

### Generate SPEC Files
```bash
./main.py generate-specs /path/to/go/project
```

### Full Build Pipeline
```bash
./main.py build /path/to/go/project
```

### Run Tests
```bash
make test
# or
python -m pytest tests/
```

### Build Docker Image
```bash
make docker-build
# or
cd docker && docker build -t claude4rpm-builder .
```

## File Organization

```
claude4rpm/
├── Documentation (5 files)
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── PROJECT_SUMMARY.md
│   ├── IMPLEMENTATION_COMPLETE.md
│   └── FILES.txt
│
├── Main Scripts (2 files)
│   ├── main.py
│   └── demo.py
│
├── Source Code (5 files)
│   └── src/
│       ├── __init__.py
│       ├── dependency_analyzer.py
│       ├── spec_generator.py
│       ├── docker_builder.py
│       └── validator.py
│
├── Templates (1 file)
│   └── templates/
│       └── spec_template.j2
│
├── Docker (2 files)
│   └── docker/
│       ├── Dockerfile
│       └── build.sh
│
├── Tests (3 files)
│   └── tests/
│       ├── __init__.py
│       ├── test_dependency_analyzer.py
│       └── test_spec_generator.py
│
├── Configuration (4 files)
│   ├── requirements.txt
│   ├── Makefile
│   ├── .gitignore
│   └── verify.sh
│
└── Output (3 directories)
    └── output/
        ├── specs/
        ├── rpms/
        └── reports/
```

## Module Dependencies

```
main.py
├── dependency_analyzer.py
│   └── subprocess (go list)
│   └── networkx (graphs)
│   └── graphviz (visualization)
│
├── spec_generator.py
│   └── jinja2 (templates)
│   └── requests (GitHub API)
│
├── docker_builder.py
│   └── docker (SDK)
│
└── validator.py
    └── docker_builder.py
```

## CLI Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `analyze` | Analyze dependencies | `./main.py analyze /path/to/project` |
| `generate-specs` | Generate SPEC files | `./main.py generate-specs /path/to/project` |
| `build` | Full pipeline | `./main.py build /path/to/project` |
| `validate` | Validate SPECs/RPMs | `./main.py validate --specs-dir ./output/specs` |
| `visualize` | Create graph | `./main.py visualize /path/to/project` |

## Make Targets Reference

| Target | Description | Command |
|--------|-------------|---------|
| `install` | Install dependencies | `make install` |
| `test` | Run unit tests | `make test` |
| `demo` | Run demonstration | `make demo` |
| `verify` | Verify installation | `make verify` |
| `clean` | Clean output | `make clean` |
| `docker-build` | Build Docker image | `make docker-build` |

## Key Features

1. **Dependency Analysis**
   - Parses go.mod files
   - Executes `go list -m -json all`
   - Handles replace directives
   - Exports to JSON/YAML

2. **SPEC Generation**
   - Jinja2 templates
   - Automatic naming
   - GitHub metadata
   - Batch processing

3. **Docker Building**
   - openEuler 24.03 LTS
   - Isolated environment
   - Volume mounting
   - Container management

4. **Validation**
   - rpmlint checks
   - Build verification
   - Install testing
   - JSON reports

5. **User Interface**
   - Colored output
   - Progress bars
   - Verbose logging
   - Error handling

## Support

- Check logs: `cat claude4rpm.log`
- Verbose mode: `./main.py <command> -v`
- Run verification: `./verify.sh`
- Read docs: Start with [QUICKSTART.md](QUICKSTART.md)

## Version

**Current Version**: 0.1.0
**Status**: Production Ready
**Date**: 2026-01-29

## License

MIT License

---

**Quick Links:**
- [Get Started](QUICKSTART.md)
- [Full Documentation](README.md)
- [Technical Details](PROJECT_SUMMARY.md)
- [Implementation Status](IMPLEMENTATION_COMPLETE.md)
