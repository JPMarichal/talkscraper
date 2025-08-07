"""
Factory Pattern implementation for creating scrapers.

This module implements the Factory pattern to create appropriate
scraper instances based on phase and configuration.
"""

from typing import Union

from core.url_collector import URLCollector
from core.talk_url_extractor import TalkURLExtractor
from core.talk_content_extractor import TalkContentExtractor


class ScraperFactory:
    """
    Factory class for creating scraper instances.
    
    Implements the Factory pattern to encapsulate scraper creation logic
    and provide a clean interface for creating the appropriate scraper
    based on the requested phase.
    """
    
    @staticmethod
    def create_scraper(phase: int, config_path: str = "config.ini") -> Union[URLCollector, TalkURLExtractor, TalkContentExtractor]:
        """
        Create and return the appropriate scraper for the given phase.
        
        Args:
            phase: The scraping phase (1, 2, or 3)
            config_path: Path to configuration file
            
        Returns:
            Appropriate scraper instance for the phase
            
        Raises:
            ValueError: If phase is not 1, 2, or 3
        """
        if phase == 1:
            return URLCollector(config_path)
        elif phase == 2:
            return TalkURLExtractor(config_path)
        elif phase == 3:
            return TalkContentExtractor(config_path)
        else:
            raise ValueError(f"Invalid phase: {phase}. Must be 1, 2, or 3.")
    
    @classmethod
    def create_url_collector(cls, config_path: str = "config.ini") -> URLCollector:
        """Create URL collector instance."""
        return URLCollector(config_path)
    
    @classmethod
    def create_talk_url_extractor(cls, config_path: str = "config.ini") -> TalkURLExtractor:
        """Create talk URL extractor instance."""
        return TalkURLExtractor(config_path)
    
    @classmethod
    def create_talk_content_extractor(cls, config_path: str = "config.ini") -> TalkContentExtractor:
        """Create talk content extractor instance."""
        return TalkContentExtractor(config_path)
