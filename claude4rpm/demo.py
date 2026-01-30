#!/usr/bin/env python3
"""
Example usage of Claude4RPM
Demonstrates basic functionality without requiring a real Go project
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from colorama import init, Fore, Style

init(autoreset=True)


def print_header(text):
    """Print formatted header"""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}{text.center(60)}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")


def demo_spec_generation():
    """Demonstrate SPEC file generation"""
    from spec_generator import SpecGenerator

    print_header("SPEC GENERATION DEMO")

    # Sample dependency
    sample_dep = {
        "path": "github.com/gin-gonic/gin",
        "version": "v1.9.1",
        "indirect": False,
        "replace": None
    }

    print(f"Sample dependency: {sample_dep['path']} {sample_dep['version']}")

    # Generate SPEC
    template_dir = Path(__file__).parent / "templates"
    generator = SpecGenerator(str(template_dir))

    print("\nGenerating SPEC file...")

    try:
        spec_path = generator.generate(sample_dep, "./output/demo")
        print(f"{Fore.GREEN}✓ SPEC file generated: {spec_path}")

        # Show first few lines
        print(f"\n{Fore.YELLOW}First 20 lines of generated SPEC:")
        with open(spec_path) as f:
            lines = f.readlines()[:20]
            for line in lines:
                print(f"  {line.rstrip()}")

    except Exception as e:
        print(f"{Fore.RED}✗ Error: {e}")


def demo_rpm_naming():
    """Demonstrate RPM naming conventions"""
    from spec_generator import SpecGenerator

    print_header("RPM NAMING DEMO")

    template_dir = Path(__file__).parent / "templates"
    generator = SpecGenerator(str(template_dir))

    test_paths = [
        "github.com/gin-gonic/gin",
        "golang.org/x/net",
        "gopkg.in/yaml.v3",
        "github.com/spf13/cobra",
        "k8s.io/client-go",
    ]

    print("Go Import Path → RPM Package Name\n")

    for path in test_paths:
        rpm_name = generator._generate_rpm_name(path)
        print(f"  {path:40} → {rpm_name}")


def demo_dependency_structure():
    """Show example dependency structure"""
    print_header("DEPENDENCY STRUCTURE DEMO")

    example_deps = {
        "main_module": "github.com/example/myapp",
        "dependencies": [
            {
                "path": "github.com/gin-gonic/gin",
                "version": "v1.9.1",
                "indirect": False,
                "replace": None
            },
            {
                "path": "github.com/go-playground/validator/v10",
                "version": "v10.14.0",
                "indirect": True,
                "replace": None
            },
            {
                "path": "golang.org/x/net",
                "version": "v0.0.0-20230425224052-82fc56287a22",
                "indirect": True,
                "replace": None
            }
        ],
        "total_count": 3
    }

    import json
    print("Example dependency analysis output:\n")
    print(json.dumps(example_deps, indent=2))


def main():
    """Run all demos"""
    print(f"{Fore.GREEN}Claude4RPM - Demo Script")
    print(f"{Fore.YELLOW}This demonstrates the tool's functionality without requiring a Go project\n")

    demos = [
        ("RPM Naming Conventions", demo_rpm_naming),
        ("Dependency Structure", demo_dependency_structure),
        ("SPEC File Generation", demo_spec_generation),
    ]

    for title, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"{Fore.RED}✗ Demo failed: {e}")

    print(f"\n{Fore.GREEN}Demo complete!")
    print(f"\n{Fore.YELLOW}To use with a real Go project:")
    print(f"  ./main.py analyze /path/to/go/project")
    print(f"  ./main.py build /path/to/go/project")


if __name__ == '__main__':
    main()
