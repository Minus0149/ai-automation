"""
Test Suite for Automation Project
Task: analyze forms and input elements
"""

import unittest
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main_automation import AutomationRunner
from config import Config

class TestAutomation(unittest.TestCase):
    """Test cases for automation project."""
    
    def setUp(self):
        """Set up test fixtures."""
        Config.setup_directories()
        self.runner = AutomationRunner()
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self.runner, 'cleanup'):
            self.runner.cleanup()
    
    def test_config_loading(self):
        """Test configuration loading."""
        self.assertIsNotNone(Config.PROJECT_ID)
        self.assertIsNotNone(Config.TASK_DESCRIPTION)
        self.assertTrue(Config.BASE_DIR.exists())
    
    def test_directory_creation(self):
        """Test that necessary directories are created."""
        Config.setup_directories()
        self.assertTrue(Config.LOGS_DIR.exists())
        self.assertTrue(Config.SCREENSHOTS_DIR.exists())
        self.assertTrue(Config.RESULTS_DIR.exists())
    
    def test_browser_options(self):
        """Test browser options configuration."""
        chrome_options = Config.get_chrome_options()
        edge_options = Config.get_edge_options()
        
        self.assertIsNotNone(chrome_options)
        self.assertIsNotNone(edge_options)
    
    def test_automation_runner_init(self):
        """Test automation runner initialization."""
        self.assertIsNotNone(self.runner)
        self.assertTrue(hasattr(self.runner, 'run'))

if __name__ == "__main__":
    unittest.main(verbosity=2)
