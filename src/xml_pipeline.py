"""XML to TTS pipeline for VOICEVOX.

This module provides a command-line interface to generate TTS audio
from XML book files using the VOICEVOX synthesizer.

Integration with existing components:
- xml_parser: Parse XML and extract page content
- text_cleaner: Clean text for TTS consumption
- pipeline: Generate audio files
- voicevox_client: VOICEVOX synthesis
"""

import argparse
import logging
import sys
from pathlib import Path

from src.dict_manager import get_content_hash
from src.pipeline import process_pages
from src.text_cleaner import Page, clean_page_text, init_for_content
from src.voicevox_client import VoicevoxConfig, VoicevoxSynthesizer
from src.xml_parser import parse_book_xml, to_page

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args(args=None):
    """Parse command line arguments.

    Args:
        args: List of arguments (for testing). If None, uses sys.argv.

    Returns:
        argparse.Namespace with parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate TTS audio from XML book files"
    )

    # Required
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input XML file path"
    )

    # Optional with defaults
    parser.add_argument(
        "--output", "-o",
        default="./output",
        help="Output directory (default: ./output)"
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="Start page number (default: 1)"
    )
    parser.add_argument(
        "--end-page",
        type=int,
        default=None,
        help="End page number (default: last page)"
    )
    parser.add_argument(
        "--style-id",
        type=int,
        default=13,
        help="VOICEVOX style ID (default: 13)"
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speech speed (default: 1.0)"
    )
    parser.add_argument(
        "--voicevox-dir",
        default="./voicevox_core_cuda",
        help="VOICEVOX Core directory (default: ./voicevox_core_cuda)"
    )
    parser.add_argument(
        "--max-chunk-chars",
        type=int,
        default=500,
        help="Max characters per TTS chunk (default: 500)"
    )

    return parser.parse_args(args)


def main(args=None):
    """Main entry point.

    Args:
        args: List of arguments (for testing). If None, uses sys.argv.

    Raises:
        FileNotFoundError: If input file does not exist
        xml.etree.ElementTree.ParseError: If XML is malformed
    """
    parsed = parse_args(args)

    # Check file existence
    input_path = Path(parsed.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {parsed.input}")

    logger.info("Reading XML: %s", input_path)

    # Parse XML (will raise ParseError for invalid XML)
    xml_pages = parse_book_xml(input_path)
    logger.info("Found %d pages in XML", len(xml_pages))

    # Filter page range
    if parsed.end_page:
        xml_pages = [p for p in xml_pages if parsed.start_page <= p.number <= parsed.end_page]
    else:
        xml_pages = [p for p in xml_pages if p.number >= parsed.start_page]

    if not xml_pages:
        logger.warning("No pages in specified range")
        return

    logger.info("Processing %d pages (range: %d-%s)",
                len(xml_pages), parsed.start_page, parsed.end_page or "end")

    # Convert to Page objects
    pages_raw = [to_page(xp) for xp in xml_pages]

    # Initialize text cleaner with combined content for hash/dict loading
    combined_text = "\n".join(p.text for p in pages_raw)
    init_for_content(combined_text)

    # Clean page text
    pages = []
    for page in pages_raw:
        cleaned_text = clean_page_text(page.text)
        if cleaned_text.strip():
            pages.append(Page(number=page.number, text=cleaned_text))

    logger.info("Pages after cleaning: %d", len(pages))

    # Generate hash-based output directory
    content_hash = get_content_hash(combined_text)
    output_base = Path(parsed.output)
    output_dir = output_base / content_hash
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Output directory: %s", output_dir)

    # Save cleaned text
    cleaned_text_path = output_dir / "cleaned_text.txt"
    with open(cleaned_text_path, "w", encoding="utf-8") as f:
        for page in pages:
            f.write(f"=== Page {page.number} ===\n")
            f.write(page.text)
            f.write("\n\n")
    logger.info("Saved cleaned text: %s", cleaned_text_path)

    # Initialize VOICEVOX synthesizer
    voicevox_dir = Path(parsed.voicevox_dir)
    config = VoicevoxConfig(
        onnxruntime_dir=voicevox_dir / "onnxruntime" / "lib",
        open_jtalk_dict_dir=voicevox_dir / "dict" / "open_jtalk_dic_utf_8-1.11",
        vvm_dir=voicevox_dir / "models" / "vvms",
        style_id=parsed.style_id,
        speed_scale=parsed.speed,
        pitch_scale=0.0,
        volume_scale=1.0,
    )
    synthesizer = VoicevoxSynthesizer(config)
    synthesizer.initialize()
    synthesizer.load_all_models()
    logger.info("VOICEVOX initialized (style_id=%d)", parsed.style_id)

    # Process pages and generate audio
    process_pages(pages, synthesizer, output_dir, parsed, output_filename="book.wav")
    logger.info("Audio generation complete")


if __name__ == "__main__":
    main()
