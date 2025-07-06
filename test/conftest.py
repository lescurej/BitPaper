import pytest
import tempfile
import os
from pathlib import Path
import json

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def sample_text_file(temp_dir):
    content = "Hello, this is a test file for BitPaper encoding and decoding!"
    file_path = temp_dir / "sample.txt"
    with open(file_path, 'w') as f:
        f.write(content)
    return file_path

@pytest.fixture
def sample_binary_file(temp_dir):
    content = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])  # PNG header
    file_path = temp_dir / "sample.bin"
    with open(file_path, 'wb') as f:
        f.write(content)
    return file_path

@pytest.fixture
def large_text_file(temp_dir):
    content = "This is a larger test file. " * 1000
    file_path = temp_dir / "large.txt"
    with open(file_path, 'w') as f:
        f.write(content)
    return file_path

@pytest.fixture
def json_data_file(temp_dir):
    data = {
        "name": "Test User",
        "age": 30,
        "skills": ["Python", "JavaScript", "React"],
        "projects": [
            {"name": "BitPaper", "status": "active"},
            {"name": "Other Project", "status": "completed"}
        ]
    }
    file_path = temp_dir / "data.json"
    with open(file_path, 'w') as f:
        json.dump(data, f)
    return file_path

@pytest.fixture
def unicode_file(temp_dir):
    content = "Hello 世界! 🌍 Test with emojis 🚀"
    file_path = temp_dir / "unicode.txt"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return file_path

@pytest.fixture
def empty_file(temp_dir):
    file_path = temp_dir / "empty.txt"
    file_path.touch()
    return file_path

@pytest.fixture
def single_byte_file(temp_dir):
    file_path = temp_dir / "single.txt"
    with open(file_path, 'wb') as f:
        f.write(b'A')
    return file_path

@pytest.fixture
def test_results():
    return {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "categories": {
            "basic_encoding": {"passed": 0, "failed": 0},
            "camera_simulation": {"passed": 0, "failed": 0},
            "edge_cases": {"passed": 0, "failed": 0},
            "integration": {"passed": 0, "failed": 0},
            "performance": {"passed": 0, "failed": 0}
        }
    } 