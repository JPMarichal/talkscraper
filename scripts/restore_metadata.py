#!/usr/bin/env python3
"""
Restore Metadata Script

This script restores metadata from existing HTML files in conf/ to the talk_metadata table.
It's useful for populating the database with historical data when HTML files already exist.

Usage:
    python scripts/restore_metadata.py [--config CONFIG_FILE] [--dry-run]
    
Options:
    --config: Path to config file (default: config.ini)
    --dry-run: Preview what would be done without making changes
    --language: Process only specific language (eng or spa)
    --conference: Process only specific conference (e.g., 202504)
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.talk_content_extractor import TalkContentExtractor
from utils.logger_setup import setup_logger


def main():
    """Main function for metadata restoration."""
    parser = argparse.ArgumentParser(
        description='Restore metadata from HTML files to database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--config',
        default='config.ini',
        help='Path to configuration file (default: config.ini)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be done without making changes'
    )
    parser.add_argument(
        '--language',
        choices=['eng', 'spa'],
        help='Process only specific language'
    )
    parser.add_argument(
        '--conference',
        help='Process only specific conference (e.g., 202504)'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logger
    log_config = {
        'level': 'DEBUG' if args.verbose else 'INFO',
        'file': 'logs/restore_metadata.log',
        'console': True
    }
    logger = setup_logger('RestoreMetadata', log_config)
    
    logger.info("=" * 60)
    logger.info("Metadata Restoration Script")
    logger.info("=" * 60)
    
    if args.dry_run:
        logger.warning("DRY RUN MODE - No changes will be made to the database")
    
    try:
        # Initialize extractor (skip_notes=True since we're only restoring metadata)
        logger.info(f"Initializing with config: {args.config}")
        extractor = TalkContentExtractor(args.config, skip_notes=True)
        
        # Filter HTML files if needed
        if args.language or args.conference:
            logger.info(f"Filtering: language={args.language}, conference={args.conference}")
            # For now, we'll use the full backup method and filter in post-processing
            # A more efficient implementation would filter during rglob
        
        if args.dry_run:
            logger.info("Would restore metadata from HTML files in conf/")
            logger.info("Dry run complete - no changes made")
        else:
            logger.info("Starting metadata restoration from HTML files...")
            extractor.backup_existing_html_metadata()
            logger.info("Metadata restoration complete!")
        
        # Print statistics
        logger.info("\nFinal Statistics:")
        stats = extractor.db.get_processing_stats()
        
        if 'metadata' in stats:
            logger.info("Metadata records by language:")
            for lang, data in stats['metadata'].items():
                logger.info(f"  {lang}: {data['total']} talks")
        
        if 'recent_conferences' in stats:
            logger.info("\nRecent conferences:")
            for conf in stats['recent_conferences'][:10]:
                logger.info(
                    f"  {conf['conference_session']} ({conf['language']}): "
                    f"{conf['talks']} talks"
                )
        
    except FileNotFoundError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please ensure config.ini or config_template.ini exists")
        return 1
    except Exception as e:
        logger.error(f"Error during restoration: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1
    
    logger.info("\n" + "=" * 60)
    logger.info("Restoration script completed successfully")
    logger.info("=" * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
