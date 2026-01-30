"""
SPEC Generator Module
Generates RPM SPEC files for Go packages
"""

import re
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import requests

logger = logging.getLogger(__name__)


class SpecGenerator:
    """Generates RPM SPEC files for Go packages"""

    def __init__(self, template_dir: str):
        self.template_dir = Path(template_dir)
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))

    def generate(self, dependency: Dict, output_dir: str) -> str:
        """
        Generate SPEC file for a dependency
        Returns the path to the generated SPEC file
        """
        logger.info(f"Generating SPEC for {dependency['path']}")

        # Prepare package metadata
        metadata = self._prepare_metadata(dependency)

        # Load and render template
        template = self.env.get_template('spec_template.j2')
        spec_content = template.render(**metadata)

        # Save SPEC file
        output_path = Path(output_dir) / f"{metadata['rpm_name']}.spec"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(spec_content)

        logger.info(f"SPEC file generated: {output_path}")
        return str(output_path)

    def _prepare_metadata(self, dependency: Dict) -> Dict:
        """Prepare metadata for SPEC template"""
        go_import_path = dependency["path"]
        version = dependency["version"].lstrip('v')  # Remove 'v' prefix

        # Generate RPM package name
        rpm_name = self._generate_rpm_name(go_import_path)

        # Extract GitHub info if applicable
        github_info = self._parse_github_path(go_import_path)

        # Get package metadata from GitHub API
        pkg_metadata = {}
        if github_info:
            pkg_metadata = self._fetch_github_metadata(
                github_info["owner"],
                github_info["repo"]
            )

        # Prepare metadata
        metadata = {
            "rpm_name": rpm_name,
            "go_import_path": go_import_path,
            "version": version,
            "release": "1",
            "summary": pkg_metadata.get("description", f"Go library for {go_import_path}"),
            "description": pkg_metadata.get("description", f"Go library for {go_import_path}"),
            "license": pkg_metadata.get("license", "Unknown"),
            "url": f"https://{go_import_path}",
            "source_url": self._generate_source_url(go_import_path, dependency["version"]),
            "packager": "Claude4RPM Tool",
            "date": datetime.now().strftime("%a %b %d %Y"),
            "build_requires": [],  # Will be populated from dependencies
            "git_commit": self._extract_commit(dependency["version"]),
        }

        return metadata

    def _generate_rpm_name(self, go_import_path: str) -> str:
        """
        Generate RPM package name from Go import path
        Example: github.com/gin-gonic/gin -> golang-github-gin-gonic-gin
        """
        # Remove protocol if present
        path = go_import_path.replace("https://", "").replace("http://", "")

        # Replace special characters with hyphens
        path = re.sub(r'[/._]', '-', path)

        # Add golang prefix
        return f"golang-{path}".lower()

    def _parse_github_path(self, go_import_path: str) -> Optional[Dict]:
        """Parse GitHub owner and repo from import path"""
        match = re.match(r'github\.com/([^/]+)/([^/]+)', go_import_path)
        if match:
            return {
                "owner": match.group(1),
                "repo": match.group(2)
            }
        return None

    def _fetch_github_metadata(self, owner: str, repo: str) -> Dict:
        """Fetch package metadata from GitHub API"""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                license_info = data.get("license", {})
                return {
                    "description": data.get("description", ""),
                    "license": license_info.get("spdx_id", "Unknown") if license_info else "Unknown",
                    "homepage": data.get("homepage", ""),
                    "stars": data.get("stargazers_count", 0)
                }
        except Exception as e:
            logger.warning(f"Failed to fetch GitHub metadata: {e}")

        return {}

    def _generate_source_url(self, go_import_path: str, version: str) -> str:
        """Generate source tarball URL"""
        if "github.com" in go_import_path:
            # GitHub archive URL
            parts = go_import_path.split("/")
            if len(parts) >= 3:
                owner, repo = parts[1], parts[2]
                return f"https://github.com/{owner}/{repo}/archive/{version}.tar.gz"

        # Fallback to proxy.golang.org
        return f"https://proxy.golang.org/{go_import_path}/@v/{version}.zip"

    def _extract_commit(self, version: str) -> str:
        """Extract commit hash from version string"""
        # Version format: v0.0.0-20210101120000-abcdef123456
        match = re.search(r'-([a-f0-9]{12,})$', version)
        if match:
            return match.group(1)
        return ""

    def generate_batch(self, dependencies: list, output_dir: str) -> list:
        """Generate SPEC files for multiple dependencies"""
        spec_files = []

        for dep in dependencies:
            try:
                spec_path = self.generate(dep, output_dir)
                spec_files.append(spec_path)
            except Exception as e:
                logger.error(f"Failed to generate SPEC for {dep['path']}: {e}")

        logger.info(f"Generated {len(spec_files)} SPEC files")
        return spec_files
