"""
CLI Commands for TalkScraper operations.

This module provides command line interfaces for specific
TalkScraper operations using the Command pattern.
"""

import argparse
from typing import List, Optional, Dict, Any

from patterns.command_pattern import (
    URLCollectionCommand,
    TalkURLExtractionCommand, 
    ContentExtractionCommand,
    CommandInvoker
)


class CLICommands:
    """
    Command Line Interface for TalkScraper operations.
    
    Provides structured CLI commands for each phase of scraping.
    """
    
    def __init__(self, config_path: str = "config.ini"):
        self.config_path = config_path
        self.invoker = CommandInvoker()
    
    def collect_urls(self, languages: List[str]) -> bool:
        """Execute Phase 1: URL Collection."""
        command = URLCollectionCommand(languages, self.config_path)
        result = self.invoker.execute_command(command)
        
        if result['success']:
            total_urls = sum(len(urls) for urls in result['urls'].values()) if result['urls'] else 0
            print(f"✅ URL collection completed successfully!")
            print(f"📊 Total URLs collected: {total_urls}")
            for lang, urls in result['urls'].items():
                print(f"   {lang.upper()}: {len(urls)} URLs")
            print(f"⏱️  Duration: {result['duration']:.2f} seconds")
            return True
        else:
            print(f"❌ URL collection failed: {result['error']}")
            return False
    
    def extract_talk_urls(self, languages: List[str]) -> bool:
        """Execute Phase 2: Talk URL Extraction."""
        command = TalkURLExtractionCommand(languages, self.config_path)
        result = self.invoker.execute_command(command)
        
        if result['success']:
            print(f"✅ Talk URL extraction completed successfully!")
            print(f"⏱️  Duration: {result['duration']:.2f} seconds")
            return True
        else:
            print(f"❌ Talk URL extraction failed: {result['error']}")
            return False
    
    def extract_content(self, languages: Optional[List[str]] = None, limit: Optional[int] = None,
                        batch_size: int = 12, skip_notes: bool = False) -> bool:
        """Execute Phase 3: Content Extraction."""
        if languages is None:
            languages = ["eng", "spa"]

        command = ContentExtractionCommand(self.config_path, languages, limit, batch_size, skip_notes=skip_notes)
        result = self.invoker.execute_command(command)

        if result['success']:
            if 'message' in result:
                print(f"ℹ️  {result['message']}")
            else:
                langs = ', '.join(result.get('languages', languages))
                print(f"✅ Content extraction completed successfully for: {langs}")
                print(f"📊 Talks processed: {result.get('processed_count', 0)}")
                if result.get('results'):
                    success_count = result['results'].get('success_count', 0)
                    error_count = result['results'].get('error_count', 0)
                    print(f"   ✅ Successful: {success_count}")
                    print(f"   ❌ Errors: {error_count}")
                if result.get('skip_notes', skip_notes):
                    print("   📝 Notes extraction skipped")
            print(f"⏱️  Duration: {result['duration']:.2f} seconds")
            return True
        else:
            print(f"❌ Content extraction failed: {result['error']}")
            return False
    
    def show_statistics(self) -> bool:
        """Show processing statistics from database."""
        try:
            # Import here to avoid circular imports
            from utils.database_manager import DatabaseManager
            from utils.config_manager import ConfigManager
            
            config = ConfigManager(self.config_path)
            db = DatabaseManager(config.get_db_path())
            
            stats = db.get_processing_stats()
            log_summary = db.get_processing_log_summary()

            print("📊 TalkScraper Statistics")
            print("=" * 60)

            print("Conferences")
            print("-" * 60)
            if stats['conferences']:
                for language, data in stats['conferences'].items():
                    print(f" {language.upper():>3} → Total: {data['total']:<4} | Procesadas: {data['processed']:<4} | Pendientes: {data['pending']:<4}")
            else:
                print(" No hay registros de conferencias.")

            print("\nTalk URLs")
            print("-" * 60)
            if stats['talks']:
                for language, data in stats['talks'].items():
                    print(f" {language.upper():>3} → Total: {data['total']:<4} | Procesadas: {data['processed']:<4} | Pendientes: {data['pending']:<4}")
            else:
                print(" No hay registros de discursos.")

            print("\nMetadata respaldada")
            print("-" * 60)
            if stats['metadata']:
                for language, data in stats['metadata'].items():
                    print(f" {language.upper():>3} → {data['total']} discursos en `talk_metadata`")
            else:
                print(" No hay metadatos guardados.")

            print("\nConferencias recientes (talk_metadata)")
            print("-" * 60)
            if stats['recent_conferences']:
                for rc in stats['recent_conferences']:
                    print(f" {rc['conference_session']} [{rc['language'].upper()}] → {rc['talks']} discursos")
            else:
                print(" No hay conferencias recientes registradas.")

            print("\nProcessing log")
            print("-" * 60)
            if log_summary['status_counts']:
                for status, count in log_summary['status_counts'].items():
                    print(f" {status:>8}: {count}")
            else:
                print(" No hay entradas en `processing_log`.")

            if log_summary['recent_failures']:
                print("\nÚltimos fallos")
                for failure in log_summary['recent_failures']:
                    time_str = failure['timestamp'] or '-'
                    lang = failure['language'] or '-'
                    print(f" • {time_str} | {failure['operation']} [{lang}] → {failure['url'] or '-'}")
                    if failure['message']:
                        print(f"   ↳ {failure['message']}")
            else:
                print("\nNo se registran fallos recientes.")
            
            return True
            
        except Exception as e:
            print(f"❌ Error showing statistics: {e}")
            return False
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get command execution history."""
        return self.invoker.get_history()


def create_cli_parser() -> argparse.ArgumentParser:
    """Create the main CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="TalkScraper - Church Conference Talk Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s collect --languages eng spa
  %(prog)s extract-talks --languages eng
  %(prog)s extract-content --limit 100 --batch-size 8
  %(prog)s stats
        """
    )
    
    # Global options
    parser.add_argument(
        "--config",
        type=str,
        default="config.ini",
        help="Configuration file path (default: config.ini)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # URL Collection command
    collect_parser = subparsers.add_parser(
        "collect",
        help="Phase 1: Collect conference URLs"
    )
    collect_parser.add_argument(
        "--languages",
        nargs="+",
        choices=["eng", "spa"],
        default=["eng", "spa"],
        help="Languages to process (default: both)"
    )
    
    # Talk URL Extraction command
    extract_parser = subparsers.add_parser(
        "extract-talks", 
        help="Phase 2: Extract individual talk URLs"
    )
    extract_parser.add_argument(
        "--languages",
        nargs="+", 
        choices=["eng", "spa"],
        default=["eng", "spa"],
        help="Languages to process (default: both)"
    )
    
    # Content Extraction command
    content_parser = subparsers.add_parser(
        "extract-content",
        help="Phase 3: Extract talk content and generate HTML files"
    )
    content_parser.add_argument(
        "--languages",
        nargs="+",
        choices=["eng", "spa"],
        default=["eng", "spa"],
        help="Languages to process (default: both)"
    )
    content_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of talks to process (default: all unprocessed)"
    )
    content_parser.add_argument(
        "--batch-size",
        type=int,
        default=12,
        help="Number of talks to process simultaneously (default: 12)"
    )
    content_parser.add_argument(
        "--skip-notes",
        action="store_true",
        help="Skip Selenium note extraction (static content only)"
    )
    
    # Statistics command
    subparsers.add_parser(
        "stats",
        help="Show processing statistics"
    )
    
    return parser
