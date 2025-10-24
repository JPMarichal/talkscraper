#!/usr/bin/env python3
"""
TalkScraper - Talk Content Extractor Module

This module handles the complete extraction of talk content including:
- Title, author, position/calling, and content (static)
- Notes (dynamic, using Selenium)
- File organization and saving

Phase 3: Complete Content Extraction
"""

import logging
import time
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm

from utils.config_manager import ConfigManager
from utils.database_manager import DatabaseManager
from utils.logger_setup import setup_logger


@dataclass
class CompleteTalkData:
    """Complete talk data structure including notes."""
    title: str
    author: str
    calling: str  # Position/calling of the speaker
    content: str
    notes: List[str]  # List of extracted notes
    url: str
    language: str
    year: str
    conference_session: str
    extraction_timestamp: str
    note_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class TalkContentExtractor:
    """
    Complete talk content extractor for Phase 3.
    Combines static content extraction with dynamic note extraction.
    """
    
    def __init__(self, config_file: str):
        """
        Initialize the content extractor.
        
        Args:
            config_file: Path to configuration file
        """
        self.config = ConfigManager(config_file)
        self.db = DatabaseManager(self.config.get_db_path())
        
        # Setup logger
        log_config = self.config.get_log_config()
        self.logger = setup_logger('TalkContentExtractor', log_config)
        
        # Session for static content requests - optimized for speed
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.get_user_agent(),
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        # Connection pooling and timeout optimizations
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=50,
            pool_maxsize=50,
            max_retries=2
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Chrome options for Selenium (notes extraction) - Optimized for speed
        selenium_config = self.config.get_selenium_config()
        self.chrome_options = Options()
        if selenium_config['headless']:
            self.chrome_options.add_argument('--headless')
        
        # Performance optimizations - CPU focused
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument('--disable-web-security')
        self.chrome_options.add_argument('--disable-features=VizDisplayCompositor,TranslateUI,BlinkGenPropertyTrees')
        self.chrome_options.add_argument('--disable-background-timer-throttling')
        self.chrome_options.add_argument('--disable-renderer-backgrounding')
        self.chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        self.chrome_options.add_argument('--disable-background-networking')
        self.chrome_options.add_argument('--disable-image-loading')
        self.chrome_options.add_argument('--disable-plugins')
        self.chrome_options.add_argument('--disable-default-apps')
        
        # CPU optimization specific flags
        self.chrome_options.add_argument('--disable-javascript-harmony-shipping')
        self.chrome_options.add_argument('--disable-software-rasterizer')
        self.chrome_options.add_argument('--disable-background-media-downloads')
        self.chrome_options.add_argument('--disable-client-side-phishing-detection')
        self.chrome_options.add_argument('--disable-sync')
        self.chrome_options.add_argument('--disable-speech-api')
        
        self.chrome_options.add_argument('--window-size=600,400')  # Optimized window size
        self.chrome_options.add_argument('--memory-pressure-off')
        self.chrome_options.add_argument('--max_old_space_size=512')  # Limit V8 memory
        self.chrome_options.add_argument('--aggressive-cache-discard')
        
        # Disable logging to reduce I/O
        self.chrome_options.add_argument('--log-level=3')
        self.chrome_options.add_argument('--silent')
        
        # Experimental optimizations
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # Prefs for faster loading
        prefs = {
            "profile.default_content_setting_values": {
                "images": 2,  # Block images
                "plugins": 2,  # Block plugins
                "popups": 2,  # Block popups
                "geolocation": 2,  # Block location sharing
                "notifications": 2,  # Block notifications
                "media_stream": 2,  # Block media stream
            },
            "profile.managed_default_content_settings": {
                "images": 2
            }
        }
        self.chrome_options.add_experimental_option("prefs", prefs)
        
        # Output directory configuration
        self.output_dir = Path('conf')  # Use default conf directory
        self.ensure_output_structure()
    
    def ensure_output_structure(self):
        """Ensure the output directory structure exists."""
        for language in ['eng', 'spa']:
            lang_dir = self.output_dir / language
            lang_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_complete_talk(self, url: str) -> Optional[CompleteTalkData]:
        """
        Extract complete talk data including static content and notes.
        
        Args:
            url: Talk URL to extract from
            
        Returns:
            CompleteTalkData object or None if extraction fails
        """
        self.logger.info(f"Starting complete extraction for: {url}")
        
        try:
            # Step 1: Extract static content
            static_data = self._extract_static_content(url)
            if not static_data:
                self.logger.error(f"Failed to extract static content from: {url}")
                return None
            
            # Step 2: Extract notes using Selenium
            notes = self._extract_notes_selenium(url)
            if notes is None:
                self.logger.warning(f"Failed to extract notes from: {url}, proceeding with static content only")
                notes = []
            
            # Step 3: Combine data
            complete_data = CompleteTalkData(
                title=static_data['title'],
                author=static_data['author'],
                calling=static_data['calling'],
                content=static_data['content'],
                notes=notes,
                url=url,
                language=static_data['language'],
                year=static_data['year'],
                conference_session=static_data['conference_session'],
                extraction_timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                note_count=len(notes)
            )
            
            self.logger.info(f"Successfully extracted complete talk: '{complete_data.title}' by {complete_data.author} ({complete_data.note_count} notes)")
            self._backup_talk_metadata(complete_data)
            return complete_data
            
        except Exception as e:
            self.logger.error(f"Error in complete extraction for {url}: {e}")
            return None
    
    def _extract_static_content(self, url: str) -> Optional[Dict[str, str]]:
        """
        Extract static content using requests + BeautifulSoup.
        
        Args:
            url: Talk URL to extract from
            
        Returns:
            Dictionary with static content or None if extraction fails
        """
        try:
            response = self.session.get(url, timeout=15)  # Reduced timeout for speed
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract language from URL
            language = 'eng' if 'lang=eng' in url else 'spa'
            
            # Extract year and session from URL
            url_match = re.search(r'/general-conference/(\d{4})/(\d{2})/', url)
            if not url_match:
                self.logger.error(f"Could not parse year/session from URL: {url}")
                return None
                
            year = url_match.group(1)
            session_num = url_match.group(2)
            conference_session = f"{year}-{session_num}"
            
            # Extract title
            title = self._extract_title(soup)
            if not title:
                self.logger.error(f"Could not extract title from: {url}")
                return None
            
            # Extract author
            author = self._extract_author(soup)
            if not author:
                self.logger.error(f"Could not extract author from: {url}")
                return None
            
            # Extract calling/position
            calling = self._extract_calling(soup)
            if not calling:
                calling = "Posición no identificada"
            
            # Extract content
            content = self._extract_content(soup)
            if not content:
                self.logger.error(f"Could not extract content from: {url}")
                return None
            
            return {
                'title': title,
                'author': author,
                'calling': calling,
                'content': content,
                'language': language,
                'year': year,
                'conference_session': conference_session
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting static content from {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract talk title from HTML."""
        title_selectors = [
            'h1.title',
            'h1',
            '.title-block h1',
            '.title',
            '[data-testid="title"]',
            '.study-title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 3:
                    return title
        
        return None
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author name from HTML."""
        # Try multiple selectors for author
        author_selectors = [
            '.byline .author',
            '.author-name',
            '.byline',
            '.author',
            '[data-testid="author"]',
            '.study-author',
            'p.author'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                author = element.get_text(strip=True)
                # Clean up author text (remove "By " prefix if present)
                author = re.sub(r'^(By\s+|Por\s+)', '', author, flags=re.IGNORECASE)
                if author and len(author) > 2:
                    return author
        
        # Fallback: Look for "By [Name]" pattern in the first few paragraphs
        paragraphs = soup.find_all('p')[:5]
        for p in paragraphs:
            text = p.get_text(strip=True)
            # Look for "By Name" or "Por Name" pattern
            match = re.search(r'^(By|Por)\s+([A-Z][a-zA-Z\s\.]+)', text, re.IGNORECASE)
            if match:
                author = match.group(2).strip()
                if len(author) > 2:
                    return author
        
        return None
    
    def _extract_calling(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract speaker's calling/position from HTML."""
        # Try multiple selectors for calling
        calling_selectors = [
            '.byline .calling',
            '.author-calling',
            '.calling',
            '.position',
            '[data-testid="calling"]',
            '.study-calling'
        ]
        
        for selector in calling_selectors:
            element = soup.select_one(selector)
            if element:
                calling = element.get_text(strip=True)
                if calling and len(calling) > 3:
                    return calling
        
        # Sometimes calling is in the same element as author, separated by comma or line break
        byline_element = soup.select_one('.byline')
        if byline_element:
            byline_text = byline_element.get_text(separator='\n', strip=True)
            lines = [line.strip() for line in byline_text.split('\n') if line.strip()]
            if len(lines) >= 2:
                # Second line often contains the calling
                calling = lines[1]
                if calling and len(calling) > 3:
                    return calling
        
        # Alternative: Look for calling information in paragraphs near the author
        paragraphs = soup.find_all('p')[:10]
        for p in paragraphs:
            text = p.get_text(strip=True)
            # Common patterns for callings
            calling_patterns = [
                r'(President|Elder|Bishop|Member|Sister|Brother|Apostle)\s+of\s+',
                r'(First|Second)\s+Counselor',
                r'Presiding\s+Bishop',
                r'General\s+(Authority|Officer)',
                r'Quorum\s+of\s+the\s+Twelve',
                r'First\s+Presidency'
            ]
            
            for pattern in calling_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    # Extract the calling (first sentence or line)
                    calling = text.split('.')[0].strip()
                    if len(calling) > 5 and len(calling) < 100:
                        return calling
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract main talk content from HTML, preserving formatting."""
        # Try multiple selectors for content
        content_selectors = [
            '.body-block',
            '.study-content',
            '.content',
            '[data-testid="content"]',
            '.articleBody'
        ]
        
        content_element = None
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                content_element = element
                break
        
        if not content_element:
            # Fallback: try to get all paragraphs
            content_element = soup
        
        # Extract paragraphs while preserving HTML structure
        paragraphs = content_element.find_all('p')
        if not paragraphs:
            return None
        
        formatted_paragraphs = []
        for p in paragraphs:
            # Skip paragraphs that might be metadata, bylines, etc.
            p_text = p.get_text(strip=True)
            if len(p_text) < 20:
                continue
            
            # Format the paragraph while preserving important HTML elements
            formatted_p = self._format_paragraph_html(p)
            if formatted_p:
                formatted_paragraphs.append(formatted_p)
        
        if formatted_paragraphs:
            return '\n'.join(formatted_paragraphs)
        
        return None
    
    def _format_paragraph_html(self, paragraph) -> str:
        """Format a single paragraph while preserving important HTML elements."""
        try:
            # Create a copy to avoid modifying the original
            p_copy = BeautifulSoup(str(paragraph), 'html.parser')
            p_elem = p_copy.find('p')
            
            if not p_elem:
                return ""
            
            # Remove all links except note references (preserve text content)
            for link in p_elem.find_all('a'):
                href = link.get('href', '')
                class_attr = link.get('class', [])
                
                # Keep note reference links
                if 'note-ref' in class_attr or '#note' in href:
                    # Convert to our internal note link format
                    note_match = re.search(r'#note(\d+)', href)
                    if note_match:
                        note_id = note_match.group(1)
                        link['href'] = f"#note{note_id}"
                        link['class'] = 'note-link'
                    continue
                
                # For all other links, replace with just the text content
                link.replace_with(link.get_text())
            
            # Get HTML content without escaping
            content = str(p_elem).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            
            # Remove unnecessary attributes using regex
            content = re.sub(r' data-aid="[^"]*"', '', content)
            content = re.sub(r' id="[^"]*"', '', content)
            content = re.sub(r' data-scroll-id="[^"]*"', '', content)
            
            # Ensure note superscripts are visible by adding text content
            # Fix <sup class="marker" data-value="X"></sup> to <sup>X</sup>
            content = re.sub(r'<sup class="marker" data-value="(\d+)"></sup>', r'<sup>\1</sup>', content)
            
            # Clean up whitespace but preserve structure
            content = re.sub(r'\s+', ' ', content)
            content = content.strip()
            
            return content
            
        except Exception as e:
            # Fallback: return plain text if HTML processing fails
            return f"<p>{paragraph.get_text(strip=True)}</p>"
    
    def _extract_notes_selenium(self, url: str) -> Optional[List[str]]:
        """
        Extract notes using Selenium for JavaScript-rendered content.
        
        Args:
            url: Talk URL to extract notes from
            
        Returns:
            List of notes or None if extraction fails
        """
        driver = None
        notes = []
        
        try:
            self.logger.debug(f"Starting Selenium note extraction for: {url}")
            driver = webdriver.Chrome(options=self.chrome_options)
            
            # Load the page
            driver.get(url)
            
            # Wait for page to load - reduced timeout for speed
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Try to activate "Related Content" button
            self._activate_related_content(driver)
            
            # Reduced wait time for faster processing
            time.sleep(1.5)
            
            # Extract notes from li elements with id starting with "note"
            note_elements = driver.find_elements(By.CSS_SELECTOR, 'li[id^="note"]')
            self.logger.debug(f"Found {len(note_elements)} note elements")
            
            for element in note_elements:
                note_id = element.get_attribute('id')
                try:
                    # Get the innerHTML for complete content
                    inner_html = driver.execute_script("return arguments[0].innerHTML;", element)
                    
                    if inner_html and inner_html.strip():
                        # Clean the HTML to get text only with proper spacing
                        soup = BeautifulSoup(inner_html, 'html.parser')
                        # Use separator to ensure spaces between elements
                        clean_text = soup.get_text(separator=' ', strip=True)
                        
                        # Clean up multiple consecutive spaces but preserve single spaces
                        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                        
                        if clean_text and len(clean_text) > 5:
                            notes.append(f"[{note_id}] {clean_text}")
                            self.logger.debug(f"Extracted note {note_id}: {clean_text[:50]}...")
                        
                except Exception as e:
                    self.logger.warning(f"Error extracting note {note_id}: {e}")
            
            self.logger.info(f"Successfully extracted {len(notes)} notes from: {url}")
            return notes
            
        except Exception as e:
            self.logger.error(f"Error in Selenium note extraction for {url}: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def _activate_related_content(self, driver):
        """Try to activate the Related Content button."""
        try:
            related_content_selectors = [
                'button[data-testid="related-content"]',
                'button[aria-label*="Related"]',
                'button[title*="Related"]'
            ]
            
            for selector in related_content_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        element = elements[0]
                        if element.is_displayed() and element.is_enabled():
                            driver.execute_script("arguments[0].click();", element)
                            self.logger.debug("Activated Related Content button")
                            # Wait for content to load
                            time.sleep(2)
                            return True
                except Exception:
                    continue
            
            self.logger.debug("Could not activate Related Content button")
            return False
            
        except Exception as e:
            self.logger.warning(f"Error activating Related Content: {e}")
            return False
    
    def save_talk_to_file(self, talk_data: CompleteTalkData) -> Optional[str]:
        """
        Save talk data to HTML file following the project's naming convention.
        
        Args:
            talk_data: Complete talk data to save
            
        Returns:
            Path to saved file or None if save fails
        """
        try:
            # Create directory structure: lang/YYYYMM/
            year_month = f"{talk_data.year}{talk_data.conference_session.split('-')[1]}"
            output_dir = self.output_dir / talk_data.language / year_month
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Clean filename (remove problematic characters)
            safe_title = re.sub(r'[<>:"/\\|?*]', '', talk_data.title)
            safe_author = re.sub(r'[<>:"/\\|?*.]', '', talk_data.author)
            safe_author = safe_author.replace('.', '')  # Remove periods
            
            # Construct filename: "Title (Author).html"
            filename = f"{safe_title} ({safe_author}).html"
            file_path = output_dir / filename
            
            # Generate HTML content
            html_content = self._generate_html_content(talk_data)
            
            # Save file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Saved talk to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Error saving talk {talk_data.title}: {e}")
            return None
    
    def _generate_html_content(self, talk_data: CompleteTalkData) -> str:
        """
        Generate HTML content for the talk file.
        
        Args:
            talk_data: Complete talk data
            
        Returns:
            HTML content as string
        """
        notes_html = ""
        if talk_data.notes:
            # Generate notes with proper anchors for internal linking
            notes_items = []
            for i, note in enumerate(talk_data.notes, 1):
                # Remove [noteX] prefix if present and add proper anchor
                clean_note = re.sub(r'^\[note\d+\]\s*', '', note)
                notes_items.append(f'        <li id="note{i}"><a name="note{i}"></a>{clean_note}</li>')
            notes_list = "\n".join(notes_items)
            notes_html = f"""
    <div class="notes">
        <h2>Notas</h2>
        <ol>
{notes_list}
        </ol>
    </div>"""
        
        return f"""<!DOCTYPE html>
<html lang="{talk_data.language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{talk_data.title} - {talk_data.author}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #ccc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .author {{
            font-size: 1.2em;
            color: #34495e;
            margin-bottom: 5px;
        }}
        .calling {{
            font-style: italic;
            color: #7f8c8d;
            margin-bottom: 10px;
        }}
        .metadata {{
            font-size: 0.9em;
            color: #95a5a6;
        }}
        .content {{
            text-align: justify;
            margin: 30px 0;
        }}
        .content p {{
            margin-bottom: 15px;
        }}
        .notes {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ccc;
        }}
        .notes h2 {{
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        .notes ol {{
            padding-left: 20px;
        }}
        .notes li {{
            margin-bottom: 8px;
            font-size: 0.9em;
        }}
        .note-link {{
            color: #3498db;
            text-decoration: none;
            font-weight: bold;
        }}
        .note-link:hover {{
            text-decoration: underline;
        }}
        .extraction-info {{
            margin-top: 40px;
            padding: 15px;
            background-color: #ecf0f1;
            border-radius: 5px;
            font-size: 0.8em;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{talk_data.title}</h1>
        <div class="author">{talk_data.author}</div>
        <div class="calling">{talk_data.calling}</div>
        <div class="metadata">
            {talk_data.conference_session} | {talk_data.language.upper()} | {talk_data.note_count} notas
        </div>
    </div>
    
    <div class="content">
        {talk_data.content}
    </div>
{notes_html}
    
    <div class="extraction-info">
        <strong>Información de extracción:</strong><br>
        URL original: <a href="{talk_data.url}" target="_blank">{talk_data.url}</a><br>
        Extraído: {talk_data.extraction_timestamp}<br>
        Notas extraídas: {talk_data.note_count}
    </div>
</body>
</html>"""
    
    def _format_content_paragraphs(self, content: str) -> str:
        """Format content text into HTML paragraphs."""
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if para:
                # Escape HTML characters
                para = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                formatted_paragraphs.append(f"        <p>{para}</p>")
        
        return '\n'.join(formatted_paragraphs)
    
    def extract_talks_batch(self, talk_urls: List[str], batch_size: int = 24) -> Dict[str, int]:
        """
        Extract multiple talks in parallel batches using ThreadPoolExecutor.
        Optimized for maximum performance.
        
        Args:
            talk_urls: List of talk URLs to extract
            batch_size: Number of talks to process concurrently (default: 24 for 64GB RAM)
            
        Returns:
            Dictionary with extraction statistics
        """
        self.logger.info(f"Starting OPTIMIZED concurrent extraction of {len(talk_urls)} talks with {batch_size} threads")
        
        stats = {
            'total': len(talk_urls),
            'successful': 0,
            'failed': 0,
            'saved': 0,
            'marked_processed': 0
        }
        
        # Thread-safe counters
        stats_lock = Lock()
        
        def extract_single_talk_optimized(url: str) -> Optional[Tuple[str, bool, bool]]:
            """Extract a single talk and return results - optimized version."""
            try:
                # Extract complete talk data
                talk_data = self.extract_complete_talk(url)
                
                if talk_data:
                    # Save to file immediately in the same thread
                    saved_path = self.save_talk_to_file(talk_data)
                    saved = bool(saved_path)
                    
                    # Mark as processed in database if successfully saved
                    if saved:
                        try:
                            self.mark_talk_processed(url, success=True)
                            # Note: stats['marked_processed'] will be updated in the main loop
                        except Exception as db_e:
                            self.logger.warning(f"Error marking {url} as processed: {db_e}")
                    
                    return (url, True, saved)
                else:
                    # Mark as processed even if extraction failed to avoid retry loops
                    try:
                        self.mark_talk_processed(url, success=False)
                        # Note: stats['marked_processed'] will be updated in the main loop
                    except Exception as db_e:
                        self.logger.warning(f"Error marking failed {url} as processed: {db_e}")
                    return (url, False, False)
                    
            except Exception as e:
                self.logger.warning(f"Error processing {url}: {e}")  # Changed to warning for speed
                # Mark as processed even on exception to avoid retry loops
                try:
                    self.mark_talk_processed(url, success=False)
                    # Note: stats['marked_processed'] will be updated in the main loop
                except Exception as db_e:
                    self.logger.warning(f"Error marking exception {url} as processed: {db_e}")
                return (url, False, False)
        
        # Process talks in parallel with optimized thread pool
        with ThreadPoolExecutor(max_workers=batch_size, thread_name_prefix="OptimizedTalkExtractor") as executor:
            # Submit all jobs at once for better scheduling
            future_to_url = {executor.submit(extract_single_talk_optimized, url): url for url in talk_urls}
            
            # Process completed futures with faster progress updates
            with tqdm(total=len(talk_urls), desc="Extracting talks", unit="talk", mininterval=0.1) as pbar:
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        result = future.result(timeout=30)  # Add timeout to prevent hanging
                        if result:
                            _, success, saved = result
                            
                            # Update stats thread-safely with minimal locking
                            with stats_lock:
                                if success:
                                    stats['successful'] += 1
                                    if saved:
                                        stats['saved'] += 1
                                else:
                                    stats['failed'] += 1
                                # Always increment marked_processed since we mark all URLs as processed
                                stats['marked_processed'] += 1
                            
                            # Less frequent progress bar updates for performance
                            if stats['successful'] % 5 == 0 or not success:
                                pbar.set_postfix({
                                    'success': f"{stats['successful']}/{stats['total']}",
                                    'failed': stats['failed'],
                                    'saved': stats['saved'],
                                    'marked': stats['marked_processed']
                                })
                        else:
                            with stats_lock:
                                stats['failed'] += 1
                                stats['marked_processed'] += 1
                                
                    except Exception as e:
                        self.logger.warning(f"Future timeout/exception for {url}: {e}")  # Warning instead of error
                        with stats_lock:
                            stats['failed'] += 1
                            stats['marked_processed'] += 1
                    
                    pbar.update(1)
        
        self.logger.info(f"OPTIMIZED concurrent extraction completed: {stats['successful']}/{stats['total']} successful, {stats['saved']} saved to files, {stats['marked_processed']} marked as processed")
        return stats
    
    def get_unprocessed_talk_urls(self, language: str, limit: Optional[int] = None) -> List[str]:
        """
        Get list of unprocessed talk URLs from the database.
        
        Args:
            language: Language to filter ('eng' or 'spa')
            limit: Maximum number of URLs to return
            
        Returns:
            List of unprocessed talk URLs
        """
        try:
            urls = self.db.get_unprocessed_talk_urls(language, limit)
            self.logger.info(f"Retrieved {len(urls)} unprocessed {language} talk URLs")
            return urls
        except Exception as e:
            self.logger.error(f"Error retrieving unprocessed URLs for {language}: {e}")
            return []
    
    def get_all_unprocessed_talk_urls(self, languages: Optional[List[str]] = None, limit: Optional[int] = None) -> List[str]:
        """
        Get list of unprocessed talk URLs from all languages.

        Args:
            languages: Iterable of language codes to include (default: both)
            limit: Maximum number of URLs to return

        Returns:
            List of unprocessed talk URLs from all languages
        """
        try:
            all_urls = []
            if languages is None:
                languages = ['eng', 'spa']

            for language in languages:
                try:
                    urls = self.db.get_unprocessed_talk_urls(language)
                    all_urls.extend(urls)
                    self.logger.info(f"Retrieved {len(urls)} unprocessed {language} talk URLs")
                except Exception as e:
                    self.logger.warning(f"Error retrieving unprocessed URLs for {language}: {e}")
            
            # Apply limit if specified
            if limit and len(all_urls) > limit:
                all_urls = all_urls[:limit]
            
            self.logger.info(f"Total unprocessed URLs retrieved: {len(all_urls)}")
            return all_urls
        except Exception as e:
            self.logger.error(f"Error retrieving unprocessed URLs: {e}")
            return []
    
    def mark_talk_processed(self, url: str, success: bool = True):
        """Mark a talk URL as processed in the database."""
        try:
            self.db.mark_talk_processed(url, success)
        except Exception as e:
            self.logger.error(f"Error marking {url} as processed: {e}")
    
    def _normalize_author(self, author: str) -> str:
        """Remove common prefixes from author name."""
        return re.sub(r'^(Elder|Hermana|Presidente|President|Sister|Brother)\s+', '', author, flags=re.IGNORECASE).strip()

    def _backup_talk_metadata(self, talk_data: CompleteTalkData):
        """Save metadata (title, author, calling, note_count) to the database."""
        try:
            clean_author = self._normalize_author(talk_data.author)
            # Update metadata in talk_urls table using the update method
            self.db.update_talk_metadata(
                talk_url=talk_data.url,
                title=talk_data.title,
                author=clean_author,
                calling=talk_data.calling,
                conference=talk_data.conference_session
            )
            self.logger.info(f"Metadata backed up for: {talk_data.title}")
        except Exception as e:
            self.logger.error(f"Error backing up metadata for {talk_data.url}: {e}")

    def backup_existing_html_metadata(self):
        """Scan saved HTML files and backup metadata to the database."""
        for language in ['eng', 'spa']:
            lang_dir = self.output_dir / language
            for html_file in lang_dir.rglob('*.html'):
                try:
                    with open(html_file, 'r', encoding='utf-8') as f:
                        soup = BeautifulSoup(f, 'html.parser')
                        title = soup.find('h1').get_text(strip=True)
                        author = soup.find(class_='author').get_text(strip=True)
                        calling = soup.find(class_='calling').get_text(strip=True)
                        note_count = len(soup.select('.notes li'))
                        url_tag = soup.find('a', href=True)
                        url = url_tag['href'] if url_tag else ''
                        year = html_file.parent.name[:4]
                        conference_session = html_file.parent.name
                        talk_data = CompleteTalkData(
                            title=title,
                            author=author,
                            calling=calling,
                            content='',
                            notes=[],
                            url=url,
                            language=language,
                            year=year,
                            conference_session=conference_session,
                            extraction_timestamp='',
                            note_count=note_count
                        )
                        self._backup_talk_metadata(talk_data)
                except Exception as e:
                    self.logger.warning(f"Error processing {html_file}: {e}")
        if hasattr(self, 'db'):
            self.db.close()
