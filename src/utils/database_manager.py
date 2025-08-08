"""
Database Manager for TalkScraper

Handles SQLite database operations for storing scraping progress and URLs.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Optional, Dict, Union
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
                    title TEXT,
                    author TEXT,
                    calling TEXT,
                    conference TEXT,
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
            
            # Talk metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS talk_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    calling TEXT,
                    note_count INTEGER,
                    language TEXT,
                    year TEXT,
                    conference_session TEXT,
                    backup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(url)
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
    
    def store_talk_metadata(self, url: str, title: str, author: str, calling: str, note_count: int, language: str, year: str, conference_session: str):
        """
        Store talk metadata (without content/notes) in the database.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO talk_metadata 
                    (url, title, author, calling, note_count, language, year, conference_session)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (url, title, author, calling, note_count, language, year, conference_session))
                conn.commit()
                self.logger.info(f"Talk metadata stored for {title} [{url}]")
            except sqlite3.Error as e:
                self.logger.error(f"Error storing talk metadata for {url}: {e}")
    
    def get_processing_stats(self) -> Dict[str, Dict[str, Dict[str, int]]]:
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
    
    def log_operation(self, operation: str, status: str, language: Optional[str] = None,
                     url: Optional[str] = None, message: Optional[str] = None):
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
    
    def get_unprocessed_conference_urls(self, language: str) -> List[str]:
        """
        Get list of conference URLs that haven't been processed for talk extraction.
        
        Args:
            language: Language code (eng/spa)
            
        Returns:
            List of unprocessed conference URLs
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT url FROM conference_urls 
                WHERE language = ? AND processed = FALSE
                ORDER BY url
            ''', (language,))
            
            return [row[0] for row in cursor.fetchall()]
    
    def mark_conference_processed(self, conference_url: str):
        """
        Mark a conference URL as processed.
        
        Args:
            conference_url: Conference URL to mark as processed
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE conference_urls 
                SET processed = TRUE 
                WHERE url = ?
            ''', (conference_url,))
            conn.commit()
    
    def get_talk_extraction_stats(self) -> Dict[str, Dict[str, Dict[str, int]]]:
        """
        Get statistics about talk URL extraction progress.
        
        Returns:
            Dictionary with extraction statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Conference processing stats
            cursor.execute('''
                SELECT language, 
                       COUNT(*) as total_conferences, 
                       SUM(CASE WHEN processed = TRUE THEN 1 ELSE 0 END) as processed_conferences
                FROM conference_urls 
                GROUP BY language
            ''')
            
            for row in cursor.fetchall():
                language, total_conf, processed_conf = row
                if language not in stats:
                    stats[language] = {}
                stats[language]['conferences'] = {
                    'total': total_conf,
                    'processed': processed_conf,
                    'pending': total_conf - processed_conf
                }
            
            # Talk URL stats
            cursor.execute('''
                SELECT language, 
                       COUNT(*) as total_talks,
                       SUM(CASE WHEN processed = TRUE THEN 1 ELSE 0 END) as processed_talks
                FROM talk_urls 
                GROUP BY language
            ''')
            
            for row in cursor.fetchall():
                language, total_talks, processed_talks = row
                if language not in stats:
                    stats[language] = {}
                stats[language]['talks'] = {
                    'total': total_talks,
                    'processed': processed_talks,
                    'pending': total_talks - processed_talks
                }
            
            return stats

    def get_unprocessed_talk_urls(self, language: str, limit: Optional[int] = None) -> List[str]:
        """
        Get list of unprocessed talk URLs for a specific language.
        
        Args:
            language: Language code (eng/spa)
            limit: Maximum number of URLs to return (None for all)
            
        Returns:
            List of unprocessed talk URLs (ordered by most recent first)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT talk_url FROM talk_urls 
                WHERE language = ? AND processed = FALSE
                ORDER BY talk_url DESC
            '''
            
            params: List[Union[str, int]] = [language]
            
            if limit is not None:
                query += ' LIMIT ?'
                params.append(limit)
            
            cursor.execute(query, params)
            return [row[0] for row in cursor.fetchall()]

    def update_talk_metadata(self, talk_url: str, title: str = None, author: str = None, calling: str = None, conference: str = None):
        """
        Update metadata fields for a talk URL.
        
        Args:
            talk_url: Talk URL to update
            title: Talk title
            author: Talk author
            calling: Author's calling/position
            conference: Conference session (e.g., "2024-04")
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build dynamic UPDATE query based on provided parameters
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = ?")
                params.append(title)
            if author is not None:
                updates.append("author = ?")
                params.append(author)
            if calling is not None:
                updates.append("calling = ?")
                params.append(calling)
            if conference is not None:
                updates.append("conference = ?")
                params.append(conference)
            
            if updates:
                params.append(talk_url)
                query = f"UPDATE talk_urls SET {', '.join(updates)} WHERE talk_url = ?"
                cursor.execute(query, params)
                conn.commit()

    def mark_talk_processed(self, talk_url: str, success: bool = True):
        """
        Mark a talk URL as processed.
        
        Args:
            talk_url: Talk URL to mark as processed
            success: Whether the processing was successful
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE talk_urls 
                SET processed = TRUE 
                WHERE talk_url = ?
            ''', (talk_url,))
            
            # Log the processing result
            status = 'success' if success else 'failed'
            cursor.execute('''
                INSERT INTO processing_log (operation, url, status, message) 
                VALUES (?, ?, ?, ?)
            ''', ('talk_content_extraction', talk_url, status, 
                  'Talk content extraction completed' if success else 'Talk content extraction failed'))
            
            conn.commit()
