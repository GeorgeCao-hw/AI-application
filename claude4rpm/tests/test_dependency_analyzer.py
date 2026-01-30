"""
Unit tests for dependency analyzer
"""

import unittest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dependency_analyzer import DependencyAnalyzer


class TestDependencyAnalyzer(unittest.TestCase):
    """Test cases for DependencyAnalyzer"""

    def setUp(self):
        """Setup test fixtures"""
        self.test_project_path = "/tmp/test-go-project"

    @patch('subprocess.run')
    def test_get_main_module(self, mock_run):
        """Test getting main module name"""
        mock_run.return_value = MagicMock(
            stdout="github.com/example/project\n",
            returncode=0
        )

        analyzer = DependencyAnalyzer(self.test_project_path)
        result = analyzer._get_main_module()

        self.assertEqual(result, "github.com/example/project")
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_get_all_dependencies(self, mock_run):
        """Test getting all dependencies"""
        mock_output = '''
        {"Path": "github.com/example/project", "Version": "v1.0.0"}
        {"Path": "github.com/gin-gonic/gin", "Version": "v1.9.1", "Indirect": false}
        {"Path": "github.com/go-playground/validator", "Version": "v10.14.0", "Indirect": true}
        '''

        mock_run.return_value = MagicMock(
            stdout=mock_output,
            returncode=0
        )

        analyzer = DependencyAnalyzer(self.test_project_path)
        analyzer.main_module = "github.com/example/project"
        dependencies = analyzer._get_all_dependencies()

        self.assertEqual(len(dependencies), 2)
        self.assertEqual(dependencies[0]["path"], "github.com/gin-gonic/gin")
        self.assertFalse(dependencies[0]["indirect"])
        self.assertTrue(dependencies[1]["indirect"])

    def test_save_to_file_json(self):
        """Test saving analysis to JSON file"""
        analyzer = DependencyAnalyzer(self.test_project_path)
        analyzer.main_module = "github.com/example/project"
        analyzer.dependencies = [
            {"path": "github.com/gin-gonic/gin", "version": "v1.9.1", "indirect": False}
        ]

        output_file = "/tmp/test_deps.json"
        analyzer.save_to_file(output_file, format="json")

        # Verify file was created
        self.assertTrue(Path(output_file).exists())

        # Verify content
        with open(output_file) as f:
            data = json.load(f)
            self.assertEqual(data["main_module"], "github.com/example/project")
            self.assertEqual(len(data["dependencies"]), 1)

        # Cleanup
        Path(output_file).unlink()


if __name__ == '__main__':
    unittest.main()
