"""
Unit tests for ConfigManager class.

Tests the configuration management functionality including
file loading, default values, and error handling.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from utils.config_manager import ConfigManager


class TestConfigManager:
    """Test suite for ConfigManager class."""
    
    @pytest.mark.unit
    def test_init_with_existing_config(self, test_config_file):
        """Test initialization with an existing config file."""
        config_manager = ConfigManager(test_config_file)
        
        assert config_manager.config_path == Path(test_config_file)
        assert config_manager.config is not None
        
    @pytest.mark.unit
    def test_init_with_nonexistent_config_and_template(self, temp_dir):
        """Test initialization when config.ini doesn't exist but template does."""
        # Create template file
        template_path = temp_dir / "config_template.ini"
        template_content = """[DEFAULT]
base_url_eng = https://example.com/eng
base_url_spa = https://example.com/spa

[SCRAPING]
user_agent = Test-Agent
"""
        template_path.write_text(template_content)
        
        config_path = temp_dir / "config.ini"
        
        # Change to temp directory to find template
        with patch('pathlib.Path.cwd', return_value=temp_dir):
            config_manager = ConfigManager(str(config_path))
        
        assert config_path.exists()
        assert config_manager.get_base_url('eng') == 'https://example.com/eng'
        
    @pytest.mark.unit
    def test_init_without_config_or_template(self, temp_dir):
        """Test initialization when neither config nor template exists."""
        config_path = temp_dir / "config.ini"
        
        with pytest.raises(FileNotFoundError):
            ConfigManager(str(config_path))
            
    @pytest.mark.unit
    def test_get_base_url(self, config_manager):
        """Test getting base URLs for different languages."""
        eng_url = config_manager.get_base_url('eng')
        spa_url = config_manager.get_base_url('spa')
        
        assert eng_url == 'https://test.example.com/eng'
        assert spa_url == 'https://test.example.com/spa'
        
    @pytest.mark.unit
    def test_get_output_dir_with_language(self, config_manager):
        """Test getting output directory with specific language."""
        eng_dir = config_manager.get_output_dir('eng')
        spa_dir = config_manager.get_output_dir('spa')
        
        assert eng_dir == 'conf/eng'
        assert spa_dir == 'conf/spa'
        
    @pytest.mark.unit
    def test_get_output_dir_without_language(self, config_manager):
        """Test getting general output directory."""
        output_dir = config_manager.get_output_dir()
        
        assert output_dir == 'conf'
        
    @pytest.mark.unit
    def test_get_db_path(self, config_manager):
        """Test getting database file path."""
        db_path = config_manager.get_db_path()
        
        assert db_path == 'test_talkscraper.db'
        
    @pytest.mark.unit
    def test_get_user_agent(self, config_manager):
        """Test getting user agent string."""
        user_agent = config_manager.get_user_agent()
        
        assert user_agent == 'TalkScraper-Test/1.0'
        
    @pytest.mark.unit
    def test_get_conference_link_selector(self, config_manager):
        """Test getting conference link CSS selector."""
        selector = config_manager.get_conference_link_selector()
        
        assert selector == 'a.test-conference'
        
    @pytest.mark.unit
    def test_get_talk_link_selector(self, config_manager):
        """Test getting talk link CSS selector."""
        selector = config_manager.get_talk_link_selector()
        
        assert selector == 'a.test-talk'
        
    @pytest.mark.unit
    def test_get_decade_link_selector(self, config_manager):
        """Test getting decade link CSS selector."""
        selector = config_manager.get_decade_link_selector()
        
        assert selector == 'a.test-decade'
        
    @pytest.mark.unit
    def test_missing_config_value(self, config_manager):
        """Test behavior when requesting a missing configuration value."""
        with pytest.raises(Exception):  # ConfigParser will raise an exception
            config_manager.config.get('DEFAULT', 'nonexistent_key')
            
    @pytest.mark.unit
    def test_config_file_permissions(self, temp_dir):
        """Test behavior with config file permission issues."""
        config_path = temp_dir / "readonly_config.ini"
        config_path.write_text("[DEFAULT]\ntest=value")
        config_path.chmod(0o444)  # Read-only
        
        # Should still be able to read
        config_manager = ConfigManager(str(config_path))
        assert config_manager.config is not None
