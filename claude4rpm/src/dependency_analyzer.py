"""
Dependency Analyzer Module
Analyzes Go module dependencies and builds dependency tree
"""

import json
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """Analyzes Go module dependencies"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.dependencies = []
        self.main_module = None

    def analyze(self) -> Dict:
        """
        Analyze all dependencies of the Go project
        Returns a dictionary with main module and all dependencies
        """
        logger.info(f"Analyzing dependencies for {self.project_path}")

        # Check if go.mod exists
        go_mod_path = self.project_path / "go.mod"
        if not go_mod_path.exists():
            raise FileNotFoundError(f"go.mod not found in {self.project_path}")

        # Get main module name
        self.main_module = self._get_main_module()
        logger.info(f"Main module: {self.main_module}")

        # Get all dependencies
        self.dependencies = self._get_all_dependencies()
        logger.info(f"Found {len(self.dependencies)} dependencies")

        return {
            "main_module": self.main_module,
            "dependencies": self.dependencies,
            "total_count": len(self.dependencies)
        }

    def _get_main_module(self) -> str:
        """Get the main module name from go.mod"""
        try:
            result = subprocess.run(
                ["go", "list", "-m"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get main module: {e.stderr}")
            raise

    def _get_all_dependencies(self) -> List[Dict]:
        """Get all dependencies using 'go list -m -json all'"""
        try:
            result = subprocess.run(
                ["go", "list", "-m", "-json", "all"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )

            dependencies = []
            # Parse JSON output (multiple JSON objects)
            decoder = json.JSONDecoder()
            idx = 0
            output = result.stdout.strip()

            while idx < len(output):
                output = output[idx:].lstrip()
                if not output:
                    break
                try:
                    obj, end_idx = decoder.raw_decode(output)
                    idx += end_idx

                    # Skip the main module
                    if obj.get("Path") == self.main_module:
                        continue

                    dep_info = {
                        "path": obj.get("Path", ""),
                        "version": obj.get("Version", ""),
                        "indirect": obj.get("Indirect", False),
                        "replace": None
                    }

                    # Handle replace directives
                    if "Replace" in obj:
                        replace = obj["Replace"]
                        dep_info["replace"] = {
                            "path": replace.get("Path", ""),
                            "version": replace.get("Version", "")
                        }

                    dependencies.append(dep_info)

                except json.JSONDecodeError:
                    break

            return dependencies

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get dependencies: {e.stderr}")
            raise

    def save_to_file(self, output_path: str, format: str = "json"):
        """Save dependency analysis to file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "main_module": self.main_module,
            "dependencies": self.dependencies,
            "total_count": len(self.dependencies)
        }

        if format == "json":
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
        elif format == "yaml":
            import yaml
            with open(output_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Dependency analysis saved to {output_path}")

    def get_dependency_graph(self):
        """Build dependency graph using networkx"""
        try:
            import networkx as nx

            G = nx.DiGraph()
            G.add_node(self.main_module, type="main")

            for dep in self.dependencies:
                dep_path = dep["path"]
                G.add_node(dep_path,
                          version=dep["version"],
                          indirect=dep["indirect"],
                          type="dependency")
                G.add_edge(self.main_module, dep_path)

            return G
        except ImportError:
            logger.warning("networkx not installed, skipping graph generation")
            return None

    def visualize(self, output_path: str):
        """Generate dependency graph visualization"""
        try:
            import networkx as nx
            from graphviz import Digraph

            G = self.get_dependency_graph()
            if G is None:
                logger.warning("Cannot visualize without networkx")
                return

            dot = Digraph(comment='Dependency Graph')
            dot.attr(rankdir='LR')

            # Add main module
            dot.node(self.main_module, self.main_module,
                    shape='box', style='filled', fillcolor='lightblue')

            # Add dependencies (limit to direct dependencies for readability)
            direct_deps = [d for d in self.dependencies if not d["indirect"]]
            for dep in direct_deps[:20]:  # Limit to 20 for readability
                dep_path = dep["path"]
                label = f"{dep_path}\n{dep['version']}"
                dot.node(dep_path, label, shape='ellipse')
                dot.edge(self.main_module, dep_path)

            if len(direct_deps) > 20:
                dot.node("more", f"... and {len(direct_deps) - 20} more",
                        shape='plaintext')

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save as PNG
            dot.render(str(output_path.with_suffix('')), format='png', cleanup=True)
            logger.info(f"Dependency graph saved to {output_path}")

        except ImportError as e:
            logger.warning(f"Cannot visualize: {e}")
