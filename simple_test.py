#!/usr/bin/env python3
"""Simple test to debug URL extraction and content parsing."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import sqlite3
from utils.database_manager import DatabaseManager

# Test the URL extraction directly
def test_url_extraction_simple():
    print("=== Simple URL Extraction Test ===")
    
    db = DatabaseManager('talkscraper_state.db')
    
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        # Get 5 random English URLs
        cursor.execute(
            'SELECT talk_url FROM talk_urls WHERE language = ? ORDER BY RANDOM() LIMIT ?',
            ('eng', 5)
        )
        urls = [row[0] for row in cursor.fetchall()]
        
        print(f"Found {len(urls)} URLs:")
        for i, url in enumerate(urls, 1):
            print(f"  {i}. {url}")
    
    db.close()
    
    if not urls:
        print("❌ No URLs found!")
        return []
    
    # Test the extraction on one URL
    from tests.integrity.test_phase3_content_extraction import BasicContentExtractor
    
    test_config = 'config.ini'
    extractor = BasicContentExtractor(test_config)
    
    print(f"\n=== Testing extraction on first URL ===")
    test_url = urls[0]
    print(f"Testing: {test_url}")
    
    metadata = extractor.extract_talk_metadata(test_url)
    
    if metadata:
        print(f"✅ Success!")
        print(f"   Title: {metadata.title}")
        print(f"   Author: {metadata.author}")
        print(f"   Calling: {metadata.calling}")
        print(f"   Content length: {len(metadata.content)} chars")
        print(f"   Year: {metadata.year}")
    else:
        print(f"❌ Failed to extract metadata")
    
    return urls

if __name__ == '__main__':
    test_url_extraction_simple()
