"""
Unit tests for DatabaseManager class.

Tests database operations including URL storage, retrieval,
and state management.
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime

from utils.database_manager import DatabaseManager


class TestDatabaseManager:
    """Test suite for DatabaseManager class."""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_init_creates_database(self, test_db_path):
        """Test that initialization creates database and tables."""
        db_manager = DatabaseManager(test_db_path)
        
        assert Path(test_db_path).exists()
        
        # Check that tables exist
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['conference_urls', 'talk_urls', 'processing_log']
        for table in expected_tables:
            assert table in tables
            
        db_manager.close()
        
    @pytest.mark.unit
    @pytest.mark.database
    def test_store_conference_urls(self, database_manager):
        """Test storing conference URLs."""
        test_urls = [
            'https://example.com/conference1',
            'https://example.com/conference2'
        ]
        
        count = database_manager.store_conference_urls('eng', test_urls)
        
        assert count == 2
        
        # Verify URLs are stored
        stored_urls = database_manager.get_conference_urls('eng')
        assert len(stored_urls) == 2
        assert all(url in stored_urls for url in test_urls)
        
    @pytest.mark.unit
    @pytest.mark.database
    def test_store_duplicate_conference_urls(self, database_manager):
        """Test that duplicate URLs are not stored."""
        test_urls = [
            'https://example.com/conference1',
            'https://example.com/conference1',  # Duplicate
            'https://example.com/conference2'
        ]
        
        count = database_manager.store_conference_urls('eng', test_urls)
        
        # Should only store unique URLs
        assert count == 2
        
        stored_urls = database_manager.get_conference_urls('eng')
        assert len(stored_urls) == 2
        
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_conference_urls_unprocessed_only(self, database_manager):
        """Test getting only unprocessed conference URLs."""
        test_urls = [
            'https://example.com/conference1',
            'https://example.com/conference2'
        ]
        
        database_manager.store_conference_urls('eng', test_urls)
        
        # Mark one as processed
        database_manager.mark_conference_processed(test_urls[0])
        
        # Get only unprocessed
        unprocessed = database_manager.get_conference_urls('eng', unprocessed_only=True)
        assert len(unprocessed) == 1
        assert test_urls[1] in unprocessed
        assert test_urls[0] not in unprocessed
        
    @pytest.mark.unit
    @pytest.mark.database
    def test_store_talk_urls(self, database_manager):
        """Test storing talk URLs."""
        conference_url = 'https://example.com/conference1'
        talk_urls = [
            'https://example.com/talk1',
            'https://example.com/talk2'
        ]
        
        count = database_manager.store_talk_urls(conference_url, 'eng', talk_urls)
        
        assert count == 2
        
    @pytest.mark.unit
    @pytest.mark.database
    def test_store_duplicate_talk_urls(self, database_manager):
        """Test that duplicate talk URLs are not stored."""
        conference_url = 'https://example.com/conference1'
        talk_urls = [
            'https://example.com/talk1',
            'https://example.com/talk1',  # Duplicate
            'https://example.com/talk2'
        ]
        
        count = database_manager.store_talk_urls(conference_url, 'eng', talk_urls)
        
        # Should only store unique URLs
        assert count == 2
        
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_processing_stats(self, populated_database):
        """Test getting processing statistics."""
        stats = populated_database.get_processing_stats()
        
        assert 'conferences' in stats
        assert 'talks' in stats
        
        # Check that we have data for both languages
        assert 'eng' in stats['conferences']
        assert 'spa' in stats['conferences']
        
        # Check structure
        eng_conf = stats['conferences']['eng']
        assert 'total' in eng_conf
        assert 'processed' in eng_conf
        assert eng_conf['total'] > 0
        
    @pytest.mark.unit
    @pytest.mark.database
    def test_mark_conference_processed(self, database_manager):
        """Test marking a conference as processed."""
        test_url = 'https://example.com/conference1'
        database_manager.store_conference_urls('eng', [test_url])
        
        # Initially should be unprocessed
        unprocessed = database_manager.get_conference_urls('eng', unprocessed_only=True)
        assert test_url in unprocessed
        
        # Mark as processed
        database_manager.mark_conference_processed(test_url)
        
        # Should no longer be in unprocessed list
        unprocessed = database_manager.get_conference_urls('eng', unprocessed_only=True)
        assert test_url not in unprocessed
        
    @pytest.mark.unit
    @pytest.mark.database
    def test_log_operation(self, database_manager):
        """Test logging operations to database."""
        database_manager.log_operation(
            operation='test_operation',
            status='success',
            language='eng',
            url='https://example.com/test',
            message='Test message'
        )
        
        # Verify log entry exists
        with sqlite3.connect(database_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM processing_log WHERE operation = ?', ('test_operation',))
            log_entry = cursor.fetchone()
        
        assert log_entry is not None
        assert log_entry[1] == 'test_operation'  # operation
        assert log_entry[4] == 'success'  # status
        
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_unprocessed_conference_urls(self, database_manager):
        """Test getting unprocessed conference URLs."""
        test_urls = [
            'https://example.com/conference1',
            'https://example.com/conference2',
            'https://example.com/conference3'
        ]
        
        database_manager.store_conference_urls('eng', test_urls)
        
        # Mark some as processed
        database_manager.mark_conference_processed(test_urls[0])
        database_manager.mark_conference_processed(test_urls[2])
        
        unprocessed = database_manager.get_unprocessed_conference_urls('eng')
        
        assert len(unprocessed) == 1
        assert test_urls[1] in unprocessed
        
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_talk_extraction_stats(self, populated_database):
        """Test getting talk extraction statistics."""
        stats = populated_database.get_talk_extraction_stats()
        
        assert isinstance(stats, dict)
        
        # Should have language keys
        for lang in ['eng', 'spa']:
            if lang in stats:
                lang_stats = stats[lang]
                if 'talks' in lang_stats:
                    assert 'total' in lang_stats['talks']
                    assert 'processed' in lang_stats['talks']
                    assert 'pending' in lang_stats['talks']
                    
    @pytest.mark.unit
    @pytest.mark.database
    def test_database_with_invalid_path(self):
        """Test database creation with invalid path."""
        invalid_path = '/invalid/path/that/does/not/exist/db.sqlite'
        
        # Should raise an exception when trying to create database
        with pytest.raises(Exception):
            db_manager = DatabaseManager(invalid_path)
            # Try to perform an operation that requires database access
            db_manager.store_conference_urls('eng', ['test_url'])
            
    @pytest.mark.unit
    @pytest.mark.database
    def test_concurrent_database_access(self, database_manager):
        """Test that multiple operations can be performed safely."""
        # Simulate concurrent operations
        urls1 = ['https://example.com/conf1', 'https://example.com/conf2']
        urls2 = ['https://example.com/conf3', 'https://example.com/conf4']
        
        # Store URLs from different "processes"
        count1 = database_manager.store_conference_urls('eng', urls1)
        count2 = database_manager.store_conference_urls('spa', urls2)
        
        assert count1 == 2
        assert count2 == 2
        
        # Verify both sets are stored
        eng_urls = database_manager.get_conference_urls('eng')
        spa_urls = database_manager.get_conference_urls('spa')
        
        assert len(eng_urls) == 2
        assert len(spa_urls) == 2
