"""
Unit tests for SPEC generator
"""

import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spec_generator import SpecGenerator


class TestSpecGenerator(unittest.TestCase):
    """Test cases for SpecGenerator"""

    def setUp(self):
        """Setup test fixtures"""
        self.template_dir = Path(__file__).parent.parent / "templates"
        self.generator = SpecGenerator(str(self.template_dir))

    def test_generate_rpm_name(self):
        """Test RPM name generation"""
        test_cases = [
            ("github.com/gin-gonic/gin", "golang-github-com-gin-gonic-gin"),
            ("golang.org/x/net", "golang-golang-org-x-net"),
            ("gopkg.in/yaml.v3", "golang-gopkg-in-yaml-v3"),
        ]

        for import_path, expected_name in test_cases:
            result = self.generator._generate_rpm_name(import_path)
            self.assertEqual(result, expected_name)

    def test_parse_github_path(self):
        """Test parsing GitHub paths"""
        result = self.generator._parse_github_path("github.com/gin-gonic/gin")

        self.assertIsNotNone(result)
        self.assertEqual(result["owner"], "gin-gonic")
        self.assertEqual(result["repo"], "gin")

    def test_parse_non_github_path(self):
        """Test parsing non-GitHub paths"""
        result = self.generator._parse_github_path("golang.org/x/net")
        self.assertIsNone(result)

    def test_extract_commit(self):
        """Test extracting commit hash from version"""
        test_cases = [
            ("v0.0.0-20210101120000-abcdef123456", "abcdef123456"),
            ("v1.9.1", ""),
            ("v0.1.0-20230101-1234567890ab", "1234567890ab"),
        ]

        for version, expected_commit in test_cases:
            result = self.generator._extract_commit(version)
            self.assertEqual(result, expected_commit)

    @patch('requests.get')
    def test_fetch_github_metadata(self, mock_get):
        """Test fetching metadata from GitHub API"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "description": "Test package",
            "license": {"spdx_id": "MIT"},
            "homepage": "https://example.com",
            "stargazers_count": 1000
        }
        mock_get.return_value = mock_response

        result = self.generator._fetch_github_metadata("gin-gonic", "gin")

        self.assertEqual(result["description"], "Test package")
        self.assertEqual(result["license"], "MIT")
        self.assertEqual(result["stars"], 1000)

    def test_prepare_metadata(self):
        """Test preparing metadata for template"""
        dependency = {
            "path": "github.com/gin-gonic/gin",
            "version": "v1.9.1",
            "indirect": False,
            "replace": None
        }

        with patch.object(self.generator, '_fetch_github_metadata', return_value={}):
            metadata = self.generator._prepare_metadata(dependency)

        self.assertEqual(metadata["go_import_path"], "github.com/gin-gonic/gin")
        self.assertEqual(metadata["version"], "1.9.1")  # v prefix removed
        self.assertIn("golang-github", metadata["rpm_name"])


if __name__ == '__main__':
    unittest.main()
