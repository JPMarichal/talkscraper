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
from scrapers.talk_url_extractor import TalkURLExtractor
from scrapers.talk_content_extractor import TalkContentExtractor
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


def phase_2_talk_extraction(languages, config_path):
    """Execute Phase 2: Talk URL Extraction."""
    print("=== PHASE 2: TALK URL EXTRACTION ===")
    print(f"Languages: {', '.join(languages)}")
    print(f"Config: {config_path}")
    print()
    
    try:
        extractor = TalkURLExtractor(config_path)
        
        # Extract talk URLs for all specified languages
        results = extractor.extract_all_talk_urls(languages)
        
        # Display results
        total_talks = 0
        for lang, count in results.items():
            print(f"✅ {lang.upper()}: {count} talk URLs extracted")
            total_talks += count
        
        print(f"\n🎯 Total talk URLs extracted: {total_talks}")
        
        # Show updated statistics
        stats = extractor.get_extraction_stats()
        if stats:
            print("\n📊 Extraction Statistics:")
            for lang, data in stats.items():
                if 'conferences' in data:
                    conf = data['conferences']
                    print(f"   {lang.upper()} Conferences: {conf['processed']}/{conf['total']} processed")
                if 'talks' in data:
                    talks = data['talks']
                    print(f"   {lang.upper()} Talks: {talks['total']} extracted")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in Phase 2: {e}")
        return False


def phase_3_content_extraction(languages, config_path):
    """Execute Phase 3: Complete Content Extraction."""
    print("=== PHASE 3: COMPLETE CONTENT EXTRACTION ===")
    print(f"Languages: {', '.join(languages)}")
    print(f"Config: {config_path}")
    print()
    
    try:
        extractor = TalkContentExtractor(config_path)
        
        # Extract content for all specified languages
        results = {}
        total_extracted = 0
        
        for language in languages:
            print(f"\n🔍 Processing {language.upper()} talks...")
            
            # Get unprocessed talk URLs (limit to 10 for testing)
            talk_urls = extractor.get_unprocessed_talk_urls(language, limit=10)
            
            if not talk_urls:
                print(f"   No unprocessed URLs found for {language}")
                results[language] = 0
                continue
            
            print(f"   Found {len(talk_urls)} unprocessed talks")
            
            # Extract talks in batch
            stats = extractor.extract_talks_batch(talk_urls)
            results[language] = stats['saved']
            total_extracted += stats['saved']
            
            print(f"   ✅ {language.upper()}: {stats['saved']}/{stats['total']} talks saved to files")
        
        print(f"\n🎯 Total talks extracted and saved: {total_extracted}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in Phase 3: {e}")
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
        success = phase_2_talk_extraction(args.languages, str(config_path))
    elif args.phase == 3:
        success = phase_3_content_extraction(args.languages, str(config_path))
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
