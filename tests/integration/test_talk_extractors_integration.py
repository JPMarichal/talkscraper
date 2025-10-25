"""
Integration tests for talk content extraction and metadata integrity.

Tests the complete flow of talk extraction, validation, and metadata storage
as required by Milestone 6.
"""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup

from core.talk_content_extractor import TalkContentExtractor, CompleteTalkData
from utils.database_manager import DatabaseManager


class TestTalkExtractionIntegration:
    """Integration tests for talk content extraction flow."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tf:
            db_path = tf.name
        yield db_path
        Path(db_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def mock_config(self, temp_db, temp_output_dir):
        """Create a mock config with temporary paths."""
        config = Mock()
        config.get_db_path.return_value = temp_db
        config.config = MagicMock()
        config.config.getboolean.return_value = True  # skip_notes
        config.get_content_retry_config.return_value = (1, 0)
        config.get_log_config.return_value = {
            'level': 'INFO',
            'file': None,
            'console': False
        }
        config.get_user_agent.return_value = 'Test Agent'
        config.get_selenium_config.return_value = {'headless': True}
        return config
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_metadata_backup_flow(self, temp_db):
        """Test that metadata is properly backed up to talk_metadata table."""
        db = DatabaseManager(temp_db)
        
        # Insert a talk URL first
        test_url = "https://example.com/test/1985/10/test-talk"
        db.store_talk_urls("https://example.com/conf", "eng", [test_url])
        
        # Store metadata
        db.store_talk_metadata(
            url=test_url,
            title="Test Title",
            author="Test Author",
            calling="Test Calling",
            note_count=5,
            language="eng",
            year="1985",
            conference_session="1985-10"
        )
        
        # Verify metadata was stored
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM talk_metadata WHERE url = ?", (test_url,))
            result = cursor.fetchone()
            
            assert result is not None
            assert result[2] == "Test Title"  # title
            assert result[3] == "Test Author"  # author
            assert result[4] == "Test Calling"  # calling
            assert result[5] == 5  # note_count
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_talk_validation_prevents_incomplete_processing(self, temp_db):
        """Test that incomplete talks are not marked as processed."""
        db = DatabaseManager(temp_db)
        
        # Create test data with missing content
        incomplete_data = CompleteTalkData(
            title="Test Title",
            author="Test Author",
            calling="Test Calling",
            content="Short",  # Too short to be valid
            notes=[],
            url="https://example.com/test",
            language="eng",
            year="1985",
            conference_session="1985-10",
            extraction_timestamp="2024-01-01 00:00:00",
            note_count=0
        )
        
        # Store talk URL
        db.store_talk_urls("https://example.com/conf", "eng", [incomplete_data.url])
        
        # Create extractor with mocked config
        with patch('core.talk_content_extractor.ConfigManager') as mock_config_class:
            mock_config = Mock()
            mock_config.get_db_path.return_value = temp_db
            mock_config.config = MagicMock()
            mock_config.config.getboolean.return_value = True
            mock_config.get_content_retry_config.return_value = (1, 0)
            mock_config.get_log_config.return_value = {
                'level': 'ERROR',
                'file': 'logs/test.log',
                'console': False
            }
            mock_config_class.return_value = mock_config
            
            extractor = TalkContentExtractor('config.ini', skip_notes=True)
            
            # Validate the incomplete data
            is_valid, error = extractor._validate_talk_data(incomplete_data)
            
            assert is_valid is False
            assert "content" in error.lower()
    
    @pytest.mark.integration
    def test_backup_existing_html_metadata_parsing(self, temp_output_dir):
        """Test that backup_existing_html_metadata correctly parses HTML files."""
        # Create a test HTML file
        html_content = """<!DOCTYPE html>
<html lang="eng">
<head>
    <meta charset="UTF-8">
    <title>Test Talk - Test Author</title>
</head>
<body>
    <div class="header">
        <h1>Test Talk Title</h1>
        <div class="author">Test Author</div>
        <div class="calling">Test Calling</div>
    </div>
    <div class="content">
        <p>Test content paragraph 1</p>
        <p>Test content paragraph 2</p>
    </div>
    <div class="notes">
        <ol>
            <li id="note1">Test note 1</li>
            <li id="note2">Test note 2</li>
        </ol>
    </div>
    <div class="extraction-info">
        <a href="https://example.com/test/1985/10/test-talk" target="_blank">URL</a>
    </div>
</body>
</html>"""
        
        # Create directory structure
        lang_dir = temp_output_dir / 'eng' / '198510'
        lang_dir.mkdir(parents=True, exist_ok=True)
        
        html_file = lang_dir / 'Test Talk (Test Author).html'
        html_file.write_text(html_content, encoding='utf-8')
        
        # Parse the HTML
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # Test extraction
        title_elem = soup.find('h1')
        assert title_elem is not None
        assert title_elem.get_text(strip=True) == "Test Talk Title"
        
        author_elem = soup.find(class_='author')
        assert author_elem is not None
        assert author_elem.get_text(strip=True) == "Test Author"
        
        calling_elem = soup.find(class_='calling')
        assert calling_elem is not None
        assert calling_elem.get_text(strip=True) == "Test Calling"
        
        note_count = len(soup.select('.notes li'))
        assert note_count == 2
        
        url_tag = soup.find('a', href=True)
        assert url_tag is not None
        assert 'example.com' in url_tag['href']
        
        # Test conference_session formatting
        dir_name = html_file.parent.name
        conference_session = TalkContentExtractor._parse_conference_session_from_dirname(dir_name)
        assert conference_session == "1985-10"
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_processing_log_tracks_selenium_failures(self, temp_db):
        """Test that Selenium failures are logged to processing_log."""
        db = DatabaseManager(temp_db)
        
        # Log a Selenium failure
        db.log_operation(
            'selenium_note_extraction',
            'failed',
            language='eng',
            url='https://example.com/test',
            message='Selenium note extraction failed, proceeding with static content only'
        )
        
        # Verify log entry
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM processing_log WHERE operation = ? AND status = ?",
                ('selenium_note_extraction', 'failed')
            )
            result = cursor.fetchone()
            
            assert result is not None
            assert result[1] == 'selenium_note_extraction'  # operation
            assert result[3] == 'https://example.com/test'  # url
            assert result[4] == 'failed'  # status
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_complete_extraction_flow_with_validation(self, temp_db):
        """Test complete extraction flow with validation."""
        db = DatabaseManager(temp_db)
        
        # Sample valid data
        valid_data = CompleteTalkData(
            title="Valid Talk Title",
            author="Valid Author",
            calling="Valid Calling",
            content="This is valid content that is long enough to pass validation checks. " * 5,
            notes=["Note 1", "Note 2"],
            url="https://example.com/valid",
            language="eng",
            year="2024",
            conference_session="2024-04",
            extraction_timestamp="2024-01-01 00:00:00",
            note_count=2
        )
        
        # Store talk URL
        db.store_talk_urls("https://example.com/conf", "eng", [valid_data.url])
        
        # Create extractor
        with patch('core.talk_content_extractor.ConfigManager') as mock_config_class:
            mock_config = Mock()
            mock_config.get_db_path.return_value = temp_db
            mock_config.config = MagicMock()
            mock_config.config.getboolean.return_value = True
            mock_config.get_content_retry_config.return_value = (1, 0)
            mock_config.get_log_config.return_value = {
                'level': 'ERROR',
                'file': 'logs/test.log',
                'console': False
            }
            mock_config_class.return_value = mock_config
            
            extractor = TalkContentExtractor('config.ini', skip_notes=True)
            
            # Validate data
            is_valid, error = extractor._validate_talk_data(valid_data)
            assert is_valid is True
            assert error is None
            
            # Backup metadata
            extractor._backup_talk_metadata(valid_data)
            
            # Verify metadata was stored
            with sqlite3.connect(temp_db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM talk_metadata WHERE url = ?", (valid_data.url,))
                count = cursor.fetchone()[0]
                assert count == 1
                
                cursor.execute("SELECT title, author FROM talk_metadata WHERE url = ?", (valid_data.url,))
                result = cursor.fetchone()
                assert result[0] == "Valid Talk Title"
                assert result[1] == "Valid Author"


class TestMetadataRestoration:
    """Tests for metadata restoration functionality."""
    
    @pytest.mark.integration
    def test_conference_session_format_conversion(self):
        """Test that directory names are correctly converted to conference_session format."""
        test_cases = [
            ('198510', '1985-10'),
            ('202504', '2025-04'),
            ('199004', '1990-04'),
            ('201210', '2012-10'),
        ]
        
        for dir_name, expected in test_cases:
            conference_session = TalkContentExtractor._parse_conference_session_from_dirname(dir_name)
            assert conference_session == expected
    
    @pytest.mark.integration
    def test_invalid_directory_format_handling(self):
        """Test handling of invalid directory formats."""
        invalid_dirs = ['invalid', '12345', 'abcd', '2025', '']
        
        for dir_name in invalid_dirs:
            conference_session = TalkContentExtractor._parse_conference_session_from_dirname(dir_name)
            assert conference_session is None
