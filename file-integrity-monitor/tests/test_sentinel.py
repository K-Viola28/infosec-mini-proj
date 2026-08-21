import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from sentinel import (
    calculate_hash,
    compare_hashes,
    verify_baseline,
    load_baseline
)

def test_hash_is_consistent(tmp_path):
    test_file = tmp_path / "test.txt"

    test_file.write_text("Hello Sentinel")

    first_hash = calculate_hash(test_file)
    second_hash = calculate_hash(test_file)

    assert first_hash == second_hash

def test_hash_changes_when_file_changes(tmp_path):
    test_file = tmp_path / "test.txt"

    test_file.write_text("Original content")

    original_hash = calculate_hash(test_file)

    test_file.write_text("Modified content")

    modified_hash = calculate_hash(test_file)

    assert original_hash != modified_hash

def test_unchanged_file():
    baseline = {
        "file.txt": "abc123"
    }

    current = {
        "file.txt": "abc123"
    }

    results = compare_hashes(baseline, current)

    assert "file.txt" in results["unchanged"]

def test_modified_file():
    baseline = {
        "file.txt": "abc123"
    }

    current = {
        "file.txt": "xyz789"
    }

    results = compare_hashes(baseline, current)

    assert "file.txt" in results["modified"]

def test_deleted_file():
    baseline = {
        "file.txt": "abc123"
    }

    current = {}

    results = compare_hashes(baseline, current)

    assert "file.txt" in results["deleted"]

def test_new_file():
    baseline = {}

    current = {
        "new_file.txt": "xyz789"
    }

    results = compare_hashes(baseline, current)

    assert "new_file.txt" in results["new"]

def test_file_has_one_status():
    baseline = {
        "file.txt": "abc123"
    }

    current = {
        "file.txt": "xyz789"
    }

    results = compare_hashes(baseline, current)

    assert "file.txt" in results["modified"]
    assert "file.txt" not in results["unchanged"]
    assert "file.txt" not in results["deleted"]
    assert "file.txt" not in results["new"]

def test_valid_baseline(tmp_path, monkeypatch):
    baseline_file = tmp_path / "baseline.json"
    hash_file = tmp_path / "baseline.hash"

    baseline_file.write_text('{"file.txt": "abc123"}')

    expected_hash = calculate_hash(baseline_file)
    hash_file.write_text(expected_hash)

    monkeypatch.setattr("sentinel.BASELINE_FILE", baseline_file)
    monkeypatch.setattr("sentinel.BASELINE_HASH_FILE", hash_file)

    assert verify_baseline() is True

def test_tampered_baseline(tmp_path, monkeypatch):
    baseline_file = tmp_path / "baseline.json"
    hash_file = tmp_path / "baseline.hash"

    baseline_file.write_text('{"file.txt": "abc123"}')

    original_hash = calculate_hash(baseline_file)
    hash_file.write_text(original_hash)

    baseline_file.write_text('{"file.txt": "TAMPERED"}')

    monkeypatch.setattr("sentinel.BASELINE_FILE", baseline_file)
    monkeypatch.setattr("sentinel.BASELINE_HASH_FILE", hash_file)

    assert verify_baseline() is False

def test_missing_baseline_hash(tmp_path, monkeypatch):
    baseline_file = tmp_path / "baseline.json"
    hash_file = tmp_path / "baseline.hash"

    baseline_file.write_text('{"file.txt": "abc123"}')

    monkeypatch.setattr("sentinel.BASELINE_FILE", baseline_file)
    monkeypatch.setattr("sentinel.BASELINE_HASH_FILE", hash_file)

    assert verify_baseline() is False

def test_corrupted_baseline(tmp_path, monkeypatch):
    baseline_file = tmp_path / "baseline.json"

    baseline_file.write_text("this is not valid JSON")

    monkeypatch.setattr("sentinel.BASELINE_FILE", baseline_file)

    assert load_baseline() is None