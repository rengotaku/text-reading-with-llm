"""Hash-based dictionary management for per-book reading dictionaries."""

import hashlib
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Base directory for all data (hash-based folders)
DATA_BASE_DIR = Path(__file__).parent.parent / "data"

# Legacy path for backward compatibility
DICT_BASE_DIR = DATA_BASE_DIR / "readings"


def get_content_hash(content: str, length: int = 12) -> str:
    """Generate a short hash from content.

    Args:
        content: Text content to hash
        length: Length of the returned hash (default: 12 chars)

    Returns:
        Short hex hash string
    """
    full_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return full_hash[:length]


def get_dict_path(input_path: Path) -> Path:
    """Get the dictionary path for a given input file.

    Uses content hash to uniquely identify the book.

    Args:
        input_path: Path to the input markdown file

    Returns:
        Path to the corresponding dictionary JSON file
    """
    content = input_path.read_text(encoding="utf-8")
    content_hash = get_content_hash(content)
    return DICT_BASE_DIR / f"{content_hash}.json"


def get_output_dir(content: str) -> Path:
    """Get the output directory for a given content.

    Args:
        content: The markdown content

    Returns:
        Path to the hash-based output directory
    """
    content_hash = get_content_hash(content)
    return DATA_BASE_DIR / content_hash


def get_dict_path_from_content(content: str) -> Path:
    """Get the dictionary path from content directly.

    Args:
        content: The markdown content

    Returns:
        Path to the corresponding dictionary JSON file
    """
    content_hash = get_content_hash(content)
    # New path: data/{hash}/readings.json
    new_path = DATA_BASE_DIR / content_hash / "readings.json"
    # Legacy path: data/readings/{hash}.json
    legacy_path = DICT_BASE_DIR / f"{content_hash}.json"

    # Prefer new path if exists, otherwise check legacy
    if new_path.exists():
        return new_path
    if legacy_path.exists():
        return legacy_path
    # Default to new path for new files
    return new_path


def load_dict(input_path: Path) -> dict[str, str]:
    """Load the reading dictionary for a given input file.

    Args:
        input_path: Path to the input markdown file

    Returns:
        Dictionary mapping terms to readings, or empty dict if not found
    """
    dict_path = get_dict_path(input_path)
    if dict_path.exists():
        with open(dict_path, encoding="utf-8") as f:
            data = json.load(f)
            logger.info("Loaded %d readings from %s", len(data), dict_path.name)
            return data
    logger.info("No dictionary found for %s (expected: %s)", input_path.name, dict_path.name)
    return {}


def load_dict_from_content(content: str) -> dict[str, str]:
    """Load the reading dictionary from content hash.

    Args:
        content: The markdown content

    Returns:
        Dictionary mapping terms to readings, or empty dict if not found
    """
    dict_path = get_dict_path_from_content(content)
    if dict_path.exists():
        with open(dict_path, encoding="utf-8") as f:
            data = json.load(f)
            logger.debug("Loaded %d readings from %s", len(data), dict_path.name)
            return data
    return {}


def save_dict(readings: dict[str, str], input_path: Path) -> Path:
    """Save the reading dictionary for a given input file.

    Args:
        readings: Dictionary mapping terms to readings
        input_path: Path to the input markdown file

    Returns:
        Path where the dictionary was saved
    """
    content = input_path.read_text(encoding="utf-8")
    content_hash = get_content_hash(content)
    # Save to new path: data/{hash}/readings.json
    dict_path = DATA_BASE_DIR / content_hash / "readings.json"
    dict_path.parent.mkdir(parents=True, exist_ok=True)

    with open(dict_path, "w", encoding="utf-8") as f:
        json.dump(readings, f, ensure_ascii=False, indent=2)

    logger.info("Saved %d readings to %s", len(readings), dict_path)
    return dict_path


def list_dicts() -> list[tuple[str, int]]:
    """List all available dictionaries.

    Returns:
        List of (filename, entry_count) tuples
    """
    if not DICT_BASE_DIR.exists():
        return []

    result = []
    for path in DICT_BASE_DIR.glob("*.json"):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                result.append((path.name, len(data)))
        except (json.JSONDecodeError, OSError):
            result.append((path.name, -1))

    return sorted(result)
