#!/usr/bin/env python3
import sys
import os
import subprocess
from pathlib import Path

def main():
    print("🧪 Running BitPaper Test Suite (Fixed)")
    print("=" * 50)
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Add current directory to Python path
    sys.path.insert(0, str(project_root))
    
    try:
        import bitpaper
        print("✅ BitPaper module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import BitPaper module: {e}")
        return False
    
    # Run pytest directly
    cmd = [
        sys.executable, "-m", "pytest", 
        "test/", 
        "-v", 
        "--tb=short",
        "--durations=10",
        "--cov=bitpaper",
        "--cov-report=html",
        "--cov-report=term-missing"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("\n📊 Test Results")
        print("=" * 50)
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️  Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1) 