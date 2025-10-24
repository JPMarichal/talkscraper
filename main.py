#!/usr/bin/env python3
"""
TalkScraper - Unified CLI Application

Modernized entry point using Command Pattern and Factory Pattern.
Provides a clean, extensible CLI interface for all scraping operations.

Usage:
    python main.py collect --languages eng spa
    python main.py extract-talks --languages eng  
    python main.py extract-content --limit 100 --batch-size 8
    python main.py stats
"""

import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from commands.cli_commands import CLICommands, create_cli_parser


def main():
    """Main entry point with modernized CLI."""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # Check if config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        print("💡 Copy config_template.ini to config.ini and adjust settings")
        return 1
    
    # Create CLI command handler
    cli = CLICommands(str(config_path))
    
    # Route to appropriate command
    success = False
    
    if args.command == "collect":
        success = cli.collect_urls(args.languages)
    
    elif args.command == "extract-talks":
        success = cli.extract_talk_urls(args.languages)
    
    elif args.command == "extract-content":
        success = cli.extract_content(args.languages, args.limit, args.batch_size)
    
    elif args.command == "stats":
        success = cli.show_statistics()
    
    else:
        parser.print_help()
        return 1
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
