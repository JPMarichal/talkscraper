#!/usr/bin/env python3
"""
TalkScraper Main Script

Phase 1: URL Collection
Collects all conference URLs from the Church website.

Usage:
    python main.py --phase 1 --languages eng spa
    python main.py --phase 1 --languages eng --config custom_config.ini
"""

import argparse
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scrapers.url_collector import URLCollector
from utils.logger_setup import setup_logger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="TalkScraper - Church Conference Talk Scraper"
    )
    
    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 2, 3],
        default=1,
        help="Scraping phase: 1=URL Collection, 2=Talk URLs, 3=Content Extraction"
    )
    
    parser.add_argument(
        "--languages",
        nargs="+",
        choices=["eng", "spa"],
        default=["eng", "spa"],
        help="Languages to process (default: both)"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.ini",
        help="Configuration file path (default: config.ini)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show processing statistics"
    )
    
    return parser.parse_args()


def phase_1_url_collection(languages, config_path):
    """Execute Phase 1: URL Collection."""
    print("=== PHASE 1: URL COLLECTION ===")
    print(f"Languages: {', '.join(languages)}")
    print(f"Config: {config_path}")
    print()
    
    try:
        collector = URLCollector(config_path)
        
        # Collect URLs for all specified languages
        all_urls = collector.collect_all_urls(languages)
        
        # Display results
        total_urls = 0
        for lang, urls in all_urls.items():
            print(f"✅ {lang.upper()}: {len(urls)} conference URLs collected")
            total_urls += len(urls)
        
        print(f"\n🎯 Total URLs collected: {total_urls}")
        
        # Show statistics
        stats = collector.db.get_processing_stats()
        if stats['conferences']:
            print("\n📊 Database Statistics:")
            for lang, data in stats['conferences'].items():
                print(f"   {lang.upper()}: {data['total']} total, {data['processed']} processed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in Phase 1: {e}")
        return False


def show_statistics(config_path):
    """Show current processing statistics."""
    try:
        collector = URLCollector(config_path)
        stats = collector.db.get_processing_stats()
        
        print("=== PROCESSING STATISTICS ===")
        
        if stats['conferences']:
            print("\n📋 Conference URLs:")
            for lang, data in stats['conferences'].items():
                processed_pct = (data['processed'] / data['total'] * 100) if data['total'] > 0 else 0
                print(f"   {lang.upper()}: {data['total']} total, {data['processed']} processed ({processed_pct:.1f}%)")
        
        if stats['talks']:
            print("\n🎤 Talk URLs:")
            for lang, data in stats['talks'].items():
                processed_pct = (data['processed'] / data['total'] * 100) if data['total'] > 0 else 0
                print(f"   {lang.upper()}: {data['total']} total, {data['processed']} processed ({processed_pct:.1f}%)")
        
        if not stats['conferences'] and not stats['talks']:
            print("No data found. Run Phase 1 first to collect URLs.")
        
    except Exception as e:
        print(f"❌ Error showing statistics: {e}")


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Check if config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        print("💡 Copy config_template.ini to config.ini and adjust settings")
        return 1
    
    # Show statistics if requested
    if args.stats:
        show_statistics(str(config_path))
        return 0
    
    # Execute requested phase
    success = False
    
    if args.phase == 1:
        success = phase_1_url_collection(args.languages, str(config_path))
    elif args.phase == 2:
        print("⚠️  Phase 2 (Talk URL Collection) not implemented yet")
        print("Current implementation focuses on Phase 1 only")
    elif args.phase == 3:
        print("⚠️  Phase 3 (Content Extraction) not implemented yet")
        print("Current implementation focuses on Phase 1 only")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
