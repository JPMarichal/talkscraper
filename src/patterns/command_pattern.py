"""
Command Pattern implementation for TalkScraper operations.

This module implements the Command pattern to encapsulate
scraping operations as objects, allowing for queuing,
logging, and undo operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from patterns.scraper_factory import ScraperFactory


class Command(ABC):
    """Abstract base class for all commands."""
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Execute the command."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get a human-readable description of the command."""
        pass


class URLCollectionCommand(Command):
    """Command for Phase 1: URL Collection."""
    
    def __init__(self, languages: List[str], config_path: str):
        self.languages = languages
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
    
    def execute(self) -> Dict[str, Any]:
        """Execute URL collection for specified languages."""
        start_time = datetime.now()
        self.logger.info(f"Starting URL collection for languages: {', '.join(self.languages)}")
        
        try:
            collector = ScraperFactory.create_url_collector(self.config_path)
            urls = collector.collect_all_urls(self.languages)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            return {
                'success': True,
                'urls': urls,
                'languages': self.languages,
                'duration': duration.total_seconds(),
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"URL collection failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'languages': self.languages
            }
    
    def get_description(self) -> str:
        """Get command description."""
        return f"Collect conference URLs for languages: {', '.join(self.languages)}"


class TalkURLExtractionCommand(Command):
    """Command for Phase 2: Talk URL Extraction."""
    
    def __init__(self, languages: List[str], config_path: str):
        self.languages = languages
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
    
    def execute(self) -> Dict[str, Any]:
        """Execute talk URL extraction for specified languages."""
        start_time = datetime.now()
        self.logger.info(f"Starting talk URL extraction for languages: {', '.join(self.languages)}")
        
        try:
            extractor = ScraperFactory.create_talk_url_extractor(self.config_path)
            results = extractor.extract_all_talk_urls(self.languages)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            return {
                'success': True,
                'results': results,
                'languages': self.languages,
                'duration': duration.total_seconds(),
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Talk URL extraction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'languages': self.languages
            }
    
    def get_description(self) -> str:
        """Get command description."""
        return f"Extract talk URLs for languages: {', '.join(self.languages)}"


class ContentExtractionCommand(Command):
    """Command for Phase 3: Content Extraction."""
    
    def __init__(self, config_path: str, languages: List[str], limit: Optional[int] = None,
                 batch_size: int = 12, skip_notes: bool = False):
        self.config_path = config_path
        self.languages = languages
        self.limit = limit
        self.batch_size = batch_size
        self.skip_notes = skip_notes
        self.logger = logging.getLogger(__name__)

    def execute(self) -> Dict[str, Any]:
        """Execute content extraction with specified parameters."""
        start_time = datetime.now()
        self.logger.info(
            "Starting content extraction for languages %s (limit: %s, batch_size: %s, skip_notes: %s)",
            ', '.join(self.languages),
            self.limit,
            self.batch_size,
            self.skip_notes
        )
        
        try:
            extractor = ScraperFactory.create_talk_content_extractor(
                self.config_path,
                skip_notes=self.skip_notes
            )
        
            # Get unprocessed talk URLs
            all_urls = extractor.get_all_unprocessed_talk_urls(self.languages, limit=self.limit)
        
            if not all_urls:
                return {
                    'success': True,
                    'message': 'No unprocessed talks found',
                    'processed_count': 0,
                    'duration': 0
                }
            
            # Extract talks in batches
            results = extractor.extract_talks_batch(all_urls, batch_size=self.batch_size)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            return {
                'success': True,
                'results': results,
                'processed_count': len(all_urls),
                'languages': self.languages,
                'limit': self.limit,
                'batch_size': self.batch_size,
                'skip_notes': self.skip_notes,
                'duration': duration.total_seconds(),
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Content extraction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'languages': self.languages,
                'limit': self.limit,
                'batch_size': self.batch_size,
                'skip_notes': self.skip_notes
            }
    
    def get_description(self) -> str:
        """Get command description."""
        limit_str = f" (limit: {self.limit})" if self.limit else ""
        notes_str = " (skip notes)" if self.skip_notes else ""
        return f"Extract talk content for {', '.join(self.languages)} with batch size {self.batch_size}{limit_str}{notes_str}"


class CommandInvoker:
    """
    Invoker class that executes commands and maintains history.
    
    This class can be extended to support queuing, undo operations,
    and command logging.
    """
    
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
    
    def execute_command(self, command: Command) -> Dict[str, Any]:
        """
        Execute a command and store the result in history.
        
        Args:
            command: The command to execute
            
        Returns:
            Command execution result
        """
        description = command.get_description()
        self.logger.info(f"Executing command: {description}")
        
        result = command.execute()
        
        # Store in history
        history_entry = {
            'command_description': description,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        self.history.append(history_entry)
        
        return result
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get command execution history."""
        return self.history.copy()
    
    def clear_history(self):
        """Clear command execution history."""
        self.history.clear()
