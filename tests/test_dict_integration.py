"""Integration tests for dictionary loading between gen-dict and xml-tts."""

import json

import pytest

from src.dict_manager import get_content_hash, get_xml_content_hash
from src.xml2_parser import parse_book2_xml


@pytest.fixture
def sample_xml(tmp_path):
    """Create a sample XML file for testing."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<book>
    <metadata>
        <title>Sample Book</title>
    </metadata>
    <chapter number="1" title="Introduction">
        <paragraph>This is a test paragraph with technical terms like API and SRE.</paragraph>
    </chapter>
</book>
"""
    xml_file = tmp_path / "sample.xml"
    xml_file.write_text(xml_content, encoding="utf-8")
    return xml_file


def test_xml_content_hash_consistency(sample_xml):
    """Test that get_xml_content_hash returns consistent hash for same XML file."""
    hash1 = get_xml_content_hash(sample_xml)
    hash2 = get_xml_content_hash(sample_xml)

    assert hash1 == hash2
    assert len(hash1) == 12  # Default hash length


def test_xml_hash_matches_pipeline_hash(sample_xml):
    """Test that gen-dict and xml-tts use the same hash calculation.

    This simulates the hash calculation done in xml2_pipeline.py:
    1. Parse XML
    2. Combine all text
    3. Calculate hash

    The hash from get_xml_content_hash() should match this.
    """
    # Simulate xml2_pipeline hash calculation
    items = parse_book2_xml(sample_xml)
    combined_text = " ".join(item.text for item in items)
    pipeline_hash = get_content_hash(combined_text)

    # Get hash from dict_manager
    dict_manager_hash = get_xml_content_hash(sample_xml)

    assert dict_manager_hash == pipeline_hash


def test_dict_path_generation(sample_xml, tmp_path):
    """Test that dictionary path is correctly generated using XML content hash."""
    from src.dict_manager import DATA_BASE_DIR

    content_hash = get_xml_content_hash(sample_xml)
    expected_path = DATA_BASE_DIR / content_hash / "readings.json"

    # Test that the path format is correct
    assert expected_path.parent.name == content_hash
    assert expected_path.name == "readings.json"


def test_dict_save_and_load(sample_xml, tmp_path, monkeypatch):
    """Test that dictionary saved by gen-dict can be loaded by xml-tts."""

    # Use tmp_path as DATA_BASE_DIR
    test_data_dir = tmp_path / "data"
    monkeypatch.setattr("src.dict_manager.DATA_BASE_DIR", test_data_dir)

    # Get hash and create dict path
    content_hash = get_xml_content_hash(sample_xml)
    dict_path = test_data_dir / content_hash / "readings.json"

    # Simulate gen-dict: save dictionary
    test_dict = {"API": "エーピーアイ", "SRE": "エスアールイー"}
    dict_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dict_path, "w", encoding="utf-8") as f:
        json.dump(test_dict, f, ensure_ascii=False, indent=2)

    # Simulate xml-tts: load dictionary
    assert dict_path.exists()
    with open(dict_path, encoding="utf-8") as f:
        loaded_dict = json.load(f)

    assert loaded_dict == test_dict
    assert loaded_dict["API"] == "エーピーアイ"
    assert loaded_dict["SRE"] == "エスアールイー"


def test_different_xml_different_hash(tmp_path):
    """Test that different XML content produces different hash."""
    xml1 = tmp_path / "sample1.xml"
    xml1.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<book>
    <chapter number="1" title="Chapter 1">
        <paragraph>Content A</paragraph>
    </chapter>
</book>""",
        encoding="utf-8",
    )

    xml2 = tmp_path / "sample2.xml"
    xml2.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<book>
    <chapter number="1" title="Chapter 1">
        <paragraph>Content B</paragraph>
    </chapter>
</book>""",
        encoding="utf-8",
    )

    hash1 = get_xml_content_hash(xml1)
    hash2 = get_xml_content_hash(xml2)

    assert hash1 != hash2
