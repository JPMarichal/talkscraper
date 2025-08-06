#!/usr/bin/env python3
"""Debug script for Phase 3 content extraction."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import sqlite3
import random
import re
from utils.database_manager import DatabaseManager

def debug_url_extraction():
    """Debug the URL extraction process."""
    print("=== Debugging URL Extraction ===")
    
    # Test database connection
    try:
        db = DatabaseManager('talkscraper_state.db')
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Check URLs in database
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM talk_urls WHERE language = "eng"')
        eng_count = cursor.fetchone()[0]
        print(f"📊 English URLs: {eng_count}")
        
        cursor.execute('SELECT COUNT(*) FROM talk_urls WHERE language = "spa"')
        spa_count = cursor.fetchone()[0]
        print(f"📊 Spanish URLs: {spa_count}")
        
        # Get sample URLs
        cursor.execute('SELECT talk_url FROM talk_urls WHERE language = "eng" LIMIT 5')
        sample_urls = [row[0] for row in cursor.fetchall()]
        print(f"📋 Sample URLs:")
        for url in sample_urls:
            print(f"   {url}")
        
        # Test year extraction
        print(f"\n📅 Year extraction test:")
        for url in sample_urls[:3]:
            match = re.search(r'/general-conference/(\d{4})/', url)
            year = match.group(1) if match else None
            print(f"   {url} -> {year}")
    
    db.close()

def test_single_url_extraction():
    """Test extraction from a single URL."""
    print("\n=== Testing Single URL Extraction ===")
    
    # Get one URL
    db = DatabaseManager('talkscraper_state.db')
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT talk_url FROM talk_urls WHERE language = "eng" LIMIT 1')
        result = cursor.fetchone()
        if not result:
            print("❌ No URLs found in database")
            return
        
        test_url = result[0]
    
    db.close()
    
    print(f"🌐 Testing URL: {test_url}")
    
    # Test with our BasicContentExtractor
    import requests
    from bs4 import BeautifulSoup
    
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        response = session.get(test_url, timeout=30)
        print(f"📡 HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Test title extraction
            title_selectors = ['h1', '.title', '[data-testid="title"]']
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text(strip=True)
                    print(f"📝 Title ({selector}): {title[:100]}...")
                    break
            
            # Test content extraction
            content_selectors = ['.body-block', '.study-content', '.content']
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = elements[0].get_text(strip=True)
                    print(f"📄 Content ({selector}): {len(content)} chars - {content[:100]}...")
                    break
            
            # Check page structure
            print(f"\n🔍 Page structure analysis:")
            print(f"   Total paragraphs: {len(soup.find_all('p'))}")
            print(f"   Total divs: {len(soup.find_all('div'))}")
            print(f"   Has .body-block: {bool(soup.select('.body-block'))}")
            print(f"   Has .study-content: {bool(soup.select('.study-content'))}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == '__main__':
    debug_url_extraction()
    test_single_url_extraction()
