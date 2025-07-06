#!/usr/bin/env python3
import sys
import os
import subprocess
import webbrowser
from pathlib import Path

def main():
    print("🧪 Running BitPaper Test Suite (Clean)")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    sys.path.insert(0, str(project_root))
    
    try:
        import bitpaper
        print("✅ BitPaper module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import BitPaper module: {e}")
        return False
    
    # Use the proper test runner instead of direct pytest
    try:
        from test.test_runner import run_tests
        success = run_tests()
        
        # Open the generated report
        test_report = project_root / "test_report.html"
        if test_report.exists():
            try:
                webbrowser.open(f"file://{test_report.absolute()}")
                print(f"✅ Opened test report: {test_report}")
            except Exception as e:
                print(f"⚠️  Could not open test report: {e}")
        
        # Also open coverage report if it exists
        coverage_report = project_root / "htmlcov" / "index.html"
        if coverage_report.exists():
            try:
                webbrowser.open(f"file://{coverage_report.absolute()}")
                print(f"✅ Opened coverage report: {coverage_report}")
            except Exception as e:
                print(f"⚠️  Could not open coverage report: {e}")
        
        print("\n📋 Reports Generated:")
        if test_report.exists():
            print(f"   📈 Test Results: {test_report}")
        if coverage_report.exists():
            print(f"   📊 Coverage: {coverage_report}")
        
        return success
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1) 