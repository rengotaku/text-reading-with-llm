"""XML2 to TTS pipeline for VOICEVOX (book2.xml format).

This module provides a command-line interface to generate TTS audio
from book2.xml files using the VOICEVOX synthesizer.

Integration with existing components:
- xml2_parser: Parse book2.xml and extract content items
- text_cleaner: Clean text for TTS consumption
- pipeline: Generate audio files
- voicevox_client: VOICEVOX synthesis
"""

import argparse
import atexit
import logging
from pathlib import Path

# Re-exports from split modules (for backward compatibility)
from src.chapter_processor import (  # noqa: F401
    load_sound,
    process_chapters,
    process_content,
    sanitize_filename,
)
from src.dict_manager import get_content_hash
from src.process_manager import (  # noqa: F401
    cleanup_pid_file,
    get_pid_file_path,
    kill_existing_process,
    write_pid_file,
)
from src.text_cleaner import clean_page_text, init_for_content, split_text_into_chunks  # noqa: F401
from src.voicevox_client import (  # noqa: F401
    VoicevoxConfig,
    VoicevoxSynthesizer,
    concatenate_audio_files,
    generate_audio,
    normalize_audio,
    save_audio,
)
from src.xml2_parser import CHAPTER_MARKER, SECTION_MARKER, ContentItem, parse_book2_xml  # noqa: F401

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: List of arguments (for testing). If None, uses sys.argv.

    Returns:
        argparse.Namespace with parsed arguments
    """
    parser = argparse.ArgumentParser(description="Generate TTS audio from book2.xml files")

    # Required
    parser.add_argument("--input", "-i", required=True, help="Input XML file path")

    # Optional with defaults
    parser.add_argument("--output", "-o", default="./output", help="Output directory (default: ./output)")
    parser.add_argument(
        "--chapter-sound",
        default="assets/sounds/chapter.mp3",
        help="Sound file to play before chapters (MP3/WAV) (default: assets/sounds/chapter.mp3)",
    )
    parser.add_argument(
        "--section-sound",
        default="assets/sounds/section.mp3",
        help="Sound file to play before sections (MP3/WAV) (default: assets/sounds/section.mp3)",
    )
    parser.add_argument("--style-id", type=int, default=13, help="VOICEVOX style ID (default: 13)")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (default: 1.0)")
    parser.add_argument(
        "--voicevox-dir", default="./voicevox_core", help="VOICEVOX Core directory (default: ./voicevox_core)"
    )
    parser.add_argument("--max-chunk-chars", type=int, default=500, help="Max characters per TTS chunk (default: 500)")
    parser.add_argument("--start-page", type=int, default=1, help="Start page number (default: 1)")
    parser.add_argument("--end-page", type=int, default=None, help="End page number (default: last page)")
    parser.add_argument(
        "--cleaned-text",
        default=None,
        help="Path to existing cleaned_text.txt (skip text cleaning if provided)",
    )

    return parser.parse_args(args)


def main(args: list[str] | None = None) -> None:
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

    # PID file management (Rails-style)
    pid_file = get_pid_file_path(str(input_path))
    kill_existing_process(pid_file)
    write_pid_file(pid_file)
    # Register cleanup on exit
    atexit.register(cleanup_pid_file, pid_file)

    logger.info("Reading XML: %s", input_path)

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

    # Check if --cleaned-text option is provided
    if parsed.cleaned_text:
        # Use existing cleaned_text.txt file
        cleaned_text_path = Path(parsed.cleaned_text)
        if not cleaned_text_path.exists():
            raise FileNotFoundError(f"Cleaned text file not found: {parsed.cleaned_text}")
        logger.info("Using existing cleaned text: %s", cleaned_text_path)
    else:
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

    # Load sound effects if specified
    chapter_sound = None
    section_sound = None

    if parsed.chapter_sound:
        sound_path = Path(parsed.chapter_sound)
        if sound_path.exists():
            logger.info("Loading chapter sound: %s", sound_path)
            chapter_sound = load_sound(sound_path)
            logger.info("Chapter sound loaded (%.2f sec)", len(chapter_sound) / 24000)
        else:
            logger.warning("Chapter sound file not found: %s", sound_path)

    if parsed.section_sound:
        sound_path = Path(parsed.section_sound)
        if sound_path.exists():
            logger.info("Loading section sound: %s", sound_path)
            section_sound = load_sound(sound_path)
            logger.info("Section sound loaded (%.2f sec)", len(section_sound) / 24000)
        else:
            logger.warning("Section sound file not found: %s", sound_path)

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
    synthesizer.load_model_for_style_id(parsed.style_id)
    logger.info("VOICEVOX initialized (style_id=%d)", parsed.style_id)

    # Process content and generate audio
    process_chapters(
        content_items,
        synthesizer,
        output_dir,
        parsed,
        chapter_sound=chapter_sound,
        section_sound=section_sound,
    )
    logger.info("Audio generation complete")


if __name__ == "__main__":
    main()
