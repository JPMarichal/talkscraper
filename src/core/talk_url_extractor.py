"""
TalkScraper - Talk URL Extraction Module

This module handles the extraction of individual talk URLs from conference pages.

Phase 2: Talk URL Extraction
- Access each conference page from Phase 1 results
- Extract URLs for all individual talks
- Filter text-based talks (exclude video-only content)
- Store talk URLs with conference associations
"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from utils.config_manager import ConfigManager
from utils.database_manager import DatabaseManager
from utils.logger_setup import setup_logger


class TalkURLExtractor:
    """
    Handles extraction of individual talk URLs from conference pages.
    
    Processes all conference URLs collected in Phase 1 to extract
    the URLs of individual talks within each conference.
    """
    
    def __init__(self, config_path: str = "config.ini"):
        """Initialize the talk URL extractor with configuration."""
        self.config = ConfigManager(config_path)
        self.db = DatabaseManager(self.config.get_db_path())
        self.logger = setup_logger(__name__, self.config.get_log_config())
        
        # Session configuration
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.get_user_agent()
        })
        
        # Request settings
        self.request_delay = float(self.config.config.get('DEFAULT', 'request_delay', fallback='1.0'))
        self.retry_attempts = int(self.config.config.get('DEFAULT', 'retry_attempts', fallback='3'))
        self.retry_delay = float(self.config.config.get('DEFAULT', 'retry_delay', fallback='2.0'))
        
    def extract_all_talk_urls(self, languages: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Main entry point for talk URL extraction.
        
        Args:
            languages: List of language codes to process. If None, processes all.
            
        Returns:
            Dictionary with extraction statistics by language
        """
        if languages is None:
            languages = ['eng', 'spa']
            
        self.logger.info(f"Starting talk URL extraction for languages: {languages}")
        
        stats = {}
        for language in languages:
            self.logger.info(f"Processing language: {language}")
            count = self._extract_language_talk_urls(language)
            stats[language] = count
            self.logger.info(f"Extracted {count} talk URLs for {language}")
            
        return stats
    
    def _extract_language_talk_urls(self, language: str) -> int:
        """Extract talk URLs for a specific language."""
        # Get unprocessed conference URLs for this language
        conference_urls = self._get_unprocessed_conferences(language)
        
        if not conference_urls:
            self.logger.info(f"No unprocessed conferences found for {language}")
            return 0
        
        self.logger.info(f"Processing {len(conference_urls)} conferences for {language}")
        
        total_talks_extracted = 0
        
        # Process conferences with progress bar
        with tqdm(conference_urls, desc=f"Extracting {language.upper()} talks", unit="conf") as pbar:
            for conference_url in pbar:
                try:
                    talk_urls = self._extract_conference_talk_urls(conference_url)
                    
                    if talk_urls:
                        # Store talk URLs in database
                        stored_count = self.db.store_talk_urls(conference_url, language, talk_urls)
                        total_talks_extracted += stored_count
                        
                        if stored_count > 0:
                            # Only mark as processed if we stored at least one new talk
                            self._mark_conference_processed(conference_url)
                        else:
                            self.logger.info(f"No new talk URLs stored for {conference_url}; leaving as pending")
                        
                        pbar.set_postfix({
                            'talks': len(talk_urls),
                            'total': total_talks_extracted
                        })
                        
                        self.logger.debug(f"Extracted {len(talk_urls)} talks from {conference_url}")
                    else:
                        self.logger.warning(f"No talks found in {conference_url}")
                        
                    # Respect rate limiting
                    time.sleep(self.request_delay)
                    
                except Exception as e:
                    self.logger.error(f"Error processing conference {conference_url}: {e}")
                    continue
        
        return total_talks_extracted
    
    def _get_unprocessed_conferences(self, language: str) -> List[str]:
        """Get list of unprocessed conference URLs for a language."""
        try:
            urls = self.db.get_unprocessed_conference_urls(language)
            # Filter to only valid conference URLs
            valid_urls = [url for url in urls if self._is_valid_conference_url(url)]
            
            if len(valid_urls) != len(urls):
                self.logger.info(f"Filtered {len(urls) - len(valid_urls)} invalid URLs, {len(valid_urls)} valid conferences remain")
            
            return valid_urls
        except Exception as e:
            self.logger.error(f"Error getting unprocessed conferences: {e}")
            return []
    
    def _is_valid_conference_url(self, url: str) -> bool:
        """
        Validate if a URL is a valid conference URL (not talk URL).
        
        Valid conference URLs:
        - https://conference.churchofjesuschrist.org/study/general-conference/2025/04?lang=eng
        - https://conference.lds.org/study/general-conference/1975/10?lang=spa
        
        Invalid URLs:
        - URLs de décadas: /2010-2019, /1990-1999, etc.
        - URLs de oradores: /speakers/
        - URLs de manuales: /manual/
        - URLs de discursos individuales: /2025/04/13holland
        """
        try:
            parsed = urlparse(url)
            
            # Verificar dominios válidos
            valid_domains = [
                'www.churchofjesuschrist.org',
                'churchofjesuschrist.org', 
                'conference.churchofjesuschrist.org',
                'conference.lds.org'  # Dominio anterior, aún válido por redirección
            ]
            if parsed.netloc not in valid_domains:
                return False
            
            # Verificar que sea una URL de conferencia general
            if '/study/general-conference/' not in parsed.path:
                return False
            
            # Verificar que NO sea una URL de páginas especiales
            if any(x in parsed.path for x in ['/speakers/', '/manual/', '/topics/']):
                return False
            
            # Extraer la parte después de /study/general-conference/
            path_parts = parsed.path.strip('/').split('/')
            
            if len(path_parts) < 4:  # Debe tener al menos: study, general-conference, año, mes
                return False
            
            if path_parts[0] != 'study' or path_parts[1] != 'general-conference':
                return False
            
            year_month = path_parts[2:4]  # [año, mes]
            
            # Verificar formato de año (4 dígitos)
            if not year_month[0].isdigit() or len(year_month[0]) != 4:
                return False
            
            # Verificar formato de mes (04 o 10)
            if year_month[1] not in ['04', '10']:
                return False
            
            # Verificar que el año esté en un rango razonable (1971-2030)
            year = int(year_month[0])
            if year < 1971 or year > 2030:
                return False
            
            # Verificar que NO sea una URL de discurso individual
            # URLs de conferencia terminan en año/mes, no en año/mes/talkid
            if len(path_parts) > 4:
                # Si hay más partes después del mes, es probable que sea un discurso individual
                return False
            
            return True
            
        except Exception:
            return False
    
    def _extract_conference_talk_urls(self, conference_url: str) -> List[str]:
        """
        Extract all talk URLs from a single conference page.
        
        Args:
            conference_url: URL of the conference page
            
        Returns:
            List of talk URLs found on the page
        """
        talk_urls = []
        
        for attempt in range(self.retry_attempts):
            try:
                response = self.session.get(conference_url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Use configured CSS selector for talk links
                selector = self.config.get_talk_link_selector()
                talk_links = soup.select(selector)
                
                for link in talk_links:
                    href = link.get('href')
                    if href and isinstance(href, str):
                        # Convert relative URLs to absolute
                        full_url = urljoin(conference_url, href)
                        
                        # Basic filtering - ensure it's a talk URL
                        if self._is_valid_talk_url(full_url):
                            talk_urls.append(full_url)
                
                self.logger.debug(f"Found {len(talk_urls)} talk URLs in {conference_url}")
                break
                
            except requests.RequestException as e:
                self.logger.warning(f"Request failed for {conference_url} (attempt {attempt + 1}): {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"Failed to extract talks from {conference_url} after {self.retry_attempts} attempts")
                    
            except Exception as e:
                self.logger.error(f"Unexpected error extracting talks from {conference_url}: {e}")
                break
        
        return talk_urls
    
    def _is_valid_talk_url(self, url: str) -> bool:
        """
        Validate if a URL is a valid talk URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL appears to be a valid talk URL
        """
        try:
            parsed = urlparse(url)
            
            # Check if it's a conference talk URL pattern
            if '/study/general-conference/' in parsed.path:
                path_parts = parsed.path.strip('/').split('/')
                
                # Should have specific structure: study/general-conference/year/month/talk-title
                if len(path_parts) >= 5:
                    # Exclude session URLs (they contain 'session' in the URL)
                    if 'session' not in parsed.path.lower():
                        # Exclude URLs that are just conference indices (should have more than just year/month)
                        if len(path_parts) > 4:  # More than just study/general-conference/year/month
                            # Exclude decade pages and other index pages
                            last_part = path_parts[-1]
                            if not any(decade in last_part for decade in ['2010-2019', '2000-2009', '1990-1999', '1980-1989', '1970-1979']):
                                # Exclude speaker index pages
                                if 'speakers' not in parsed.path.lower():
                                    return True
            
            return False
            
        except Exception:
            return False
    
    def _mark_conference_processed(self, conference_url: str):
        """Mark a conference URL as processed in the database."""
        try:
            self.db.mark_conference_processed(conference_url)
        except Exception as e:
            self.logger.error(f"Error marking conference as processed {conference_url}: {e}")
    
    def get_extraction_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics about talk URL extraction progress."""
        try:
            stats = self.db.get_talk_extraction_stats()
            return stats
        except Exception as e:
            self.logger.error(f"Error getting extraction stats: {e}")
            return {}
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'session'):
            self.session.close()
