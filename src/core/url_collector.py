"""
TalkScraper - URL Collection Module

This module handles the collection of conference and talk URLs
from the Church of Jesus Christ of Latter-day Saints website.

Phase 1: Primary URL Collection
- Main conference page scraping
- Decade archive page processing
- URL compilation and storage
"""

import logging
import sqlite3
from pathlib import Path
from typing import List, Set, Tuple, Dict
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from utils.config_manager import ConfigManager
from utils.database_manager import DatabaseManager
from utils.logger_setup import setup_logger


class URLCollector:
    """
    Handles collection of all conference and talk URLs.
    
    Implements Strategy pattern for different page types and
    follows Single Responsibility principle.
    """
    
    def __init__(self, config_path: str = "config.ini"):
        """Initialize the URL collector with configuration."""
        self.config = ConfigManager(config_path)
        self.db = DatabaseManager(self.config.get_db_path())
        self.logger = setup_logger(__name__, self.config.get_log_config())
        
        # Session configuration
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.get_user_agent()
        })
        
    def collect_all_urls(self, languages: List[str] = None) -> Dict[str, List[str]]:
        """
        Main entry point for URL collection.
        
        Args:
            languages: List of language codes ['eng', 'spa']. If None, collects both.
            
        Returns:
            Dictionary with language codes as keys and URL lists as values.
        """
        if languages is None:
            languages = ['eng', 'spa']
            
        self.logger.info(f"Starting URL collection for languages: {languages}")
        
        all_urls = {}
        for lang in languages:
            self.logger.info(f"Collecting URLs for language: {lang}")
            urls = self._collect_language_urls(lang)
            all_urls[lang] = urls
            self.logger.info(f"Collected {len(urls)} URLs for {lang}")
            
        return all_urls
    
    def _collect_language_urls(self, language: str) -> List[str]:
        """Collect all conference URLs for a specific language."""
        base_url = self.config.get_base_url(language)
        
        # Get URLs from main page
        main_page_urls = self._extract_main_page_urls(base_url)
        
        # Get URLs from decade archive pages
        decade_urls = self._extract_decade_urls(base_url)
        
        # Combine and deduplicate
        all_urls = list(set(main_page_urls + decade_urls))
        
        # Store in database for persistence
        self.db.store_conference_urls(language, all_urls)
        
        return all_urls
    
    def _extract_main_page_urls(self, base_url: str) -> List[str]:
        """Extract conference URLs from the main conference page."""
        try:
            response = self.session.get(base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract conference links using CSS selector from config
            selector = self.config.get_conference_link_selector()
            links = soup.select(selector)
            
            urls = []
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    urls.append(full_url)
                    
            self.logger.info(f"Extracted {len(urls)} URLs from main page")
            return urls
            
        except Exception as e:
            self.logger.error(f"Error extracting main page URLs: {e}")
            return []
    
    def _extract_decade_urls(self, base_url: str) -> List[str]:
        """Extract conference URLs from decade archive pages."""
        self.logger.info("Extracting decade archive URLs")
        
        decade_urls = []
        language = 'eng' if 'lang=eng' in base_url else 'spa'
        
        # Get base domain from config
        from urllib.parse import urlparse
        parsed_base = urlparse(base_url)
        base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
        
        available_decades = {
            'eng': [
                "20102019",
                "20002009",
                "19901999",
                "19801989"
            ],
            'spa': [
                "20102019",
                "20002009",
                "19901999"
            ]
        }
        decade_segments = available_decades.get(language, [])
        decade_pages = [
            f"{base_domain}/study/general-conference/{segment}?lang={language}"
            for segment in decade_segments
        ]
        
        # Extraer URLs de páginas de décadas
        for decade_url in decade_pages:
            try:
                self.logger.info(f"Processing decade page: {decade_url}")
                response = self.session.get(decade_url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                selector = self.config.get_conference_link_selector()
                links = soup.select(selector)
                
                decade_count = 0
                for link in links:
                    href = link.get('href')
                    if href and isinstance(href, str):
                        full_url = urljoin(decade_url, href)
                        decade_urls.append(full_url)
                        decade_count += 1
                
                self.logger.info(f"Extracted {decade_count} URLs from {decade_url}")
                
            except Exception as e:
                self.logger.error(f"Error processing decade page {decade_url}: {e}")
        
        # Agregar URLs individuales para años 1971-1979
        if language == 'eng':
            individual_urls = self._extract_individual_year_urls(language)
            decade_urls.extend(individual_urls)
        else:
            self.logger.info(f"Skipping individual year URLs for language: {language}")
        
        self.logger.info(f"Total decade archive URLs extracted: {len(decade_urls)}")
        return decade_urls
    
    def _extract_individual_year_urls(self, language: str) -> List[str]:
        """Extract URLs for individual years (1971-1979)."""
        self.logger.info("Extracting individual year URLs (1971-1979)")
        
        individual_urls = []
        
        # Get base domain from config for current language
        base_url = self.config.get_base_url(language)
        from urllib.parse import urlparse
        parsed_base = urlparse(base_url)
        base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
        
        for year in range(1971, 1980):  # 1971-1979
            for session in ['04', '10']:  # Abril y Octubre
                url = f"{base_domain}/study/general-conference/{year}/{session}?lang={language}"
                
                try:
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        individual_urls.append(url)
                        self.logger.debug(f"Added individual URL: {url}")
                    else:
                        self.logger.warning(f"URL not available: {url} (Status: {response.status_code})")
                
                except Exception as e:
                    self.logger.error(f"Error checking individual URL {url}: {e}")
        
        self.logger.info(f"Extracted {len(individual_urls)} individual year URLs")
        return individual_urls
    
    def get_stored_urls(self, language: str) -> List[str]:
        """Retrieve stored URLs from database."""
        return self.db.get_conference_urls(language)
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'session'):
            self.session.close()
        if hasattr(self, 'db'):
            self.db.close()
