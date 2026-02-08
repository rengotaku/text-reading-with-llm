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

import numpy as np
import soundfile as sf

from src.dict_manager import get_content_hash
from src.pipeline import (
    generate_audio,
    normalize_audio,
    save_audio,
    split_text_into_chunks,
    concatenate_audio_files,
)
from src.text_cleaner import Page, clean_page_text, init_for_content
from src.voicevox_client import VoicevoxConfig, VoicevoxSynthesizer
from src.xml_parser import HEADING_MARKER, parse_book_xml, to_page

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
        default="./voicevox_core",
        help="VOICEVOX Core directory (default: ./voicevox_core)"
    )
    parser.add_argument(
        "--max-chunk-chars",
        type=int,
        default=500,
        help="Max characters per TTS chunk (default: 500)"
    )
    parser.add_argument(
        "--heading-sound",
        type=str,
        default=None,
        help="Sound file to play before headings (MP3/WAV)"
    )

    return parser.parse_args(args)


def load_heading_sound(sound_path: Path, target_sr: int = 24000) -> np.ndarray:
    """Load heading sound effect and resample to target sample rate.

    Args:
        sound_path: Path to sound file (MP3/WAV)
        target_sr: Target sample rate (default: 24000 for VOICEVOX)

    Returns:
        Audio data as numpy array
    """
    data, sr = sf.read(sound_path)

    # Convert stereo to mono if needed
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)

    # Resample if needed
    if sr != target_sr:
        from scipy import signal
        num_samples = int(len(data) * target_sr / sr)
        data = signal.resample(data, num_samples)

    # Normalize
    data = data.astype(np.float32)
    if np.max(np.abs(data)) > 0:
        data = data / np.max(np.abs(data)) * 0.5  # 50% volume

    return data


def process_pages_with_heading_sound(
    pages: list[Page],
    synthesizer: VoicevoxSynthesizer,
    output_dir: Path,
    args,
    heading_sound: np.ndarray | None = None,
) -> list[Path]:
    """Process pages with heading sound effects.

    Args:
        pages: List of Page objects
        synthesizer: VOICEVOX synthesizer
        output_dir: Output directory
        args: Parsed arguments
        heading_sound: Heading sound effect audio data

    Returns:
        List of generated WAV file paths
    """
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    wav_files = []
    sample_rate = 24000  # VOICEVOX default

    for page in pages:
        logger.info("--- Page %d ---", page.number)

        # Split text by HEADING_MARKER
        segments = page.text.split(HEADING_MARKER)
        page_audio = []

        for i, segment in enumerate(segments):
            segment = segment.strip()
            if not segment:
                continue

            # Insert heading sound before heading (except first segment if no marker)
            is_heading_segment = i > 0  # First segment is before any heading
            if is_heading_segment and heading_sound is not None:
                page_audio.append(heading_sound)

            # Split segment into chunks and synthesize
            chunks = split_text_into_chunks(segment, args.max_chunk_chars)
            for chunk_text in chunks:
                if not chunk_text.strip():
                    continue
                waveform, sr = generate_audio(
                    synthesizer,
                    text=chunk_text,
                    style_id=args.style_id,
                    speed_scale=args.speed,
                )
                waveform = normalize_audio(waveform, target_peak=0.9)
                page_audio.append(waveform)
                sample_rate = sr

        if page_audio:
            combined = np.concatenate(page_audio)
            page_path = pages_dir / f"page_{page.number:04d}.wav"
            save_audio(combined, sample_rate, page_path)
            wav_files.append(page_path)
            logger.info("  Saved: %s", page_path.name)

    # Concatenate all pages
    if wav_files:
        combined_path = output_dir / "book.wav"
        concatenate_audio_files(wav_files, combined_path)
        logger.info("Combined audio: %s", combined_path)

    return wav_files


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

    # Clean page text (preserve HEADING_MARKER through text cleaning)
    pages = []
    for page in pages_raw:
        cleaned_text = clean_page_text(page.text, heading_marker=HEADING_MARKER)
        if cleaned_text.strip():
            pages.append(Page(number=page.number, text=cleaned_text))

    logger.info("Pages after cleaning: %d", len(pages))

    # Generate hash-based output directory
    content_hash = get_content_hash(combined_text)
    output_base = Path(parsed.output)
    output_dir = output_base / content_hash
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Output directory: %s", output_dir)

    # Save cleaned text (without HEADING_MARKER for readability)
    cleaned_text_path = output_dir / "cleaned_text.txt"
    with open(cleaned_text_path, "w", encoding="utf-8") as f:
        for page in pages:
            f.write(f"=== Page {page.number} ===\n")
            # Remove HEADING_MARKER for display, replace with newline for readability
            display_text = page.text.replace(HEADING_MARKER, "\n[見出し] ")
            f.write(display_text)
            f.write("\n\n")
    logger.info("Saved cleaned text: %s", cleaned_text_path)

    # Load heading sound if specified
    heading_sound = None
    if parsed.heading_sound:
        sound_path = Path(parsed.heading_sound)
        if sound_path.exists():
            logger.info("Loading heading sound: %s", sound_path)
            heading_sound = load_heading_sound(sound_path)
            logger.info("Heading sound loaded (%.2f sec)", len(heading_sound) / 24000)
        else:
            logger.warning("Heading sound file not found: %s", sound_path)

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

    # Process pages and generate audio with heading sound
    process_pages_with_heading_sound(
        pages, synthesizer, output_dir, parsed, heading_sound=heading_sound
    )
    logger.info("Audio generation complete")


if __name__ == "__main__":
    main()
