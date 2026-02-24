"""Text cleaner CLI - Extract cleaned text from XML without TTS processing.

This module provides a command-line interface to generate cleaned_text.txt
from XML files without running the full TTS pipeline.

Usage:
    python -m src.text_cleaner_cli -i input.xml -o ./output

Extracted from xml2_pipeline.py main() L133-175 logic.
"""

import argparse
import logging
import sys
from pathlib import Path

from src.dict_manager import get_content_hash
from src.text_cleaner import clean_page_text, init_for_content
from src.xml2_parser import CHAPTER_MARKER, SECTION_MARKER, parse_book2_xml

logger = logging.getLogger(__name__)


def parse_args(args=None):
    """Parse command line arguments.

    Args:
        args: List of command line arguments (for testing). If None, uses sys.argv.

    Returns:
        Namespace object with parsed arguments.

    Raises:
        SystemExit: If required arguments are missing or invalid options provided.
    """
    parser = argparse.ArgumentParser(
        description="Generate cleaned_text.txt from XML file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input XML file path",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="./output",
        help="Output directory (default: ./output)",
    )

    return parser.parse_args(args)


def main(args=None):
    """Main entry point for text cleaner CLI.

    Args:
        args: List of command line arguments (for testing). If None, uses sys.argv.

    Raises:
        FileNotFoundError: If input XML file does not exist.
        xml.etree.ElementTree.ParseError: If XML is malformed.
    """
    parsed = parse_args(args)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    input_path = Path(parsed.input)

    # Validate input file exists
    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        raise FileNotFoundError(f"Input file not found: {input_path}")

    logger.info("Processing XML: %s", input_path)

    # Parse XML (will raise ParseError for invalid XML)
    content_items = parse_book2_xml(input_path)
    logger.info("Found %d content items in XML", len(content_items))

    if not content_items:
        logger.warning("No content items found")
        return

    # Combine all content text for hash/dict loading
    combined_text = " ".join(item.text for item in content_items)
    init_for_content(combined_text)

    # Generate hash-based output directory
    content_hash = get_content_hash(combined_text)
    output_base = Path(parsed.output)
    output_dir = output_base / content_hash
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Output directory: %s", output_dir)

    # Save cleaned text
    cleaned_text_path = output_dir / "cleaned_text.txt"
    with open(cleaned_text_path, "w", encoding="utf-8") as f:
        current_chapter = None

        for item in content_items:
            # Insert chapter separator when chapter changes
            if item.chapter_number is not None and item.chapter_number != current_chapter:
                current_chapter = item.chapter_number

                # Find chapter title from heading info
                chapter_title = "Untitled"
                if item.item_type == "heading" and item.heading_info and item.heading_info.level == 1:
                    chapter_title = item.heading_info.title

                f.write(f"=== Chapter {current_chapter}: {chapter_title} ===\n\n")

            # Remove markers before cleaning
            text = item.text
            if text.startswith(CHAPTER_MARKER):
                text = text[len(CHAPTER_MARKER) :]
            elif text.startswith(SECTION_MARKER):
                text = text[len(SECTION_MARKER) :]

            # Apply clean_page_text to remove URLs, parenthetical English, convert numbers, etc.
            cleaned = clean_page_text(text)

            # For headings, ensure they end with single period (。)
            # Remove any trailing punctuation and add one period
            if item.item_type == "heading" and cleaned.strip():
                cleaned = cleaned.rstrip()
                # Remove all trailing punctuation (、。！？)
                while cleaned and cleaned[-1] in "、。！？":
                    cleaned = cleaned[:-1]
                # Add single period at the end
                cleaned = cleaned + "。"

            # Skip empty content
            if cleaned.strip():
                f.write(cleaned)
                f.write("\n\n")

    logger.info("Saved cleaned text: %s", cleaned_text_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("Error: %s", e)
        sys.exit(1)
