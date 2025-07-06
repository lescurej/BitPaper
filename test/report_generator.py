#!/usr/bin/env python3
import re
from pathlib import Path
import json

def parse_coverage_data():
    coverage_path = Path("htmlcov/index.html")
    if not coverage_path.exists():
        return None
    
    try:
        with open(coverage_path, 'r') as f:
            content = f.read()
        
        overall_match = re.search(r'<span class="pc_cov">(\d+)%</span>', content)
        overall_coverage = overall_match.group(1) if overall_match else "0"
        
        file_coverage = []
        file_pattern = r'<tr class="region">\s*<td class="name left"><a href="[^"]*">([^<]+)</a></td>\s*<td>(\d+)</td>\s*<td>(\d+)</td>\s*<td>(\d+)</td>\s*<td class="right" data-ratio="(\d+) (\d+)">(\d+)%</td>\s*</tr>'
        
        matches = re.findall(file_pattern, content)
        for match in matches:
            filename, statements, missing, excluded, covered, total, percentage = match
            file_coverage.append({
                'file': filename,
                'statements': int(statements),
                'missing': int(missing),
                'covered': int(covered),
                'total': int(total),
                'percentage': int(percentage)
            })
        
        return {
            'overall': overall_coverage,
            'files': file_coverage
        }
    except Exception as e:
        print(f"Error parsing coverage data: {e}")
        return None

def generate_coverage_html(coverage_data):
    if not coverage_data or not coverage_data.get('files'):
        return "<p>Coverage data not available</p>"
    
    html = f"""
    <div class="coverage-summary">
        <h3>Overall Coverage: {coverage_data['overall']}%</h3>
        <div class="coverage-bar">
            <div class="coverage-fill {'high' if int(coverage_data['overall']) >= 80 else 'medium' if int(coverage_data['overall']) >= 60 else 'low'}" 
                 style="width: {coverage_data['overall']}%"></div>
        </div>
    </div>
    <div class="file-coverage-list">
        <h4>File Coverage</h4>
    """
    
    for file_data in coverage_data['files']:
        percentage = file_data['percentage']
        status_class = 'high' if percentage >= 80 else 'medium' if percentage >= 60 else 'low'
        html += f"""
        <div class="file-coverage">
            <div class="file-name">{file_data['file']}</div>
            <div class="coverage-percentage {status_class}">{percentage}%</div>
            <div class="progress">
                <div class="progress-fill {status_class}" style="width: {percentage}%"></div>
            </div>
        </div>
        """
    
    html += "</div>"
    return html 

def generate_camera_matrix_html(results_path="test/a4_camera_matrix_results.json"):
    try:
        with open(results_path, "r") as f:
            data = json.load(f)
    except Exception:
        return "<p>No camera matrix results found.</p>"

    camera_conditions = list(data.keys())
    file_sizes = sorted(list(data[camera_conditions[0]].keys()), key=lambda x: int(x.replace("KB", "")))

    html = '<table class="a4-table">'
    html += '<thead><tr><th>File Size</th>'
    for cond in camera_conditions:
        html += f'<th>{cond}</th>'
    html += '</tr></thead><tbody>'

    for size in file_sizes:
        html += f'<tr><td>{size}</td>'
        for cond in camera_conditions:
            entry = data[cond][size]
            status = "passed" if entry["pass"] else "failed"
            img_html = f'<img src="data:image/png;base64,{entry["image_b64"]}" style="width:124px;height:176px;object-fit:contain;aspect-ratio:124/176;" />' if entry["image_b64"] else ""
            html += f'<td><div class="camera-image-card {status}">{img_html}<div class="status {status}">{status.upper()}</div></div></td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html 