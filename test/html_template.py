#!/usr/bin/env python3
from datetime import datetime

def get_css():
    return """body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; color: #333; }
.container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }
.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
.header h1 { margin: 0; font-size: 2.5em; font-weight: 300; }
.header .timestamp { opacity: 0.8; font-size: 0.9em; margin-top: 10px; }
.nav { background: #f8f9fa; border-bottom: 1px solid #e9ecef; padding: 0; }
.nav ul { list-style: none; margin: 0; padding: 0; display: flex; }
.nav li { margin: 0; }
.nav a { display: block; padding: 15px 25px; text-decoration: none; color: #495057; border-bottom: 3px solid transparent; transition: all 0.3s ease; }
.nav a:hover, .nav a.active { background: #e9ecef; color: #495057; border-bottom-color: #667eea; }
.content { padding: 30px; }
.section { display: none; animation: fadeIn 0.5s ease-in; }
.section.active { display: block; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
.card { background: white; border-radius: 8px; padding: 20px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid; }
.card.passed { border-left-color: #28a745; }
.card.failed { border-left-color: #dc3545; }
.card.skipped { border-left-color: #ffc107; }
.card.coverage { border-left-color: #17a2b8; }
.card h3 { margin: 0 0 10px 0; font-size: 2em; font-weight: 300; }
.card .label { color: #6c757d; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; }
.test-results { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.test-results table { width: 100%; border-collapse: collapse; }
.test-results th, .test-results td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #e9ecef; }
.test-results th { background: #f8f9fa; font-weight: 600; color: #495057; }
.test-results tr:hover { background: #f8f9fa; }
.status { padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 600; text-transform: uppercase; }
.status.passed { background: #d4edda; color: #155724; }
.status.failed { background: #f8d7da; color: #721c24; }
.status.skipped { background: #fff3cd; color: #856404; }
.coverage-section { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.coverage-bar { background: #e9ecef; border-radius: 4px; height: 20px; overflow: hidden; margin: 10px 0; }
.coverage-fill { height: 100%; background: linear-gradient(90deg, #28a745, #20c997); transition: width 0.3s ease; }
.coverage-fill.low { background: linear-gradient(90deg, #dc3545, #fd7e14); }
.coverage-fill.medium { background: linear-gradient(90deg, #ffc107, #fd7e14); }
.file-coverage { display: grid; grid-template-columns: 1fr auto auto; gap: 15px; align-items: center; padding: 10px 0; border-bottom: 1px solid #e9ecef; }
.file-coverage:last-child { border-bottom: none; }
.file-name { font-weight: 500; }
.coverage-percentage { font-weight: 600; text-align: right; }
.coverage-percentage.high { color: #28a745; }
.coverage-percentage.medium { color: #ffc107; }
.coverage-percentage.low { color: #dc3545; }
.progress { width: 100px; background: #e9ecef; border-radius: 10px; height: 8px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 10px; transition: width 0.3s ease; }
.progress-fill.high { background: #28a745; }
.progress-fill.medium { background: #ffc107; }
.progress-fill.low { background: #dc3545; }
.coverage-summary { margin-bottom: 20px; }
.file-coverage-list { margin-top: 20px; }
.a4-results { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
.a4-results h3 { color: #495057; margin-bottom: 15px; }
.a4-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
.a4-table th, .a4-table td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #e9ecef; }
.a4-table th { background: #f8f9fa; font-weight: 600; color: #495057; }
.a4-table tr:hover { background: #f8f9fa; }
.capacity-high { color: #28a745; font-weight: 600; }
.capacity-medium { color: #ffc107; font-weight: 600; }
.capacity-low { color: #dc3545; font-weight: 600; }
.detailed-results { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
.detailed-results h3 { color: #495057; margin-bottom: 15px; }
.detailed-results pre { background: #f8f9fa; padding: 15px; border-radius: 4px; overflow-x: auto; font-family: 'Courier New', monospace; font-size: 0.9em; }
.camera-images { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
.camera-image-card { background: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
.camera-image-card h4 { margin: 0 0 10px 0; color: #495057; }
.camera-image-card img { max-width: 100%; height: auto; border-radius: 4px; border: 1px solid #e9ecef; }
.camera-image-card .params { font-size: 0.8em; color: #6c757d; margin-top: 10px; }
.camera-image-card .capacity { font-weight: 600; margin-top: 5px; }"""

def generate_html_report(timestamp, passed, failed, skipped, total, coverage_html, test_rows, a4_results_html="", detailed_results_html="", camera_images_html=""):
    css = get_css()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>BitPaper Test Suite Report</title>
    <style>
        {css}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 BitPaper Test Suite</h1>
            <div class="timestamp">{timestamp}</div>
        </div>
        
        <nav class="nav">
            <ul>
                <li><a href="#summary" class="nav-link active" onclick="showSection('summary')">Summary</a></li>
                <li><a href="#a4-capacity" class="nav-link" onclick="showSection('a4-capacity')">A4 Capacity</a></li>
                <li><a href="#camera-images" class="nav-link" onclick="showSection('camera-images')">Camera Images</a></li>
                <li><a href="#tests" class="nav-link" onclick="showSection('tests')">Test Results</a></li>
                <li><a href="#coverage" class="nav-link" onclick="showSection('coverage')">Coverage</a></li>
            </ul>
        </nav>
        
        <div class="content">
            <div id="summary" class="section active">
                <div class="summary-cards">
                    <div class="card passed">
                        <h3>{passed}</h3>
                        <div class="label">Passed</div>
                    </div>
                    <div class="card failed">
                        <h3>{failed}</h3>
                        <div class="label">Failed</div>
                    </div>
                    <div class="card skipped">
                        <h3>{skipped}</h3>
                        <div class="label">Skipped</div>
                    </div>
                    <div class="card coverage">
                        <h3>{total}</h3>
                        <div class="label">Total Tests</div>
                    </div>
                </div>
                
                <div class="coverage-section">
                    <h2> Overall Coverage</h2>
                    {coverage_html}
                </div>
                
                {a4_results_html}
            </div>
            
            <div id="a4-capacity" class="section">
                <div class="a4-results">
                    <h2>📄 A4 Paper Capacity Analysis</h2>
                    {a4_results_html}
                </div>
                
                <div class="detailed-results">
                    <h2>📊 Detailed Test Results</h2>
                    {detailed_results_html}
                </div>
            </div>
            
            <div id="camera-images" class="section">
                <div class="a4-results">
                    <h2>📷 Camera Simulation Images</h2>
                    <p>Below are sample images showing how the A4 paper looks under different camera simulation conditions:</p>
                    {camera_images_html}
                </div>
            </div>
            
            <div id="tests" class="section">
                <div class="test-results">
                    <h2>📋 Detailed Test Results</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Test Name</th>
                                <th>Status</th>
                                <th>Duration</th>
                            </tr>
                        </thead>
                        <tbody>
                            {test_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div id="coverage" class="section">
                <div class="coverage-section">
                    <h2>📈 Code Coverage Details</h2>
                    {coverage_html}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function showSection(sectionId) {{
            document.querySelectorAll('.section').forEach(section => {{
                section.classList.remove('active');
            }});
            
            document.getElementById(sectionId).classList.add('active');
            
            document.querySelectorAll('.nav-link').forEach(link => {{
                link.classList.remove('active');
            }});
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>"""

def get_html_template():
    return generate_html_report 