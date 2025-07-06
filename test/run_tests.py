#!/usr/bin/env python3
import sys
import os

# Add the test directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from test_runner import run_tests
except ImportError:
    # Fallback if running from different directory
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from test.test_runner import run_tests

from report_generator import parse_coverage_data, generate_coverage_html, generate_camera_matrix_html
from html_template import get_html_template

def main():
    return 0 if run_tests() else 1

if __name__ == "__main__":
    sys.exit(main()) 