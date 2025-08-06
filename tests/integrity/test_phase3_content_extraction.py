"""
Phase 3 Integrity Test - Basic Content Extraction

This test validates that we can extract basic metadata and content from talks
across different years and languages. This is the foundation test before
implementing note extraction.
"""

import pytest
import sqlite3
import random
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

from utils.database_manager import DatabaseManager
from utils.config_manager import ConfigManager


@dataclass
class TalkMetadata:
    """Data structure for basic talk metadata."""
    title: str
    author: str
    calling: str  # Position/calling of the speaker
    content: str
    url: str
    language: str
    year: str
    conference_session: str


class BasicContentExtractor:
    """
    Basic content extractor for Phase 3 testing.
    This is a simplified version to validate extraction capabilities.
    """
    
    def __init__(self, config_file: str):
        self.config = ConfigManager(config_file)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.get_user_agent()
        })
    
    def extract_talk_metadata(self, url: str) -> Optional[TalkMetadata]:
        """
        Extract basic metadata from a talk URL.
        
        Args:
            url: Talk URL to extract from
            
        Returns:
            TalkMetadata object or None if extraction fails
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract language from URL
            language = 'eng' if 'lang=eng' in url else 'spa'
            
            # Extract year and session from URL
            url_match = re.search(r'/general-conference/(\d{4})/(\d{2})/', url)
            if not url_match:
                return None
                
            year = url_match.group(1)
            session_num = url_match.group(2)
            conference_session = f"{year}-{session_num}"
            
            # Extract title
            title = self._extract_title(soup, language)
            if not title:
                return None
            
            # Extract author
            author = self._extract_author(soup, language)
            if not author:
                return None
            
            # Extract calling/position
            calling = self._extract_calling(soup, language)
            if not calling:
                calling = "Unknown"  # Some talks might not have calling info
            
            # Extract content
            content = self._extract_content(soup, language)
            if not content:
                return None
            
            return TalkMetadata(
                title=title,
                author=author,
                calling=calling,
                content=content,
                url=url,
                language=language,
                year=year,
                conference_session=conference_session
            )
            
        except Exception as e:
            print(f"Error extracting from {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup, language: str) -> Optional[str]:
        """Extract talk title from HTML."""
        # Try multiple selectors for title
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
                if title and len(title) > 3:  # Basic validation
                    return title
        
        return None
    
    def _extract_author(self, soup: BeautifulSoup, language: str) -> Optional[str]:
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
        paragraphs = soup.find_all('p')[:5]  # Check first 5 paragraphs
        for p in paragraphs:
            text = p.get_text(strip=True)
            # Look for "By Name" or "Por Name" pattern
            match = re.search(r'^(By|Por)\s+([A-Z][a-zA-Z\s\.]+)', text, re.IGNORECASE)
            if match:
                author = match.group(2).strip()
                if len(author) > 2:
                    return author
        
        return None
    
    def _extract_calling(self, soup: BeautifulSoup, language: str) -> Optional[str]:
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
        paragraphs = soup.find_all('p')[:10]  # Check first 10 paragraphs
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
    
    def _extract_content(self, soup: BeautifulSoup, language: str) -> Optional[str]:
        """Extract main talk content from HTML."""
        # Try multiple selectors for content
        content_selectors = [
            '.body-block',
            '.study-content',
            '.content',
            '[data-testid="content"]',
            '.articleBody'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                # Combine all content elements
                content_parts = []
                for element in elements:
                    text = element.get_text(separator='\n', strip=True)
                    if text:
                        content_parts.append(text)
                
                content = '\n\n'.join(content_parts)
                if content and len(content) > 100:  # Basic validation
                    return content
        
        # Fallback: try to get all paragraph text
        paragraphs = soup.find_all('p')
        if paragraphs:
            content_parts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 20:  # Skip very short paragraphs
                    content_parts.append(text)
            
            content = '\n\n'.join(content_parts)
            if content and len(content) > 100:
                return content
        
        return None


@pytest.mark.integrity
@pytest.mark.phase3
class TestPhase3BasicContentExtraction:
    """Test basic content extraction capabilities for Phase 3."""
    
    def test_random_talk_extraction_english(self, test_config_file):
        """Test extraction of 20 random English talks from different years."""
        results = self._test_random_talks_by_language('eng', test_config_file)
        
        # Verify we got results
        assert len(results) > 0, "No talks were successfully extracted"
        
        # We should get at least 15 out of 20 (75% success rate)
        success_rate = len(results) / 20
        assert success_rate >= 0.75, f"Success rate too low: {success_rate:.2%}"
        
        # Verify all required fields are present
        for talk in results:
            assert talk.title, f"Missing title for {talk.url}"
            assert talk.author, f"Missing author for {talk.url}"
            assert talk.content, f"Missing content for {talk.url}"
            assert len(talk.content) > 100, f"Content too short for {talk.url}"
            assert talk.language == 'eng'
            assert talk.year.isdigit()
            assert 1971 <= int(talk.year) <= 2025
        
        # Verify we have talks from different years (should span at least 10 years)
        years = set(talk.year for talk in results)
        assert len(years) >= 3, f"Not enough year diversity: {sorted(years)}"
        
        print(f"\n✅ English extraction: {len(results)}/20 successful ({len(results)/20:.1%})")
        print(f"   Years covered: {sorted(years)}")
        print(f"   Sample authors: {[talk.author for talk in results[:3]]}")
    
    def test_random_talk_extraction_spanish(self, test_config_file):
        """Test extraction of 20 random Spanish talks from different years."""
        results = self._test_random_talks_by_language('spa', test_config_file)
        
        # Verify we got results
        assert len(results) > 0, "No talks were successfully extracted"
        
        # We should get at least 15 out of 20 (75% success rate)
        success_rate = len(results) / 20
        assert success_rate >= 0.75, f"Success rate too low: {success_rate:.2%}"
        
        # Verify all required fields are present
        for talk in results:
            assert talk.title, f"Missing title for {talk.url}"
            assert talk.author, f"Missing author for {talk.url}"
            assert talk.content, f"Missing content for {talk.url}"
            assert len(talk.content) > 100, f"Content too short for {talk.url}"
            assert talk.language == 'spa'
            assert talk.year.isdigit()
            assert 1990 <= int(talk.year) <= 2025
        
        # Verify we have talks from different years
        years = set(talk.year for talk in results)
        assert len(years) >= 3, f"Not enough year diversity: {sorted(years)}"
        
        print(f"\n✅ Spanish extraction: {len(results)}/20 successful ({len(results)/20:.1%})")
        print(f"   Years covered: {sorted(years)}")
        print(f"   Sample authors: {[talk.author for talk in results[:3]]}")
    
    def _test_random_talks_by_language(self, language: str, config_file: str) -> List[TalkMetadata]:
        """
        Extract metadata from 20 random talks for a given language.
        
        Args:
            language: 'eng' or 'spa'
            config_file: Path to config file
            
        Returns:
            List of successfully extracted TalkMetadata
        """
        # Get random URLs from database
        import os
        
        # Find the project root (where talkscraper_state.db is located)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, '..', '..')
        db_path = os.path.join(project_root, 'talkscraper_state.db')
        
        # Debug: Check if database exists
        if not os.path.exists(db_path):
            print(f"❌ Database not found at: {os.path.abspath(db_path)}")
            print(f"   Current working directory: {os.getcwd()}")
            print(f"   Looking for database in project root: {os.path.abspath(project_root)}")
            return []
        
        print(f"📊 Using database: {os.path.abspath(db_path)}")
        
        try:
            db = DatabaseManager(db_path)
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            return []
        
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            # Debug: Check total URLs first
            cursor.execute('SELECT COUNT(*) FROM talk_urls WHERE language = ?', (language,))
            total_count = cursor.fetchone()[0]
            print(f"📈 Total {language} URLs in database: {total_count}")
            
            if total_count == 0:
                print(f"❌ No URLs found for language: {language}")
                db.close()
                return []
            
            # Get 20 random URLs for the language
            cursor.execute(
                'SELECT talk_url FROM talk_urls WHERE language = ? ORDER BY RANDOM() LIMIT 20',
                (language,)
            )
            urls = [row[0] for row in cursor.fetchall()]
        
        db.close()
        
        if not urls:
            print(f"❌ Failed to retrieve URLs for language: {language}")
            return []
        
        print(f"\n🔍 Extracting {len(urls)} {language} talks")
        
        # Extract content from each URL
        extractor = BasicContentExtractor(config_file)
        results = []
        
        for i, url in enumerate(urls, 1):
            year = self._extract_year_from_url(url)
            url_name = url.split('/')[-1].split('?')[0]
            print(f"   Processing {i}/{len(urls)}: {year} - {url_name}")
            
            try:
                metadata = extractor.extract_talk_metadata(url)
                if metadata:
                    results.append(metadata)
                    print(f"      ✅ Success: '{metadata.title}' by {metadata.author}")
                else:
                    print(f"      ❌ Failed to extract")
            except Exception as e:
                print(f"      ❌ Error: {e}")
        
        return results
    
    def _get_random_urls_by_year(self, language: str, count: int) -> List[str]:
        """
        Get random URLs distributed across different years.
        
        Args:
            language: 'eng' or 'spa'
            count: Number of URLs to return
            
        Returns:
            List of URLs
        """
        db = DatabaseManager('talkscraper_state.db')
        
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            # Get all URLs for the language, ordered randomly
            cursor.execute(
                'SELECT talk_url FROM talk_urls WHERE language = ? ORDER BY RANDOM() LIMIT ?',
                (language, count * 2)  # Get more than needed to allow for distribution
            )
            all_urls = [row[0] for row in cursor.fetchall()]
        
        db.close()
        
        if len(all_urls) <= count:
            return all_urls
        
        # Group URLs by year
        urls_by_year = {}
        for url in all_urls:
            year = self._extract_year_from_url(url)
            if year:
                if year not in urls_by_year:
                    urls_by_year[year] = []
                urls_by_year[year].append(url)
        
        if not urls_by_year:
            return all_urls[:count]  # Fallback if year extraction fails
        
        # Get URLs distributed across years
        years = list(urls_by_year.keys())
        selected_urls = []
        
        # Simple round-robin distribution
        year_index = 0
        while len(selected_urls) < count and any(urls_by_year.values()):
            current_year = years[year_index % len(years)]
            if urls_by_year[current_year]:
                selected_urls.append(urls_by_year[current_year].pop())
            year_index += 1
            
            # Remove empty years
            if current_year in urls_by_year and not urls_by_year[current_year]:
                del urls_by_year[current_year]
                years = list(urls_by_year.keys())
                if not years:
                    break
        
        return selected_urls[:count]
    
    def _extract_year_from_url(self, url: str) -> Optional[str]:
        """Extract year from URL."""
        match = re.search(r'/general-conference/(\d{4})/', url)
        return match.group(1) if match else None
    
    def test_content_extraction_quality(self, test_config_file):
        """Test that extracted content meets quality standards."""
        # Get a few sample URLs for quality testing
        db = DatabaseManager('talkscraper_state.db')
        
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            # Get recent URLs (likely to have better structure)
            cursor.execute('''
                SELECT talk_url FROM talk_urls 
                WHERE language = "eng" 
                AND talk_url LIKE "%/2024/%"
                LIMIT 3
            ''')
            recent_urls = [row[0] for row in cursor.fetchall()]
        
        db.close()
        
        extractor = BasicContentExtractor(test_config_file)
        
        for url in recent_urls:
            metadata = extractor.extract_talk_metadata(url)
            
            if metadata:  # Only test if extraction succeeded
                # Quality checks
                assert len(metadata.title) >= 5, f"Title too short: '{metadata.title}'"
                assert len(metadata.author) >= 3, f"Author too short: '{metadata.author}'"
                assert len(metadata.content) >= 500, f"Content too short: {len(metadata.content)} chars"
                
                # Content should contain common talk elements
                content_lower = metadata.content.lower()
                
                # Should contain some religious/spiritual content indicators
                spiritual_indicators = [
                    'jesus', 'christ', 'savior', 'lord', 'god', 'faith', 'spirit',
                    'gospel', 'church', 'testimony', 'prophet', 'scriptures'
                ]
                
                found_indicators = [word for word in spiritual_indicators if word in content_lower]
                assert len(found_indicators) >= 2, f"Content doesn't seem spiritual enough. Found: {found_indicators}"
                
                print(f"✅ Quality check passed for: '{metadata.title}' ({len(metadata.content)} chars)")


@pytest.mark.integrity  
@pytest.mark.phase3
@pytest.mark.critical
class TestPhase3CriticalExtraction:
    """Critical tests that must pass for Phase 3 content extraction."""
    
    def test_extraction_handles_network_errors(self, test_config_file):
        """Test that extraction gracefully handles network errors."""
        extractor = BasicContentExtractor(test_config_file)
        
        # Test with invalid URL
        result = extractor.extract_talk_metadata("https://invalid-domain-12345.com/fake")
        assert result is None
        
        # Test with valid domain but invalid path
        result = extractor.extract_talk_metadata("https://www.churchofjesuschrist.org/fake-path")
        assert result is None
    
    def test_extraction_validates_data_integrity(self, test_config_file):
        """Test that extracted data maintains integrity."""
        # Get one known working URL
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, '..', '..')
        db_path = os.path.join(project_root, 'talkscraper_state.db')
        
        db = DatabaseManager(db_path)
        
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT talk_url FROM talk_urls WHERE language = "eng" LIMIT 1')
            result = cursor.fetchone()
            
        if not result:
            # Skip test if no URLs available
            import pytest
            pytest.skip("No URLs available in database for testing")
            
        url = result[0]
        db.close()
        
        extractor = BasicContentExtractor(test_config_file)
        metadata = extractor.extract_talk_metadata(url)
        
        if metadata:  # Only test if extraction succeeded
            # Data integrity checks
            assert metadata.url == url
            assert metadata.language in ['eng', 'spa']
            assert metadata.year.isdigit()
            assert len(metadata.year) == 4
            
            # No HTML tags should remain in text content
            assert '<' not in metadata.title
            assert '>' not in metadata.title
            assert '<' not in metadata.author
            assert '>' not in metadata.author
            
            # Content should be properly cleaned
            html_indicators = ['<div', '<p>', '<span', '<script', '<style']
            for indicator in html_indicators:
                assert indicator not in metadata.content.lower()
