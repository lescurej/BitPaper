#!/usr/bin/env python3
import subprocess
import sys
import os
import webbrowser
import re
from datetime import datetime
from pathlib import Path
import base64
import multiprocessing
import concurrent.futures
import json
from test.html_template import generate_html_report
from test.report_generator import generate_camera_matrix_html

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

def ultra_fast_run_tests():
    """Ultra-fast test execution with parallel processing"""
    print("🚀 Running Ultra-Fast BitPaper Tests")
    
    # Use parallel test execution
    num_workers = min(multiprocessing.cpu_count(), 8)
    
    # Define test categories for parallel execution
    test_categories = [
        "basic_encoding",
        "camera_simulation", 
        "edge_cases",
        "integration",
        "performance"
    ]
    
    # Run tests in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_category = {
            executor.submit(run_test_category, category): category 
            for category in test_categories
        }
        
        results = {}
        for future in concurrent.futures.as_completed(future_to_category):
            category = future_to_category[future]
            try:
                category_results = future.result()
                results[category] = category_results
            except Exception as e:
                print(f"❌ {category} tests failed: {e}")
                results[category] = {"passed": 0, "failed": 1, "skipped": 0}
    
    return aggregate_results(results)

def run_test_category(category):
    """Run tests for a specific category"""
    cmd = [
        "python", "-m", "pytest", 
        f"test/test_{category}.py", 
        "-v", "--tb=short",
        "--durations=10"
    ]
    
    env = {"PYTHONPATH": "."}
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            env=env,
            timeout=300  # 5 minute timeout
        )
        
        return parse_test_output(result.stdout, category)
        
    except subprocess.TimeoutExpired:
        return {"passed": 0, "failed": 1, "skipped": 0, "timeout": True}
    except Exception as e:
        return {"passed": 0, "failed": 1, "skipped": 0, "error": str(e)}

def parse_test_output(output, category):
    """Ultra-fast test output parsing using regex"""
    # Use compiled regex for faster parsing
    test_pattern = re.compile(r'(\w+::\w+::\w+)\s+(PASSED|FAILED|SKIPPED)')
    
    results = {"passed": 0, "failed": 0, "skipped": 0}
    test_details = []
    
    # Parse all tests at once
    matches = test_pattern.findall(output)
    
    for test_name, status in matches:
        if status == "PASSED":
            results["passed"] += 1
        elif status == "FAILED":
            results["failed"] += 1
        elif status == "SKIPPED":
            results["skipped"] += 1
        
        test_details.append({
            "name": test_name,
            "status": status.lower(),
            "category": category
        })
    
    results["details"] = test_details
    return results

def aggregate_results(category_results):
    """Aggregate results from all categories"""
    total_results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "categories": category_results
    }
    
    for category, results in category_results.items():
        total_results["total"] += results.get("passed", 0) + results.get("failed", 0) + results.get("skipped", 0)
        total_results["passed"] += results.get("passed", 0)
        total_results["failed"] += results.get("failed", 0)
        total_results["skipped"] += results.get("skipped", 0)
    
    return total_results

def generate_optimized_report(results, timestamp):
    """Generate optimized HTML report"""
    # Generate test rows efficiently
    test_rows = []
    for category, category_results in results["categories"].items():
        for test_detail in category_results.get("details", []):
            test_rows.append(f"""
                <tr>
                    <td>{test_detail['name']}</td>
                    <td><span class="status {test_detail['status']}">{test_detail['status']}</span></td>
                    <td>{test_detail['category']}</td>
                </tr>
            """)
    
    # Generate coverage HTML (simplified)
    coverage_html = f"""
        <div class="coverage-summary">
            <div class="coverage-item">
                <div class="coverage-number">{results['passed']}</div>
                <div class="label">Passed</div>
            </div>
            <div class="coverage-item">
                <div class="coverage-number">{results['failed']}</div>
                <div class="label">Failed</div>
            </div>
            <div class="coverage-item">
                <div class="coverage-number">{results['skipped']}</div>
                <div class="label">Skipped</div>
            </div>
            <div class="coverage-item">
                <div class="coverage-number">{results['total']}</div>
                <div class="label">Total</div>
            </div>
        </div>
    """
    
    # Generate camera matrix HTML
    camera_images_html = generate_camera_matrix_html()
    
    # Generate final HTML report
    html_content = generate_html_report(
        timestamp=timestamp,
        passed=results["passed"],
        failed=results["failed"], 
        skipped=results["skipped"],
        total=results["total"],
        coverage_html=coverage_html,
        test_rows="\n".join(test_rows),
        a4_results_html="",
        detailed_results_html="",
        camera_images_html=camera_images_html
    )
    
    return html_content

def main():
    """Main test runner with ultra-fast execution"""
    import time
    
    start_time = time.time()
    
    # Run tests with parallel execution
    results = ultra_fast_run_tests()
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"\n🚀 Test Execution Summary:")
    print(f"   Total tests: {results['total']}")
    print(f"   Passed: {results['passed']}")
    print(f"   Failed: {results['failed']}")
    print(f"   Skipped: {results['skipped']}")
    print(f"   Execution time: {execution_time:.2f}s")
    
    # Generate optimized report
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    html_content = generate_optimized_report(results, timestamp)
    
    # Save report
    report_path = "test_results.html"
    with open(report_path, "w") as f:
        f.write(html_content)
    
    print(f"   Report saved: {report_path}")
    
    # Open report
    os.system(f"open {report_path}")
    
    return results["failed"] == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)