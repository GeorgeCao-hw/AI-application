#!/usr/bin/env python3
"""
Claude4RPM - Go dependency analysis and RPM packaging tool
Main entry point
"""

import argparse
import logging
import sys
from pathlib import Path
from colorama import init, Fore, Style
from tqdm import tqdm

# Initialize colorama
init(autoreset=True)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dependency_analyzer import DependencyAnalyzer
from spec_generator import SpecGenerator
from docker_builder import DockerBuilder
from validator import Validator


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('claude4rpm.log'),
            logging.StreamHandler()
        ]
    )


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}{text.center(60)}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")


def cmd_analyze(args):
    """Analyze dependencies command"""
    print_header("DEPENDENCY ANALYSIS")

    analyzer = DependencyAnalyzer(args.project_path)

    try:
        result = analyzer.analyze()

        print(f"{Fore.GREEN}✓ Main module: {result['main_module']}")
        print(f"{Fore.GREEN}✓ Total dependencies: {result['total_count']}")

        # Save to file
        output_file = Path(args.output) / "dependencies.json"
        analyzer.save_to_file(str(output_file), format="json")
        print(f"{Fore.GREEN}✓ Dependency analysis saved to {output_file}")

        # Print dependency list
        if args.list:
            print(f"\n{Fore.YELLOW}Dependencies:")
            for dep in result['dependencies'][:20]:  # Show first 20
                indirect = " (indirect)" if dep['indirect'] else ""
                print(f"  - {dep['path']} {dep['version']}{indirect}")
            if result['total_count'] > 20:
                print(f"  ... and {result['total_count'] - 20} more")

    except Exception as e:
        print(f"{Fore.RED}✗ Error: {e}")
        sys.exit(1)


def cmd_generate_specs(args):
    """Generate SPEC files command"""
    print_header("SPEC FILE GENERATION")

    # Load dependencies
    analyzer = DependencyAnalyzer(args.project_path)
    result = analyzer.analyze()

    # Generate SPEC files
    template_dir = Path(__file__).parent / "templates"
    output_dir = Path(args.output) / "specs"

    generator = SpecGenerator(str(template_dir))

    print(f"Generating SPEC files for {len(result['dependencies'])} dependencies...")

    spec_files = []
    with tqdm(total=len(result['dependencies']), desc="Generating") as pbar:
        for dep in result['dependencies']:
            try:
                spec_path = generator.generate(dep, str(output_dir))
                spec_files.append(spec_path)
            except Exception as e:
                logging.error(f"Failed to generate SPEC for {dep['path']}: {e}")
            pbar.update(1)

    print(f"{Fore.GREEN}✓ Generated {len(spec_files)} SPEC files in {output_dir}")


def cmd_build(args):
    """Full build pipeline command"""
    print_header("FULL BUILD PIPELINE")

    # Step 1: Analyze dependencies
    print(f"{Fore.YELLOW}Step 1: Analyzing dependencies...")
    analyzer = DependencyAnalyzer(args.project_path)
    result = analyzer.analyze()
    print(f"{Fore.GREEN}✓ Found {result['total_count']} dependencies")

    # Save dependency analysis
    dep_file = Path(args.output) / "dependencies.json"
    analyzer.save_to_file(str(dep_file))

    # Step 2: Generate SPEC files
    print(f"\n{Fore.YELLOW}Step 2: Generating SPEC files...")
    template_dir = Path(__file__).parent / "templates"
    output_dir = Path(args.output) / "specs"

    generator = SpecGenerator(str(template_dir))

    spec_files = []
    with tqdm(total=len(result['dependencies']), desc="Generating") as pbar:
        for dep in result['dependencies']:
            try:
                spec_path = generator.generate(dep, str(output_dir))
                spec_files.append(spec_path)
            except Exception as e:
                logging.error(f"Failed to generate SPEC for {dep['path']}: {e}")
            pbar.update(1)

    print(f"{Fore.GREEN}✓ Generated {len(spec_files)} SPEC files")

    # Step 3: Build RPMs (if Docker is available)
    if not args.skip_build:
        print(f"\n{Fore.YELLOW}Step 3: Building RPMs in Docker...")

        try:
            with DockerBuilder() as builder:
                # Setup volumes
                volumes = {
                    str(output_dir.resolve()): {'bind': '/mnt/specs', 'mode': 'ro'},
                    str((Path(args.output) / "rpms").resolve()): {'bind': '/mnt/rpms', 'mode': 'rw'}
                }

                builder.start_container(volumes=volumes, keep_running=args.keep_container)

                # Build RPMs
                build_results = []
                with tqdm(total=len(spec_files), desc="Building") as pbar:
                    for spec_file in spec_files:
                        try:
                            result = builder.build_rpm(spec_file)
                            build_results.append(result)
                        except Exception as e:
                            logging.error(f"Build failed for {spec_file}: {e}")
                        pbar.update(1)

                successful = sum(1 for r in build_results if r.get("success", False))
                print(f"{Fore.GREEN}✓ Built {successful}/{len(spec_files)} RPMs successfully")

        except Exception as e:
            print(f"{Fore.RED}✗ Docker build failed: {e}")
            print(f"{Fore.YELLOW}  You can build manually using the generated SPEC files")

    print(f"\n{Fore.GREEN}✓ Build pipeline complete!")
    print(f"  Output directory: {args.output}")


def cmd_validate(args):
    """Validate SPEC files and RPMs"""
    print_header("VALIDATION")

    spec_files = list(Path(args.specs_dir).glob("*.spec"))

    if not spec_files:
        print(f"{Fore.RED}✗ No SPEC files found in {args.specs_dir}")
        sys.exit(1)

    print(f"Found {len(spec_files)} SPEC files to validate")

    try:
        with DockerBuilder() as builder:
            volumes = {
                str(Path(args.specs_dir).resolve()): {'bind': '/mnt/specs', 'mode': 'ro'}
            }
            builder.start_container(volumes=volumes)

            validator = Validator(builder)

            # Validate all SPEC files
            with tqdm(total=len(spec_files), desc="Validating") as pbar:
                for spec_file in spec_files:
                    validator.validate_full(str(spec_file))
                    pbar.update(1)

            # Save report
            report_file = Path(args.output) / "reports" / "validation_report.json"
            validator.save_report(str(report_file))

            # Print summary
            validator.print_summary()

            print(f"{Fore.GREEN}✓ Validation report saved to {report_file}")

    except Exception as e:
        print(f"{Fore.RED}✗ Validation failed: {e}")
        sys.exit(1)


def cmd_visualize(args):
    """Visualize dependency graph"""
    print_header("DEPENDENCY VISUALIZATION")

    analyzer = DependencyAnalyzer(args.project_path)
    analyzer.analyze()

    output_file = Path(args.output) / "dependency_graph.png"

    try:
        analyzer.visualize(str(output_file))
        print(f"{Fore.GREEN}✓ Dependency graph saved to {output_file}")
    except Exception as e:
        print(f"{Fore.RED}✗ Visualization failed: {e}")
        print(f"{Fore.YELLOW}  Make sure graphviz is installed")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Claude4RPM - Go dependency analysis and RPM packaging tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze',
                                          help='Analyze Go project dependencies')
    analyze_parser.add_argument('project_path',
                               help='Path to Go project')
    analyze_parser.add_argument('-o', '--output', default='./output',
                               help='Output directory')
    analyze_parser.add_argument('-l', '--list', action='store_true',
                               help='List dependencies')

    # Generate SPEC files command
    generate_parser = subparsers.add_parser('generate-specs',
                                           help='Generate RPM SPEC files')
    generate_parser.add_argument('project_path',
                                help='Path to Go project')
    generate_parser.add_argument('-o', '--output', default='./output',
                                help='Output directory')

    # Build command
    build_parser = subparsers.add_parser('build',
                                        help='Full build pipeline')
    build_parser.add_argument('project_path',
                             help='Path to Go project')
    build_parser.add_argument('-o', '--output', default='./output',
                             help='Output directory')
    build_parser.add_argument('--skip-build', action='store_true',
                             help='Skip Docker build step')
    build_parser.add_argument('--keep-container', action='store_true',
                             help='Keep Docker container running')

    # Validate command
    validate_parser = subparsers.add_parser('validate',
                                           help='Validate SPEC files and RPMs')
    validate_parser.add_argument('--specs-dir', required=True,
                                help='Directory containing SPEC files')
    validate_parser.add_argument('-o', '--output', default='./output',
                                help='Output directory for reports')

    # Visualize command
    visualize_parser = subparsers.add_parser('visualize',
                                            help='Visualize dependency graph')
    visualize_parser.add_argument('project_path',
                                 help='Path to Go project')
    visualize_parser.add_argument('-o', '--output', default='./output',
                                 help='Output directory')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Setup logging
    setup_logging(args.verbose)

    # Execute command
    commands = {
        'analyze': cmd_analyze,
        'generate-specs': cmd_generate_specs,
        'build': cmd_build,
        'validate': cmd_validate,
        'visualize': cmd_visualize
    }

    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logging.exception("Unexpected error")
        print(f"{Fore.RED}✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
