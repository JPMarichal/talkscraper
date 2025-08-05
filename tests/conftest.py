"""
Testing configuration and fixtures for TalkScraper

This module contains shared fixtures, test utilities, and configuration
for the entire test suite. It follows pytest best practices and supports
both unit and integration testing.
"""

import os
import tempfile
import sqlite3
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch

import pytest
import responses
from freezegun import freeze_time

# Add src to Python path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config_manager import ConfigManager
from utils.database_manager import DatabaseManager
from utils.logger_setup import setup_logger


# Test Configuration Constants
TEST_CONFIG = {
    'DEFAULT': {
        'base_url_eng': 'https://test.example.com/eng',
        'base_url_spa': 'https://test.example.com/spa',
        'eng_dir': 'conf/eng',
        'spa_dir': 'conf/spa',
        'output_dir': 'conf',
        'db_file': 'test_talkscraper.db',
        'concurrent_downloads': '3',
        'request_delay': '0.1',
        'log_level': 'INFO',
        'log_file': 'logs/test_talkscraper.log'
    },
    'SCRAPING': {
        'user_agent': 'TalkScraper-Test/1.0',
        'selenium_headless': 'true',
        'conference_link_selector': 'a.test-conference',
        'talk_link_selector': 'a.test-talk',
        'decade_link_selector': 'a.test-decade'
    },
    'LOGGING': {
        'level': 'INFO',
        'file': 'logs/test_talkscraper.log'
    }
}

SAMPLE_CONFERENCE_URLS = {
    'eng': [
        'https://www.churchofjesuschrist.org/study/general-conference/2024/04?lang=eng',
        'https://www.churchofjesuschrist.org/study/general-conference/2024/10?lang=eng',
        'https://www.churchofjesuschrist.org/study/general-conference/2023/10?lang=eng'
    ],
    'spa': [
        'https://www.churchofjesuschrist.org/study/general-conference/2024/04?lang=spa',
        'https://www.churchofjesuschrist.org/study/general-conference/2024/10?lang=spa'
    ]
}

SAMPLE_TALK_URLS = {
    'eng': [
        'https://www.churchofjesuschrist.org/study/general-conference/2024/04/15holland?lang=eng',
        'https://www.churchofjesuschrist.org/study/general-conference/2024/04/16nelson?lang=eng'
    ],
    'spa': [
        'https://www.churchofjesuschrist.org/study/general-conference/2024/04/15holland?lang=spa',
        'https://www.churchofjesuschrist.org/study/general-conference/2024/04/16nelson?lang=spa'
    ]
}


@pytest.fixture(scope="session")
def test_config_dict():
    """Return test configuration dictionary."""
    return TEST_CONFIG


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    import tempfile
    import shutil
    import gc
    
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    
    # Force garbage collection to close any open file handles
    gc.collect()
    
    # Custom cleanup that handles Windows file locking
    import time
    for attempt in range(5):
        try:
            shutil.rmtree(tmpdir, ignore_errors=True)
            break
        except (OSError, PermissionError):
            time.sleep(0.2)
            continue


@pytest.fixture
def test_config_file(temp_dir):
    """Create a temporary config file for testing."""
    config_path = temp_dir / "test_config.ini"
    
    # Create ConfigParser instance and write test config
    import configparser
    config = configparser.ConfigParser()
    
    # Set DEFAULT section values directly without adding section
    for key, value in TEST_CONFIG['DEFAULT'].items():
        config.set('DEFAULT', key, value)
    
    # Add other sections normally
    for section_name, section_data in TEST_CONFIG.items():
        if section_name != 'DEFAULT':
            config.add_section(section_name)
            for key, value in section_data.items():
                config.set(section_name, key, value)
    
    with open(config_path, 'w') as f:
        config.write(f)
    
    return str(config_path)


@pytest.fixture
def test_db_path(temp_dir):
    """Create a temporary database path for testing."""
    return str(temp_dir / "test_db.sqlite")


@pytest.fixture
def config_manager(test_config_file):
    """Create a ConfigManager instance for testing."""
    return ConfigManager(test_config_file)


@pytest.fixture
def database_manager(test_db_path):
    """Create a DatabaseManager instance for testing."""
    db_manager = DatabaseManager(test_db_path)
    yield db_manager
    # Just close the connection, let temp_dir handle file cleanup
    try:
        db_manager.close()
    except:
        pass


@pytest.fixture
def populated_database(database_manager):
    """Create a database populated with test data."""
    # Store sample conference URLs
    for language, urls in SAMPLE_CONFERENCE_URLS.items():
        database_manager.store_conference_urls(language, urls)
    
    # Store sample talk URLs
    for language, urls in SAMPLE_TALK_URLS.items():
        if SAMPLE_CONFERENCE_URLS[language]:
            conference_url = SAMPLE_CONFERENCE_URLS[language][0]
            database_manager.store_talk_urls(conference_url, language, urls)
    
    return database_manager


@pytest.fixture
def mock_requests():
    """Mock requests for HTTP calls."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def sample_html_conference():
    """Return sample HTML content for a conference page."""
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Test Conference</title></head>
    <body>
        <nav>
            <ul>
                <li><a class="test-talk" href="/study/general-conference/2024/04/talk1?lang=eng">Talk 1</a></li>
                <li><a class="test-talk" href="/study/general-conference/2024/04/talk2?lang=eng">Talk 2</a></li>
                <li><a class="test-talk" href="/study/general-conference/2024/04/talk3?lang=eng">Talk 3</a></li>
            </ul>
        </nav>
    </body>
    </html>
    '''


@pytest.fixture
def sample_html_main_page():
    """Return sample HTML content for the main conference page."""
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>General Conference</title></head>
    <body>
        <div class="conferences">
            <a class="test-conference" href="/study/general-conference/2024/04?lang=eng">April 2024</a>
            <a class="test-conference" href="/study/general-conference/2024/10?lang=eng">October 2024</a>
            <a class="test-decade" href="/study/general-conference/decades/2010?lang=eng">2010s</a>
        </div>
    </body>
    </html>
    '''


@pytest.fixture
def sample_talk_content():
    """Return sample HTML content for a talk page."""
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Test Talk</title></head>
    <body>
        <article>
            <h1>The Power of Faith</h1>
            <p class="author">By Elder Jeffrey R. Holland</p>
            <p class="position">Of the Quorum of the Twelve Apostles</p>
            <div class="content">
                <p>My dear brothers and sisters, I speak to you today about faith...</p>
                <p>Faith is the first principle of the gospel...</p>
                <div class="notes">
                    <p class="note">1. See Hebrews 11:1</p>
                    <p class="note">2. See Alma 32:21</p>
                </div>
            </div>
        </article>
    </body>
    </html>
    '''


@pytest.fixture
def test_logger():
    """Create a test logger."""
    config = {
        'level': 'DEBUG',
        'file': 'logs/test.log'
    }
    return setup_logger('test_logger', config)


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, temp_dir):
    """Setup test environment variables and paths."""
    # Set environment variables
    monkeypatch.setenv('PYTEST_RUNNING', '1')
    
    # Change to temp directory for test runs
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    
    yield
    
    # Cleanup
    os.chdir(original_cwd)


# Utility functions for tests
def create_mock_response(content: str, status_code: int = 200, 
                        headers: Dict[str, str] = None) -> Mock:
    """Create a mock response object."""
    mock_response = Mock()
    mock_response.content = content.encode('utf-8')
    mock_response.text = content
    mock_response.status_code = status_code
    mock_response.headers = headers or {'Content-Type': 'text/html'}
    mock_response.raise_for_status.return_value = None
    return mock_response


def assert_database_state(db_manager: DatabaseManager, 
                         expected_conferences: Dict[str, int],
                         expected_talks: Dict[str, int] = None):
    """Assert the expected state of the database."""
    stats = db_manager.get_processing_stats()
    
    # Check conference counts
    if expected_conferences:
        for lang, count in expected_conferences.items():
            assert stats['conferences'][lang]['total'] == count, \
                f"Expected {count} conferences for {lang}, got {stats['conferences'][lang]['total']}"
    
    # Check talk counts
    if expected_talks:
        for lang, count in expected_talks.items():
            assert stats['talks'][lang]['total'] == count, \
                f"Expected {count} talks for {lang}, got {stats['talks'][lang]['total']}"


# Test markers for custom test categories
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )
    config.addinivalue_line(
        "markers", "network: mark test as requiring network"
    )
    config.addinivalue_line(
        "markers", "database: mark test as requiring database"
    )
    config.addinivalue_line(
        "markers", "selenium: mark test as requiring selenium"
    )


def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their path."""
    for item in items:
        # Add unit marker to unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add database marker to database tests
        if "database" in item.name or "db" in item.name:
            item.add_marker(pytest.mark.database)
        
        # Add network marker to network tests
        if "network" in item.name or "http" in item.name or "request" in item.name:
            item.add_marker(pytest.mark.network)
