#!/usr/bin/env python
"""
Test Runner for BROski Bot 3.0

This script provides a convenient way to run tests and generate coverage reports.
It supports running specific test categories or individual test files.
"""
import argparse
import subprocess
import sys
import os
from typing import List, Optional


def run_tests(test_paths: List[str], options: List[str]) -> int:
    """
    Run tests with pytest and the given options.
    
    Args:
        test_paths: Paths to test files or directories
        options: Additional pytest options
        
    Returns:
        Return code from pytest
    """
    # Build command
    cmd = ["pytest"] + options + test_paths
    
    print(f"Running: {' '.join(cmd)}")
    return subprocess.call(cmd)


def main():
    """Main function for the test runner."""
    parser = argparse.ArgumentParser(description="BROski Bot Test Runner")
    
    parser.add_argument(
        "--unit", action="store_true",
        help="Run unit tests only"
    )
    
    parser.add_argument(
        "--integration", action="store_true",
        help="Run integration tests only"
    )
    
    parser.add_argument(
        "--performance", action="store_true",
        help="Run performance tests"
    )
    
    parser.add_argument(
        "--coverage", action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--html", action="store_true",
        help="Generate HTML report"
    )
    
    parser.add_argument(
        "test_paths", nargs="*", default=["tests"],
        help="Paths to specific test files or directories"
    )
    
    args = parser.parse_args()
    
    # Set up options
    options = []
    
    # Test selection
    if args.unit:
        options.append("-m")
        options.append("unit")
    
    if args.integration:
        options.append("-m")
        options.append("integration")
    
    if args.performance:
        options.append("-m")
        options.append("performance")
    
    # Coverage reporting
    if args.coverage:
        options.append("--cov=.")
        options.append("--cov-report=term")
        
        if args.html:
            options.append("--cov-report=html:coverage")
    
    # Verbosity
    if args.verbose:
        options.append("-v")
    
    # HTML report
    if args.html and not args.coverage:
        options.append("--html=reports/pytest_report.html")
    
    # Run the tests
    return run_tests(args.test_paths, options)


if __name__ == "__main__":
    sys.exit(main())
