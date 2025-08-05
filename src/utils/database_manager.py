"""
Database Manager for TalkScraper

Handles SQLite database operations for storing scraping progress and URLs.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime


class DatabaseManager:
    """Manages SQLite database for storing scraping state and progress."""
    
    def __init__(self, db_path: str):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Conference URLs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conference_urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    language TEXT NOT NULL,
                    url TEXT NOT NULL,
                    discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE,
                    UNIQUE(language, url)
                )
            ''')
            
            # Talk URLs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS talk_urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conference_url TEXT NOT NULL,
                    talk_url TEXT NOT NULL,
                    language TEXT NOT NULL,
                    discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE,
                    UNIQUE(conference_url, talk_url)
                )
            ''')
            
            # Processing log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    language TEXT,
                    url TEXT,
                    status TEXT NOT NULL,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            self.logger.info("Database initialized successfully")
    
    def store_conference_urls(self, language: str, urls: List[str]) -> int:
        """
        Store conference URLs in database.
        
        Args:
            language: Language code (eng/spa)
            urls: List of conference URLs
            
        Returns:
            Number of new URLs stored
        """
        stored_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for url in urls:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO conference_urls 
                        (language, url) VALUES (?, ?)
                    ''', (language, url))
                    
                    if cursor.rowcount > 0:
                        stored_count += 1
                        
                except sqlite3.Error as e:
                    self.logger.error(f"Error storing conference URL {url}: {e}")
            
            conn.commit()
        
        self.logger.info(f"Stored {stored_count} new conference URLs for {language}")
        return stored_count
    
    def get_conference_urls(self, language: str, unprocessed_only: bool = False) -> List[str]:
        """
        Retrieve conference URLs from database.
        
        Args:
            language: Language code (eng/spa)
            unprocessed_only: If True, only return unprocessed URLs
            
        Returns:
            List of conference URLs
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = 'SELECT url FROM conference_urls WHERE language = ?'
            params = [language]
            
            if unprocessed_only:
                query += ' AND processed = FALSE'
            
            cursor.execute(query, params)
            urls = [row[0] for row in cursor.fetchall()]
        
        return urls
    
    def mark_conference_processed(self, url: str):
        """Mark a conference URL as processed."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE conference_urls 
                SET processed = TRUE 
                WHERE url = ?
            ''', (url,))
            conn.commit()
    
    def store_talk_urls(self, conference_url: str, language: str, talk_urls: List[str]) -> int:
        """
        Store talk URLs associated with a conference.
        
        Args:
            conference_url: The conference URL these talks belong to
            language: Language code
            talk_urls: List of talk URLs
            
        Returns:
            Number of new talk URLs stored
        """
        stored_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for talk_url in talk_urls:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO talk_urls 
                        (conference_url, talk_url, language) VALUES (?, ?, ?)
                    ''', (conference_url, talk_url, language))
                    
                    if cursor.rowcount > 0:
                        stored_count += 1
                        
                except sqlite3.Error as e:
                    self.logger.error(f"Error storing talk URL {talk_url}: {e}")
            
            conn.commit()
        
        return stored_count
    
    def get_processing_stats(self) -> dict:
        """Get processing statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Conference stats
            cursor.execute('''
                SELECT language, 
                       COUNT(*) as total, 
                       SUM(CASE WHEN processed = TRUE THEN 1 ELSE 0 END) as processed
                FROM conference_urls 
                GROUP BY language
            ''')
            conference_stats = {row[0]: {'total': row[1], 'processed': row[2]} 
                              for row in cursor.fetchall()}
            
            # Talk stats
            cursor.execute('''
                SELECT language, 
                       COUNT(*) as total, 
                       SUM(CASE WHEN processed = TRUE THEN 1 ELSE 0 END) as processed
                FROM talk_urls 
                GROUP BY language
            ''')
            talk_stats = {row[0]: {'total': row[1], 'processed': row[2]} 
                         for row in cursor.fetchall()}
            
        return {
            'conferences': conference_stats,
            'talks': talk_stats
        }
    
    def log_operation(self, operation: str, status: str, language: str = None, 
                     url: str = None, message: str = None):
        """Log an operation to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO processing_log 
                (operation, language, url, status, message) 
                VALUES (?, ?, ?, ?, ?)
            ''', (operation, language, url, status, message))
            conn.commit()
    
    def close(self):
        """Close database connection (if needed for cleanup)."""
        # SQLite connections are automatically closed when using context manager
        pass
