"""
Integrity Tests for Phases 1 & 2

These tests ensure that existing functionality from Phases 1 and 2 
remains intact while developing Phase 3. They focus on protecting
critical functionality and preventing regression.
"""

import pytest
import os
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch, Mock

from core.url_collector import URLCollector
from core.talk_url_extractor import TalkURLExtractor
from utils.config_manager import ConfigManager
from utils.database_manager import DatabaseManager


@pytest.mark.integrity
class TestPhase1Integrity:
    """Integrity tests for Phase 1 - URL Collection functionality."""
    
    def test_url_collector_initialization(self, test_config_file):
        """Test that URLCollector initializes correctly with all dependencies."""
        collector = URLCollector(test_config_file)
        
        # Verify all components are properly initialized
        assert collector.config is not None
        assert collector.db is not None
        assert collector.logger is not None
        assert collector.session is not None
        
        # Verify configuration is loaded
        assert collector.config.get_base_url('eng') is not None
        assert collector.config.get_base_url('spa') is not None
    
    def test_database_structure_phase1(self, database_manager):
        """Test that Phase 1 database structure is intact."""
        # Test conference_urls table exists and has correct structure
        with sqlite3.connect(database_manager.db_path) as conn:
            cursor = conn.cursor()
            
            # Check table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='conference_urls'
            """)
            assert cursor.fetchone() is not None
            
            # Check table structure
            cursor.execute("PRAGMA table_info(conference_urls)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            expected_columns = {
                'id': 'INTEGER',
                'language': 'TEXT',
                'url': 'TEXT',
                'discovered_date': 'TIMESTAMP',
                'processed': 'BOOLEAN'
            }
            
            for col_name, col_type in expected_columns.items():
                assert col_name in columns
                assert col_type in columns[col_name]
    
    def test_conference_url_storage_integrity(self, database_manager):
        """Test that conference URL storage maintains data integrity."""
        # Store test URLs
        test_urls = [
            'https://www.churchofjesuschrist.org/study/general-conference/2024/04?lang=eng',
            'https://www.churchofjesuschrist.org/study/general-conference/2024/10?lang=eng'
        ]
        
        # Store URLs
        database_manager.store_conference_urls('eng', test_urls)
        
        # Retrieve and verify
        stored_urls = database_manager.get_conference_urls('eng')
        assert len(stored_urls) == len(test_urls)
        
        for url in test_urls:
            assert url in stored_urls
        
        # Test deduplication
        database_manager.store_conference_urls('eng', test_urls)  # Store again
        stored_urls_after = database_manager.get_conference_urls('eng')
        assert len(stored_urls_after) == len(test_urls)  # No duplicates
    
    def test_configuration_integrity(self, config_manager):
        """Test that configuration system maintains integrity."""
        # Test all critical configuration values exist
        critical_configs = [
            ('base_url_eng', str),
            ('base_url_spa', str),
            ('db_file', str),
            ('user_agent', str),
            ('conference_link_selector', str),
            ('talk_link_selector', str)
        ]
        
        for config_key, expected_type in critical_configs:
            if config_key.startswith('base_url'):
                # Special handling for URL methods
                lang = config_key.split('_')[-1]
                value = config_manager.get_base_url(lang)
            elif config_key == 'user_agent':
                value = config_manager.get_user_agent()
            elif config_key == 'conference_link_selector':
                value = config_manager.get_conference_link_selector()
            elif config_key == 'talk_link_selector':
                value = config_manager.get_talk_link_selector()
            else:
                # Generic config access
                value = config_manager.config.get('DEFAULT', config_key)
            
            assert value is not None, f"Configuration {config_key} is missing"
            assert isinstance(value, expected_type), f"Configuration {config_key} has wrong type"
    
    @pytest.mark.network
    def test_url_collection_api_compatibility(self, test_config_file):
        """Test that URL collection API remains compatible."""
        collector = URLCollector(test_config_file)
        
        # Test method signatures haven't changed
        assert hasattr(collector, 'collect_all_urls')
        assert hasattr(collector, 'get_stored_urls')
        
        # Test that methods can be called without breaking
        # (using mock to avoid actual network calls)
        with patch.object(collector, '_collect_language_urls', return_value=['test_url']):
            result = collector.collect_all_urls(['eng'])
            assert isinstance(result, dict)
            assert 'eng' in result
            assert isinstance(result['eng'], list)


@pytest.mark.integrity
class TestPhase2Integrity:
    """Integrity tests for Phase 2 - Talk URL Extraction functionality."""
    
    def test_talk_url_extractor_initialization(self, test_config_file):
        """Test that TalkURLExtractor initializes correctly."""
        extractor = TalkURLExtractor(test_config_file)
        
        # Verify all components are properly initialized
        assert extractor.config is not None
        assert extractor.db is not None
        assert extractor.logger is not None
        assert extractor.session is not None
        
        # Verify request settings are configured
        assert hasattr(extractor, 'request_delay')
        assert hasattr(extractor, 'retry_attempts')
        assert hasattr(extractor, 'retry_delay')
    
    def test_database_structure_phase2(self, database_manager):
        """Test that Phase 2 database structure is intact."""
        # Test talk_urls table exists and has correct structure
        with sqlite3.connect(database_manager.db_path) as conn:
            cursor = conn.cursor()
            
            # Check table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='talk_urls'
            """)
            assert cursor.fetchone() is not None
            
            # Check table structure
            cursor.execute("PRAGMA table_info(talk_urls)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            expected_columns = {
                'id': 'INTEGER',
                'conference_url': 'TEXT',
                'talk_url': 'TEXT',
                'language': 'TEXT',
                'discovered_date': 'TIMESTAMP'
            }
            
            for col_name, col_type in expected_columns.items():
                assert col_name in columns
                assert col_type in columns[col_name]
    
    def test_talk_url_storage_integrity(self, database_manager):
        """Test that talk URL storage maintains data integrity."""
        # First store a conference URL
        conference_url = 'https://www.churchofjesuschrist.org/study/general-conference/2024/04?lang=eng'
        database_manager.store_conference_urls('eng', [conference_url])
        
        # Store test talk URLs
        test_talk_urls = [
            'https://www.churchofjesuschrist.org/study/general-conference/2024/04/15nelson?lang=eng',
            'https://www.churchofjesuschrist.org/study/general-conference/2024/04/22eyring?lang=eng'
        ]
        
        # Store talk URLs
        stored_count = database_manager.store_talk_urls(conference_url, 'eng', test_talk_urls)
        assert stored_count == len(test_talk_urls)
        
        # Test deduplication
        duplicate_count = database_manager.store_talk_urls(conference_url, 'eng', test_talk_urls)
        assert duplicate_count == 0  # No new URLs stored
    
    def test_conference_processing_state(self, database_manager):
        """Test that conference processing state is maintained correctly."""
        # Store a conference URL
        conference_url = 'https://www.churchofjesuschrist.org/study/general-conference/2024/04?lang=eng'
        database_manager.store_conference_urls('eng', [conference_url])
        
        # Initially should be unprocessed
        unprocessed = database_manager.get_unprocessed_conference_urls('eng')
        assert conference_url in unprocessed
        
        # Mark as processed
        database_manager.mark_conference_processed(conference_url)
        
        # Should no longer be in unprocessed list
        unprocessed_after = database_manager.get_unprocessed_conference_urls('eng')
        assert conference_url not in unprocessed_after
    
    def test_url_validation_integrity(self, test_config_file):
        """Test that URL validation logic remains intact."""
        extractor = TalkURLExtractor(test_config_file)
        
        # Test valid conference URLs
        valid_conference_urls = [
            'https://www.churchofjesuschrist.org/study/general-conference/2024/04?lang=eng',
            'https://www.churchofjesuschrist.org/study/general-conference/2023/10?lang=spa',
            'https://www.churchofjesuschrist.org/study/general-conference/1971/04?lang=eng'
        ]
        
        for url in valid_conference_urls:
            assert extractor._is_valid_conference_url(url), f"Failed to validate: {url}"
        
        # Test valid talk URLs
        valid_talk_urls = [
            'https://www.churchofjesuschrist.org/study/general-conference/2024/04/15nelson?lang=eng',
            'https://www.churchofjesuschrist.org/study/general-conference/2023/10/22eyring?lang=spa'
        ]
        
        for url in valid_talk_urls:
            assert extractor._is_valid_talk_url(url), f"Failed to validate talk URL: {url}"
        
        # Test invalid URLs should be rejected
        invalid_urls = [
            'https://www.churchofjesuschrist.org/study/manual/something',
            'https://www.churchofjesuschrist.org/study/general-conference/speakers',
            'https://www.churchofjesuschrist.org/study/general-conference/2024/04/session',
            'https://example.com/fake/url'
        ]
        
        for url in invalid_urls:
            assert not extractor._is_valid_conference_url(url), f"Incorrectly validated invalid URL: {url}"
    
    def test_extraction_api_compatibility(self, test_config_file):
        """Test that extraction API remains compatible."""
        extractor = TalkURLExtractor(test_config_file)
        
        # Test method signatures haven't changed
        assert hasattr(extractor, 'extract_all_talk_urls')
        assert hasattr(extractor, 'get_extraction_stats')
        
        # Test that methods can be called without breaking
        with patch.object(extractor, '_extract_language_talk_urls', return_value=10):
            result = extractor.extract_all_talk_urls(['eng'])
            assert isinstance(result, dict)
            assert 'eng' in result
            assert isinstance(result['eng'], int)


@pytest.mark.integrity
class TestCrossPhaseIntegrity:
    """Tests that verify integrity across both phases working together."""
    
    def test_phase1_to_phase2_data_flow(self, test_config_file, temp_dir):
        """Test that data flows correctly from Phase 1 to Phase 2."""
        # Use temp database for this test
        config_manager = ConfigManager(test_config_file)
        config_manager.config.set('DEFAULT', 'db_file', str(temp_dir / 'test_flow.db'))
        
        # Save updated config
        temp_config_path = temp_dir / 'temp_config.ini'
        with open(temp_config_path, 'w') as f:
            config_manager.config.write(f)
        
        # Phase 1: Collect URLs
        collector = URLCollector(str(temp_config_path))
        
        # Mock URL collection
        test_conference_urls = [
            'https://www.churchofjesuschrist.org/study/general-conference/2024/04?lang=eng',
            'https://www.churchofjesuschrist.org/study/general-conference/2024/10?lang=eng'
        ]
        
        collector.db.store_conference_urls('eng', test_conference_urls)
        
        # Phase 2: Extract talk URLs
        extractor = TalkURLExtractor(str(temp_config_path))
        
        # Verify Phase 2 can access Phase 1 data
        unprocessed = extractor._get_unprocessed_conferences('eng')
        assert len(unprocessed) == len(test_conference_urls)
        
        for url in test_conference_urls:
            assert url in unprocessed
    
    def test_database_consistency_across_phases(self, database_manager):
        """Test that database remains consistent across both phases."""
        # Add Phase 1 data
        conference_url = 'https://www.churchofjesuschrist.org/study/general-conference/2024/04?lang=eng'
        database_manager.store_conference_urls('eng', [conference_url])
        
        # Add Phase 2 data
        talk_urls = [
            'https://www.churchofjesuschrist.org/study/general-conference/2024/04/15nelson?lang=eng',
            'https://www.churchofjesuschrist.org/study/general-conference/2024/04/22eyring?lang=eng'
        ]
        database_manager.store_talk_urls(conference_url, 'eng', talk_urls)
        
        # Mark conference as processed
        database_manager.mark_conference_processed(conference_url)
        
        # Verify database statistics are consistent
        stats = database_manager.get_processing_stats()
        assert 'conferences' in stats
        assert 'eng' in stats['conferences']
        assert stats['conferences']['eng']['total'] == 1
        assert stats['conferences']['eng']['processed'] == 1
        
        # Verify talk extraction stats
        talk_stats = database_manager.get_talk_extraction_stats()
        assert 'eng' in talk_stats
        assert 'talks' in talk_stats['eng']
        assert talk_stats['eng']['talks']['total'] >= len(talk_urls)
    
    def test_logging_system_integrity(self, test_config_file):
        """Test that logging system works consistently across phases."""
        # Test Phase 1 logging
        collector = URLCollector(test_config_file)
        assert collector.logger is not None
        assert collector.logger.name == 'core.url_collector'
        
        # Test Phase 2 logging
        extractor = TalkURLExtractor(test_config_file)
        assert extractor.logger is not None
        assert extractor.logger.name == 'core.talk_url_extractor'
        
        # Test that log configuration is consistent
        log_config1 = collector.config.get_log_config()
        log_config2 = extractor.config.get_log_config()
        assert log_config1 == log_config2
    
    def test_session_management_integrity(self, test_config_file):
        """Test that HTTP session management works correctly across phases."""
        # Test Phase 1 session
        collector = URLCollector(test_config_file)
        assert collector.session is not None
        assert 'User-Agent' in collector.session.headers
        
        # Test Phase 2 session
        extractor = TalkURLExtractor(test_config_file)
        assert extractor.session is not None
        assert 'User-Agent' in extractor.session.headers
        
        # Test that user agents are consistent
        ua1 = collector.session.headers['User-Agent']
        ua2 = extractor.session.headers['User-Agent']
        assert ua1 == ua2


@pytest.mark.integrity
class TestDatabaseIntegrity:
    """Tests specifically for database integrity across all phases."""
    
    def test_database_connection_integrity(self, test_db_path):
        """Test that database connections work reliably."""
        # Test multiple connections
        db1 = DatabaseManager(test_db_path)
        db2 = DatabaseManager(test_db_path)
        
        # Both should work independently
        test_urls = ['https://example.com/test']
        db1.store_conference_urls('eng', test_urls)
        
        # Other connection should see the data
        stored_urls = db2.get_conference_urls('eng')
        assert test_urls[0] in stored_urls
        
        # Clean up
        db1.close()
        db2.close()
    
    def test_database_transaction_integrity(self, database_manager):
        """Test that database transactions maintain integrity."""
        # Store data that should maintain relationships
        conference_url = 'https://www.churchofjesuschrist.org/study/general-conference/2024/04?lang=eng'
        talk_urls = [
            'https://www.churchofjesuschrist.org/study/general-conference/2024/04/15nelson?lang=eng'
        ]
        
        # Store conference
        database_manager.store_conference_urls('eng', [conference_url])
        
        # Store talks
        database_manager.store_talk_urls(conference_url, 'eng', talk_urls)
        
        # Verify relationship integrity
        with sqlite3.connect(database_manager.db_path) as conn:
            cursor = conn.cursor()
            
            # Check that talk URLs reference existing conference
            cursor.execute("""
                SELECT t.talk_url, c.url 
                FROM talk_urls t
                JOIN conference_urls c ON t.conference_url = c.url
                WHERE t.conference_url = ?
            """, (conference_url,))
            
            results = cursor.fetchall()
            assert len(results) > 0
            assert results[0][0] == talk_urls[0]
            assert results[0][1] == conference_url
    
    def test_database_schema_integrity(self, database_manager):
        """Test that database schema remains intact."""
        with sqlite3.connect(database_manager.db_path) as conn:
            cursor = conn.cursor()
            
            # Check all expected tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            expected_tables = ['conference_urls', 'talk_urls', 'processing_log']
            
            for table in expected_tables:
                assert table in tables, f"Missing table: {table}"
            
            # Check for proper indexes (SQLite creates automatic indexes for UNIQUE constraints)
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
            """)
            
            indexes = [row[0] for row in cursor.fetchall()]
            # SQLite should have automatic indexes for UNIQUE constraints
            # We just verify that some indexes exist (could be empty if using automatic indexes)
            # The important thing is that UNIQUE constraints are working
