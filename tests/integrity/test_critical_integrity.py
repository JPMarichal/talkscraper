"""
Critical Integrity Tests for TalkScraper

These tests ensure that the most critical functionality of Phases 1 & 2
cannot be broken during Phase 3 development. They test the exact scenarios
that must continue working.
"""

import pytest
import requests
import sqlite3
from unittest.mock import patch, Mock
from pathlib import Path

from core.url_collector import URLCollector
from core.talk_url_extractor import TalkURLExtractor
from utils.database_manager import DatabaseManager


@pytest.mark.integrity
@pytest.mark.critical
class TestCriticalPhase1Scenarios:
    """Critical scenarios that Phase 1 must always handle correctly."""
    
    def test_url_collection_basic_workflow(self, test_config_file, temp_dir):
        """Test the basic Phase 1 workflow that must never break."""
        # Use temporary database to avoid conflicts
        from utils.config_manager import ConfigManager
        config = ConfigManager(test_config_file)
        config.config.set('DEFAULT', 'db_file', str(temp_dir / 'critical_test.db'))
        
        temp_config_path = temp_dir / 'critical_config.ini'
        with open(temp_config_path, 'w') as f:
            config.config.write(f)
        
        # This is the exact workflow that main.py Phase 1 uses
        collector = URLCollector(str(temp_config_path))
        
        # Mock the network calls to avoid external dependencies
        with patch.object(collector, '_extract_main_page_urls') as mock_main, \
             patch.object(collector, '_extract_decade_urls') as mock_decade:
            
            mock_main.return_value = [
                'https://www.churchofjesuschrist.org/study/general-conference/2024/04?lang=eng',
                'https://www.churchofjesuschrist.org/study/general-conference/2024/10?lang=eng'
            ]
            mock_decade.return_value = [
                'https://www.churchofjesuschrist.org/study/general-conference/2023/04?lang=eng'
            ]
            
            # Execute the critical workflow
            result = collector.collect_all_urls(['eng'])
            
            # Verify critical requirements
            assert isinstance(result, dict), "collect_all_urls must return a dictionary"
            assert 'eng' in result, "Result must contain requested language"
            assert len(result['eng']) > 0, "Must collect at least some URLs"
            
            # Verify URLs are stored in database
            stored_urls = collector.get_stored_urls('eng')
            assert len(stored_urls) == len(result['eng']), "All URLs must be stored in database"
    
    def test_database_deduplication_critical(self, database_manager):
        """Test that URL deduplication always works (critical for data integrity)."""
        # This is critical - we cannot have duplicate conference URLs
        test_urls = [
            'https://www.churchofjesuschrist.org/study/general-conference/2024/04?lang=eng',
            'https://www.churchofjesuschrist.org/study/general-conference/2024/04?lang=eng',  # Duplicate
            'https://www.churchofjesuschrist.org/study/general-conference/2024/10?lang=eng'
        ]
        
        # Store URLs multiple times
        database_manager.store_conference_urls('eng', test_urls)
        database_manager.store_conference_urls('eng', test_urls)  # Store again
        
        # Must have exactly 2 unique URLs
        stored_urls = database_manager.get_conference_urls('eng')
        unique_urls = set(stored_urls)
        
        assert len(unique_urls) == 2, f"Expected 2 unique URLs, got {len(unique_urls)}: {unique_urls}"
        assert len(stored_urls) == 2, f"Database returned {len(stored_urls)} URLs instead of 2"
    
    def test_configuration_loading_critical(self, test_config_file):
        """Test that configuration loading never fails (critical for startup)."""
        # This must always work or the application won't start
        collector = URLCollector(test_config_file)
        
        # These configuration calls must never fail
        eng_url = collector.config.get_base_url('eng')
        spa_url = collector.config.get_base_url('spa')
        db_path = collector.config.get_db_path()
        user_agent = collector.config.get_user_agent()
        
        # Critical assertions
        assert eng_url is not None and len(eng_url) > 0, "English base URL must be configured"
        assert spa_url is not None and len(spa_url) > 0, "Spanish base URL must be configured"
        assert db_path is not None and len(db_path) > 0, "Database path must be configured"
        assert user_agent is not None and len(user_agent) > 0, "User agent must be configured"
        
        # URLs must be valid HTTP/HTTPS
        assert eng_url.startswith(('http://', 'https://')), f"Invalid English URL: {eng_url}"
        assert spa_url.startswith(('http://', 'https://')), f"Invalid Spanish URL: {spa_url}"


@pytest.mark.integrity
@pytest.mark.critical
class TestCriticalPhase2Scenarios:
    """Critical scenarios that Phase 2 must always handle correctly."""
    
    def test_talk_extraction_basic_workflow(self, test_config_file, temp_dir):
        """Test the basic Phase 2 workflow that must never break."""
        from utils.config_manager import ConfigManager
        config = ConfigManager(test_config_file)
        config.config.set('DEFAULT', 'db_file', str(temp_dir / 'critical_phase2.db'))
        
        temp_config_path = temp_dir / 'critical_phase2_config.ini'
        with open(temp_config_path, 'w') as f:
            config.config.write(f)
        
        # Set up Phase 1 data (Phase 2 depends on this)
        db = DatabaseManager(config.get_db_path())
        conference_urls = [
            'https://www.churchofjesuschrist.org/study/general-conference/2024/04?lang=eng',
            'https://www.churchofjesuschrist.org/study/general-conference/2024/10?lang=eng'
        ]
        db.store_conference_urls('eng', conference_urls)
        db.close()
        
        # Test Phase 2 workflow
        extractor = TalkURLExtractor(str(temp_config_path))
        
        # Mock the talk extraction to avoid network calls
        with patch.object(extractor, '_extract_conference_talk_urls') as mock_extract:
            mock_extract.return_value = [
                'https://www.churchofjesuschrist.org/study/general-conference/2024/04/15nelson?lang=eng',
                'https://www.churchofjesuschrist.org/study/general-conference/2024/04/22eyring?lang=eng'
            ]
            
            # Execute critical workflow
            result = extractor.extract_all_talk_urls(['eng'])
            
            # Critical verifications
            assert isinstance(result, dict), "extract_all_talk_urls must return dictionary"
            assert 'eng' in result, "Result must contain requested language"
            assert isinstance(result['eng'], int), "Result must contain integer count"
            assert result['eng'] > 0, "Must extract at least some talks"
    
    def test_conference_processing_state_critical(self, database_manager):
        """Test that conference processing state is never corrupted (critical for progress)."""
        # This is critical - we must never lose track of what's been processed
        conference_url = 'https://www.churchofjesuschrist.org/study/general-conference/2024/04?lang=eng'
        
        # Store conference
        database_manager.store_conference_urls('eng', [conference_url])
        
        # Initially unprocessed
        unprocessed_before = database_manager.get_unprocessed_conference_urls('eng')
        assert conference_url in unprocessed_before, "Conference must start as unprocessed"
        
        # Mark as processed
        database_manager.mark_conference_processed(conference_url)
        
        # Must no longer be unprocessed
        unprocessed_after = database_manager.get_unprocessed_conference_urls('eng')
        assert conference_url not in unprocessed_after, "Processed conference must not appear as unprocessed"
        
        # Verify statistics reflect the change
        stats = database_manager.get_processing_stats()
        assert stats['conferences']['eng']['processed'] >= 1, "Statistics must reflect processed conference"
    
    def test_url_validation_security_critical(self, test_config_file):
        """Test that URL validation prevents malicious URLs (security critical)."""
        extractor = TalkURLExtractor(test_config_file)
        
        # These malicious/invalid URLs must NEVER be accepted
        malicious_urls = [
            'javascript:alert("xss")',
            'data:text/html,<script>alert("xss")</script>',
            'file:///etc/passwd',
            'ftp://malicious.com/file',
            'https://malicious.com/study/general-conference/2024/04?lang=eng',  # Wrong domain
            'https://www.churchofjesuschrist.org/study/manual/something',  # Wrong path
            'https://www.churchofjesuschrist.org/admin/delete-all',  # Admin path
            '',  # Empty URL
            None,  # None URL
            'not-a-url-at-all',  # Invalid format
        ]
        
        for malicious_url in malicious_urls:
            if malicious_url is not None:
                is_valid_conference = extractor._is_valid_conference_url(malicious_url)
                is_valid_talk = extractor._is_valid_talk_url(malicious_url)
                
                assert not is_valid_conference, f"SECURITY: Malicious URL incorrectly validated as conference: {malicious_url}"
                assert not is_valid_talk, f"SECURITY: Malicious URL incorrectly validated as talk: {malicious_url}"


@pytest.mark.integrity
@pytest.mark.critical  
class TestCriticalDataIntegrity:
    """Critical data integrity tests that must never fail."""
    
    def test_database_connection_resilience(self, temp_dir):
        """Test that database connections are resilient (critical for data safety)."""
        db_path = temp_dir / 'resilience_test.db'
        
        # Multiple connections should work
        db1 = DatabaseManager(str(db_path))
        db2 = DatabaseManager(str(db_path))
        
        try:
            # Write with one connection
            db1.store_conference_urls('eng', ['https://example.com/test1'])
            
            # Read with another connection
            urls = db2.get_conference_urls('eng')
            assert 'https://example.com/test1' in urls, "Data must be accessible across connections"
            
            # Close and reopen
            db1.close()
            db3 = DatabaseManager(str(db_path))
            
            # Data must persist
            urls_after_reopen = db3.get_conference_urls('eng')
            assert 'https://example.com/test1' in urls_after_reopen, "Data must persist after connection close"
            
            db3.close()
            
        finally:
            # Cleanup
            try:
                db1.close()
                db2.close()
            except:
                pass
    
    def test_data_consistency_under_stress(self, database_manager):
        """Test data consistency under rapid operations (critical for reliability)."""
        # Rapid operations that could cause race conditions
        conference_urls = [
            f'https://www.churchofjesuschrist.org/study/general-conference/202{i}/04?lang=eng'
            for i in range(10)
        ]
        
        # Store rapidly
        for url in conference_urls:
            database_manager.store_conference_urls('eng', [url])
        
        # Verify all stored correctly
        stored_urls = database_manager.get_conference_urls('eng')
        for url in conference_urls:
            assert url in stored_urls, f"URL {url} was lost during rapid storage"
        
        # No duplicates should exist
        assert len(stored_urls) == len(set(stored_urls)), "Rapid storage created duplicates"
    
    def test_sql_injection_protection(self, database_manager):
        """Test protection against SQL injection (security critical)."""
        # These URLs contain SQL injection attempts
        malicious_urls = [
            "'; DROP TABLE conference_urls; --",
            "https://example.com/test'; DELETE FROM conference_urls WHERE '1'='1",
            "https://example.com/test' UNION SELECT * FROM sqlite_master --",
            "https://example.com/test'; INSERT INTO conference_urls (url) VALUES ('malicious'); --"
        ]
        
        # These should be stored safely without executing SQL
        for malicious_url in malicious_urls:
            try:
                database_manager.store_conference_urls('eng', [malicious_url])
                
                # Verify the URL is stored as-is, not executed as SQL
                stored_urls = database_manager.get_conference_urls('eng')
                assert malicious_url in stored_urls, f"Malicious URL should be stored safely: {malicious_url}"
                
            except Exception as e:
                pytest.fail(f"SQL injection protection failed for: {malicious_url}. Error: {e}")
        
        # Verify database is still intact (tables should exist)
        with sqlite3.connect(database_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'conference_urls' in tables, "conference_urls table was dropped by SQL injection"
            assert 'talk_urls' in tables, "talk_urls table was dropped by SQL injection"


@pytest.mark.integrity
@pytest.mark.critical
class TestMainAPIIntegrity:
    """Test that the main API contracts never change (critical for main.py)."""
    
    def test_url_collector_api_contract(self, test_config_file):
        """Test that URLCollector API never changes (critical for main.py)."""
        collector = URLCollector(test_config_file)
        
        # These methods must always exist with these signatures
        assert hasattr(collector, 'collect_all_urls'), "collect_all_urls method must exist"
        assert hasattr(collector, 'get_stored_urls'), "get_stored_urls method must exist"
        
        # collect_all_urls must accept list of languages and return dict
        with patch.object(collector, '_collect_language_urls', return_value=['test']):
            result = collector.collect_all_urls(['eng'])
            assert isinstance(result, dict), "collect_all_urls must return dict"
            assert 'eng' in result, "Result must contain requested language"
            assert isinstance(result['eng'], list), "Language result must be list"
    
    def test_talk_extractor_api_contract(self, test_config_file):
        """Test that TalkURLExtractor API never changes (critical for main.py)."""
        extractor = TalkURLExtractor(test_config_file)
        
        # These methods must always exist with these signatures
        assert hasattr(extractor, 'extract_all_talk_urls'), "extract_all_talk_urls method must exist"
        assert hasattr(extractor, 'get_extraction_stats'), "get_extraction_stats method must exist"
        
        # extract_all_talk_urls must accept list of languages and return dict with counts
        with patch.object(extractor, '_extract_language_talk_urls', return_value=10):
            result = extractor.extract_all_talk_urls(['eng'])
            assert isinstance(result, dict), "extract_all_talk_urls must return dict"
            assert 'eng' in result, "Result must contain requested language"
            assert isinstance(result['eng'], int), "Language result must be integer count"
    
    def test_database_manager_api_contract(self, test_db_path):
        """Test that DatabaseManager API never changes (critical for all phases)."""
        db = DatabaseManager(test_db_path)
        
        try:
            # These methods must always exist and work
            critical_methods = [
                'store_conference_urls',
                'get_conference_urls',
                'store_talk_urls',
                'get_unprocessed_conference_urls',
                'mark_conference_processed',
                'get_processing_stats',
                'get_talk_extraction_stats',
                'close'
            ]
            
            for method_name in critical_methods:
                assert hasattr(db, method_name), f"Critical method {method_name} must exist"
            
            # Test basic operations work
            test_url = 'https://example.com/test'
            db.store_conference_urls('eng', [test_url])
            
            stored = db.get_conference_urls('eng')
            assert test_url in stored, "Basic storage/retrieval must work"
            
            stats = db.get_processing_stats()
            assert isinstance(stats, dict), "get_processing_stats must return dict"
            
        finally:
            db.close()
