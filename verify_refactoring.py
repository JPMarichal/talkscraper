#!/usr/bin/env python3
"""
Test Status Verification Script

Quick script to verify test status after refactoring.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all critical imports work."""
    try:
        # Test core imports
        from core.url_collector import URLCollector
        from core.talk_url_extractor import TalkURLExtractor  
        from core.talk_content_extractor import TalkContentExtractor
        print("✅ Core imports: OK")
        
        # Test utils imports
        from utils.config_manager import ConfigManager
        from utils.database_manager import DatabaseManager
        print("✅ Utils imports: OK")
        
        # Test patterns imports
        from patterns.scraper_factory import ScraperFactory
        from patterns.command_pattern import CommandInvoker
        print("✅ Patterns imports: OK")
        
        # Test commands imports
        from commands.cli_commands import CLICommands
        print("✅ Commands imports: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_factory():
    """Test that factory pattern works."""
    try:
        from patterns.scraper_factory import ScraperFactory
        
        # Test factory creation
        collector = ScraperFactory.create_url_collector("config.ini")
        extractor = ScraperFactory.create_talk_url_extractor("config.ini")
        content_extractor = ScraperFactory.create_talk_content_extractor("config.ini")
        
        print("✅ Factory pattern: OK")
        return True
        
    except Exception as e:
        print(f"❌ Factory error: {e}")
        return False

def main():
    """Run verification tests."""
    print("🔍 Testing refactored architecture...")
    print("=" * 50)
    
    success = True
    success &= test_imports()
    success &= test_factory()
    
    print("=" * 50)
    if success:
        print("🎉 All architecture tests passed!")
        print("✅ Ready to run full test suite")
    else:
        print("❌ Architecture issues detected")
        print("🔧 Fix errors before running tests")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
