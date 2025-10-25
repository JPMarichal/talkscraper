"""
Integration tests for URL collection functionality.

Tests the complete URL collection process including
HTTP requests, HTML parsing, and database storage.
"""

import pytest
import responses
from unittest.mock import patch

from core.url_collector import URLCollector


class TestURLCollectorIntegration:
    """Integration test suite for URLCollector class."""
    
    @pytest.mark.integration
    @pytest.mark.network
    def test_collect_all_urls_success(self, test_config_file, comprehensive_mock_requests, 
                                     sample_html_main_page):
        """Test successful collection of URLs for all languages."""
        collector = URLCollector(test_config_file)
        results = collector.collect_all_urls(['eng', 'spa'])
        
        assert 'eng' in results
        assert 'spa' in results
        assert len(results['eng']) > 0
        assert len(results['spa']) > 0
        
    @pytest.mark.integration
    @pytest.mark.network
    def test_collect_single_language_urls(self, test_config_file, comprehensive_mock_requests,
                                         sample_html_main_page):
        """Test collection of URLs for a single language."""
        collector = URLCollector(test_config_file)
        results = collector.collect_all_urls(['eng'])
        
        assert 'eng' in results
        assert 'spa' not in results
        assert len(results['eng']) > 0
        
    @pytest.mark.integration
    @pytest.mark.network
    def test_collect_urls_http_error(self, test_config_file, mock_requests):
        """Test handling of HTTP errors during URL collection."""
        mock_requests.add(
            responses.GET,
            'https://test.example.com/eng',
            status=404
        )
        
        collector = URLCollector(test_config_file)
        
        # Should handle HTTP error gracefully
        with pytest.raises(Exception):
            collector.collect_all_urls(['eng'])
            
    @pytest.mark.integration
    @pytest.mark.network
    def test_collect_urls_connection_error(self, test_config_file):
        """Test handling of connection errors."""
        collector = URLCollector(test_config_file)
        
        # Mock requests to raise connection error
        with patch('requests.get') as mock_get:
            mock_get.side_effect = ConnectionError("Connection failed")
            
            with pytest.raises(ConnectionError):
                collector.collect_all_urls(['eng'])
                
    @pytest.mark.integration
    @pytest.mark.database
    def test_url_collection_with_database_storage(self, test_config_file, 
                                                  mock_requests, sample_html_main_page,
                                                  temp_dir):
        """Test that collected URLs are properly stored in database."""
        # Update config to use temp database
        from utils.config_manager import ConfigManager
        config_manager = ConfigManager(test_config_file)
        config_manager.config.set('DEFAULT', 'db_file', str(temp_dir / 'test.db'))
        
        mock_requests.add(
            responses.GET,
            'https://test.example.com/eng',
            body=sample_html_main_page,
            status=200
        )
        
        collector = URLCollector(test_config_file)
        results = collector.collect_all_urls(['eng'])
        
        # Verify URLs are stored in database
        stored_urls = collector.db.get_conference_urls('eng')
        assert len(stored_urls) == len(results['eng'])
        
    @pytest.mark.integration
    @pytest.mark.slow
    def test_decade_url_extraction(self, test_config_file, mock_requests):
        """Test extraction of URLs from decade archive pages."""
        decade_html = '''
        <html>
        <body>
            <div class="conferences">
                <a class="test-conference" href="/study/general-conference/2015/04?lang=eng">April 2015</a>
                <a class="test-conference" href="/study/general-conference/2015/10?lang=eng">October 2015</a>
                <a class="test-conference" href="/study/general-conference/2014/04?lang=eng">April 2014</a>
            </div>
        </body>
        </html>
        '''
        
        # Mock main page that includes decade links
        main_page_html = '''
        <html>
        <body>
            <div class="conferences">
                <a class="test-decade" href="/study/general-conference/decades/2010?lang=eng">2010s</a>
            </div>
        </body>
        </html>
        '''
        
        mock_requests.add(
            responses.GET,
            'https://test.example.com/eng',
            body=main_page_html,
            status=200
        )
        
        mock_requests.add(
            responses.GET,
            'https://test.example.com/study/general-conference/decades/2010?lang=eng',
            body=decade_html,
            status=200
        )
        
        collector = URLCollector(test_config_file)
        results = collector.collect_all_urls(['eng'])
        
        # Should have collected URLs from both main page and decade page
        assert len(results['eng']) > 0
        
    @pytest.mark.integration
    def test_url_deduplication(self, test_config_file, mock_requests):
        """Test that duplicate URLs are properly deduplicated."""
        html_with_duplicates = '''
        <html>
        <body>
            <div class="conferences">
                <a class="test-conference" href="/study/general-conference/2024/04?lang=eng">April 2024</a>
                <a class="test-conference" href="/study/general-conference/2024/04?lang=eng">April 2024 (duplicate)</a>
                <a class="test-conference" href="/study/general-conference/2024/10?lang=eng">October 2024</a>
            </div>
        </body>
        </html>
        '''
        
        mock_requests.add(
            responses.GET,
            'https://test.example.com/eng',
            body=html_with_duplicates,
            status=200
        )
        
        collector = URLCollector(test_config_file)
        results = collector.collect_all_urls(['eng'])
        
        # Should have deduplicated the URLs
        unique_urls = set(results['eng'])
        assert len(unique_urls) == len(results['eng'])
        
    @pytest.mark.integration
    @pytest.mark.database
    def test_incremental_url_collection(self, test_config_file, mock_requests,
                                       sample_html_main_page, temp_dir):
        """Test that incremental collection works properly."""
        # Update config to use temp database
        from utils.config_manager import ConfigManager
        config_manager = ConfigManager(test_config_file)
        config_manager.config.set('DEFAULT', 'db_file', str(temp_dir / 'test.db'))
        
        mock_requests.add(
            responses.GET,
            'https://test.example.com/eng',
            body=sample_html_main_page,
            status=200
        )
        
        # First collection
        collector1 = URLCollector(test_config_file)
        results1 = collector1.collect_all_urls(['eng'])
        
        # Second collection (should not duplicate)
        collector2 = URLCollector(test_config_file)
        results2 = collector2.collect_all_urls(['eng'])
        
        # Results should be the same
        assert len(results1['eng']) == len(results2['eng'])
        
        # Database should not have duplicates
        stored_urls = collector2.db.get_conference_urls('eng')
        assert len(stored_urls) == len(results1['eng'])
        
    @pytest.mark.integration
    def test_statistics_after_collection(self, test_config_file, mock_requests,
                                        sample_html_main_page):
        """Test that statistics are properly updated after collection."""
        mock_requests.add(
            responses.GET,
            'https://test.example.com/eng',
            body=sample_html_main_page,
            status=200
        )
        
        collector = URLCollector(test_config_file)
        results = collector.collect_all_urls(['eng'])
        
        stats = collector.db.get_processing_stats()
        
        assert 'conferences' in stats
        assert 'eng' in stats['conferences']
        assert stats['conferences']['eng']['total'] == len(results['eng'])
        assert stats['conferences']['eng']['processed'] == 0  # None processed yet
