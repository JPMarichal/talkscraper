"""
Configuration Manager for TalkScraper

Handles loading and accessing configuration parameters.
"""

import configparser
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Manages application configuration using ConfigParser."""
    
    def __init__(self, config_path: str = "config.ini"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config = configparser.ConfigParser()
        
        # Load configuration or create from template
        if self.config_path.exists():
            self.config.read(self.config_path)
        else:
            self._create_from_template()
    
    def _create_from_template(self):
        """Create config.ini from template if it doesn't exist."""
        template_path = Path("config_template.ini")
        if template_path.exists():
            self.config.read(template_path)
            # Save as config.ini
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
        else:
            raise FileNotFoundError("No config.ini or config_template.ini found")
    
    def get_base_url(self, language: str) -> str:
        """Get base URL for specified language."""
        return self.config.get('DEFAULT', f'base_url_{language}')
    
    def get_output_dir(self, language: str = None) -> str:
        """Get output directory path."""
        if language:
            return self.config.get('DEFAULT', f'{language}_dir')
        return self.config.get('DEFAULT', 'output_dir')
    
    def get_db_path(self) -> str:
        """Get database file path."""
        return self.config.get('DEFAULT', 'db_file')
    
    def get_user_agent(self) -> str:
        """Get user agent string."""
        return self.config.get('SCRAPING', 'user_agent')
    
    def get_conference_link_selector(self) -> str:
        """Get CSS selector for conference links."""
        return self.config.get('SCRAPING', 'conference_link_selector')
    
    def get_talk_link_selector(self) -> str:
        """Get CSS selector for talk links."""
        return self.config.get('SCRAPING', 'talk_link_selector')
    
    def get_decade_link_selector(self) -> str:
        """Get CSS selector for decade archive links."""
        return self.config.get('SCRAPING', 'decade_link_selector')
    
    def get_concurrent_downloads(self) -> int:
        """Get number of concurrent downloads."""
        return self.config.getint('DEFAULT', 'concurrent_downloads')
    
    def get_request_delay(self) -> float:
        """Get delay between requests."""
        return self.config.getfloat('DEFAULT', 'request_delay')
    
    def get_retry_config(self) -> tuple:
        """Get retry configuration (attempts, delay)."""
        attempts = self.config.getint('DEFAULT', 'retry_attempts')
        delay = self.config.getfloat('DEFAULT', 'retry_delay')
        return attempts, delay
    
    def get_content_retry_config(self) -> tuple:
        """Get retry configuration for content extraction (attempts, delay)."""
        default_attempts = int(self.config['DEFAULT'].get('retry_attempts', 3))
        default_delay = float(self.config['DEFAULT'].get('retry_delay', 2.0))
        if self.config.has_section('CONTENT'):
            attempts = int(self.config['CONTENT'].get('retry_attempts', default_attempts))
            delay = float(self.config['CONTENT'].get('retry_delay', default_delay))
        else:
            attempts = default_attempts
            delay = default_delay
        return attempts, delay
    
    def get_log_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return {
            'level': self.config.get('DEFAULT', 'log_level'),
            'file': self.config.get('DEFAULT', 'log_file')
        }
    
    def get_selenium_config(self) -> Dict[str, Any]:
        """Get Selenium configuration."""
        return {
            'timeout': self.config.getint('SCRAPING', 'selenium_timeout'),
            'implicit_wait': self.config.getint('SCRAPING', 'selenium_implicit_wait'),
            'headless': self.config.getboolean('SCRAPING', 'selenium_headless')
        }
