#!/usr/bin/env python3
"""
Test runner script for TalkScraper.

This script provides easy commands to run different types of tests
and generates comprehensive reports.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and print its status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=False)
    
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        return False
    else:
        print(f"✅ Passed: {description}")
        return True


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="TalkScraper Test Runner")
    parser.add_argument("--type", choices=["unit", "integration", "all", "coverage", "fast"],
                       default="all", help="Type of tests to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--parallel", "-p", action="store_true", help="Run tests in parallel")
    parser.add_argument("--html-report", action="store_true", help="Generate HTML coverage report")
    
    args = parser.parse_args()
    
    # Change to project root directory
    os.chdir(Path(__file__).parent)
    
    # Base pytest command
    pytest_cmd = "python -m pytest"
    
    if args.verbose:
        pytest_cmd += " -v"
    
    if args.parallel:
        pytest_cmd += " -n auto"
    
    success = True
    
    if args.type == "unit":
        cmd = f"{pytest_cmd} tests/unit/ -m unit"
        success &= run_command(cmd, "Unit Tests")
        
    elif args.type == "integration":
        cmd = f"{pytest_cmd} tests/integration/ -m integration"
        success &= run_command(cmd, "Integration Tests")
        
    elif args.type == "fast":
        cmd = f'{pytest_cmd} tests/ -m "not slow and not selenium"'
        success &= run_command(cmd, "Fast Tests (excluding slow and selenium)")
        
    elif args.type == "coverage":
        cmd = f"{pytest_cmd} tests/ --cov=src --cov-report=term-missing"
        if args.html_report:
            cmd += " --cov-report=html:htmlcov"
        success &= run_command(cmd, "Tests with Coverage")
        
        if args.html_report:
            print(f"\n📊 HTML coverage report generated at: htmlcov/index.html")
        
    elif args.type == "all":
        # Run unit tests
        cmd = f"{pytest_cmd} tests/unit/ -m unit"
        success &= run_command(cmd, "Unit Tests")
        
        # Run integration tests
        cmd = f"{pytest_cmd} tests/integration/ -m integration"
        success &= run_command(cmd, "Integration Tests")
        
        # Generate coverage report
        cmd = f"{pytest_cmd} tests/ --cov=src --cov-report=term-missing"
        success &= run_command(cmd, "Coverage Report")
    
    # Print summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 All tests passed!")
        print("✅ Ready to proceed with Phase 3 implementation")
    else:
        print("❌ Some tests failed!")
        print("🔧 Please fix failing tests before proceeding")
    print(f"{'='*60}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
