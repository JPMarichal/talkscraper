#!/usr/bin/env python3
"""
Setup script for TalkScraper testing environment.

This script configures the testing environment and verifies
that all testing dependencies are properly installed.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and check its result."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} - OK")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False


def install_test_dependencies():
    """Install testing dependencies."""
    test_deps = [
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0", 
        "pytest-mock>=3.12.0",
        "pytest-asyncio>=0.21.0",
        "pytest-html>=4.1.0",
        "responses>=0.24.0",
        "freezegun>=1.2.0"
    ]
    
    print("📦 Installing testing dependencies...")
    for dep in test_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    
    return True


def verify_test_setup():
    """Verify that testing setup is working."""
    print("🧪 Verifying test setup...")
    
    # Check if pytest can discover tests
    if not run_command("python -m pytest --collect-only -q", "Test discovery"):
        return False
    
    # Run a simple test to verify everything works
    if not run_command("python -m pytest tests/unit/test_phase3_planning.py::TestContentExtractionPlanning::test_talk_url_structure_parsing -v", 
                      "Running sample test"):
        return False
    
    return True


def create_test_config():
    """Create test configuration files if they don't exist."""
    print("⚙️ Setting up test configuration...")
    
    config_files = [
        "pytest.ini",
        "pyproject.toml",
        "tests/conftest.py"
    ]
    
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✅ {config_file} - EXISTS")
        else:
            print(f"❌ {config_file} - MISSING")
            return False
    
    return True


def main():
    """Main setup function."""
    print("🚀 TalkScraper Testing Environment Setup")
    print("=" * 50)
    
    success = True
    
    # Check Python version
    success &= check_python_version()
    
    # Check configuration files
    success &= create_test_config()
    
    # Install dependencies
    success &= install_test_dependencies()
    
    # Verify setup
    success &= verify_test_setup()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Testing environment setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Run all tests: python run_tests.py --type all")
        print("2. Run fast tests: python run_tests.py --type fast")
        print("3. Generate coverage: python run_tests.py --type coverage --html-report")
        print("4. See tests/README.md for detailed documentation")
        print("\n✅ Ready for Phase 3 development with TDD!")
    else:
        print("❌ Testing environment setup failed!")
        print("Please fix the errors above and try again.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
