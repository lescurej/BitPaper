#!/usr/bin/env python3
import subprocess
import sys
import os
import webbrowser
import re
from datetime import datetime
from pathlib import Path
import base64

from .report_generator import parse_coverage_data, generate_coverage_html, generate_camera_matrix_html
from .html_template import get_html_template

def run_tests():
    print("🧪 Running BitPaper Test Suite")
    print("=" * 50)
    
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd() + os.pathsep + env.get('PYTHONPATH', '')
    
    try:
        import bitpaper
        print("✅ BitPaper module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import BitPaper module: {e}")
        return False
    
    try:
        import pytest_cov
        coverage_args = ["--cov=bitpaper", "--cov-report=html", "--cov-report=term-missing"]
        print("✅ pytest-cov plugin available")
    except ImportError:
        print("⚠️  pytest-cov not available, running tests without coverage")
        coverage_args = []
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "test/", 
        "-v", 
        "--tb=short",
        "--durations=10",
        "--ignore=test/archive/"
    ] + coverage_args
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        lines = result.stdout.split('\n')
        test_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }
        
        test_rows = []
        a4_results_html = ""
        detailed_results_html = ""
        
        # Parse test results
        for line in lines:
            if "::" in line and ("PASSED" in line or "FAILED" in line or "SKIPPED" in line):
                test_results["total"] += 1
                if "PASSED" in line:
                    test_results["passed"] += 1
                    status = "passed"
                elif "FAILED" in line:
                    test_results["failed"] += 1
                    status = "failed"
                elif "SKIPPED" in line:
                    test_results["skipped"] += 1
                    status = "skipped"
                
                parts = line.split('::')
                if len(parts) >= 3:
                    class_name = parts[1]
                    method_name = parts[2].split(' ')[0]
                    test_name = f"{class_name}.{method_name}"
                elif len(parts) >= 2:
                    test_name = parts[1].split(' ')[0]
                else:
                    test_name = "Unknown Test"
                    
                test_rows.append(f"""
                    <tr>
                        <td>{test_name}</td>
                        <td><span class="status {status}">{status}</span></td>
                        <td>-</td>
                    </tr>
                """)
        
        # Parse A4 capacity results from output
        a4_capacity_data = parse_a4_capacity_results(lines)
        if a4_capacity_data:
            a4_results_html = generate_a4_capacity_html(a4_capacity_data)
        else:
            a4_results_html = ""
        camera_images_html = generate_camera_matrix_html()
        
        # Parse detailed results
        detailed_results = parse_detailed_results(lines)
        if detailed_results:
            detailed_results_html = generate_detailed_results_html(detailed_results)
        
        print("\n📊 Test Results Summary")
        print("=" * 50)
        print(f"Total Tests: {test_results['total']}")
        print(f"✅ Passed: {test_results['passed']}")
        print(f"❌ Failed: {test_results['failed']}")
        print(f"⏭️  Skipped: {test_results['skipped']}")
        
        if test_results['failed'] == 0:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {test_results['failed']} tests failed")
        
        coverage_data = parse_coverage_data()
        coverage_html = generate_coverage_html(coverage_data)
        
        generate_html = get_html_template()
        html_content = generate_html(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            passed=test_results['passed'],
            failed=test_results['failed'],
            skipped=test_results['skipped'],
            total=test_results['total'],
            coverage_html=coverage_html,
            test_rows=''.join(test_rows),
            a4_results_html=a4_results_html,
            detailed_results_html=detailed_results_html,
            camera_images_html=camera_images_html
        )
        
        combined_report_path = "test_report.html"
        with open(combined_report_path, 'w') as f:
            f.write(html_content)
        
        print(f"🌐 Combined report generated: {combined_report_path}")
        
        try:
            webbrowser.open(f"file://{Path(combined_report_path).absolute()}")
            print(f"🌐 Opened combined report in browser")
        except Exception as e:
            print(f"⚠️  Could not open report in browser: {e}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def parse_a4_capacity_results(lines):
    """Parse A4 capacity results from test output"""
    a4_data = {}
    current_section = None
    
    for line in lines:
        if "A4 PAPER CAPACITY REPORT" in line:
            current_section = "a4_capacity"
            continue
        elif "ENCODING DENSITY ANALYSIS" in line:
            current_section = "density"
            continue
        elif "CAMERA EFFECT BREAKDOWN" in line:
            current_section = "effects"
            continue
        
        if current_section == "a4_capacity" and "KB" in line:
            # Parse lines like "Perfect         500         KB 0.0        % Last successful: 500KB"
            parts = line.split()
            if len(parts) >= 2:
                condition = parts[0].strip()
                try:
                    capacity = int(parts[1])
                    a4_data[condition] = capacity
                except (ValueError, IndexError):
                    pass
    
    return a4_data

def generate_a4_capacity_html(a4_data):
    """Generate HTML for A4 capacity results"""
    if not a4_data:
        return "<p>No A4 capacity data available</p>"
    
    html = """
    <div class="a4-results">
        <h3>📄 A4 Paper Capacity by Camera Conditions</h3>
        <table class="a4-table">
            <thead>
                <tr>
                    <th>Camera Condition</th>
                    <th>Max Capacity</th>
                    <th>Performance</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for condition, capacity in a4_data.items():
        if capacity >= 20000:
            performance_class = "capacity-high"
            performance_text = "Excellent"
        elif capacity >= 10000:
            performance_class = "capacity-medium"
            performance_text = "Good"
        else:
            performance_class = "capacity-low"
            performance_text = "Limited"
        
        html += f"""
            <tr>
                <td>{condition}</td>
                <td class="{performance_class}">{capacity}KB</td>
                <td>{performance_text}</td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html

def parse_detailed_results(lines):
    """Parse detailed test results from output"""
    detailed_results = []
    in_detailed_section = False
    
    for line in lines:
        if "📋" in line or "📊" in line or "🔍" in line:
            in_detailed_section = True
            detailed_results.append(line)
        elif in_detailed_section and line.strip():
            detailed_results.append(line)
        elif in_detailed_section and not line.strip():
            in_detailed_section = False
    
    return detailed_results

def generate_detailed_results_html(detailed_results):
    """Generate HTML for detailed results"""
    if not detailed_results:
        return "<p>No detailed results available</p>"
    
    html = """
    <div class="detailed-results">
        <h3>📊 Detailed Test Output</h3>
        <pre>
    """
    
    for line in detailed_results:
        html += line + "\n"
    
    html += """
        </pre>
    </div>
    """
    
    return html