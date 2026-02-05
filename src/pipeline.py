"""TTS pipeline: markdown → cleaned text → audio files."""

import argparse
import logging
import sys
import time
from pathlib import Path

import yaml

from src.progress import ChunkInfo, ProgressTracker
from src.text_cleaner import Page, init_for_content, split_into_pages, split_text_into_chunks
from src.tts_generator import (
    concatenate_audio_files,
    generate_audio,
    load_model,
    normalize_audio,
    save_audio,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_config() -> dict:
    """Load config.yaml if it exists."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    return {}


def parse_args() -> argparse.Namespace:
    config = load_config()

    parser = argparse.ArgumentParser(
        description="Generate TTS audio from markdown text"
    )
    parser.add_argument(
        "input",
        help="Path to input markdown file",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=config.get("output", "output"),
        help="Output directory (default: %(default)s)",
    )
    parser.add_argument(
        "--model",
        default=config.get("tts_model", "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"),
        help="TTS model name (default: %(default)s)",
    )
    parser.add_argument(
        "--speaker",
        default=config.get("speaker", "Ono_Anna"),
        help="Speaker name (default: %(default)s)",
    )
    parser.add_argument(
        "--language",
        default=config.get("language", "Japanese"),
        help="Language (default: %(default)s)",
    )
    parser.add_argument(
        "--instruct",
        default=config.get("instruct", ""),
        help="Voice style instruction (default: from config)",
    )
    parser.add_argument(
        "--device",
        default=config.get("device", "cuda:0"),
        help="Device (default: %(default)s)",
    )
    parser.add_argument(
        "--dtype",
        default=config.get("dtype", "bfloat16"),
        help="Data type (default: %(default)s)",
    )
    parser.add_argument(
        "--max-chunk-chars",
        type=int,
        default=config.get("max_chunk_chars", 500),
        help="Max characters per TTS chunk (default: %(default)s)",
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="Start from this page number (default: 1)",
    )
    parser.add_argument(
        "--end-page",
        type=int,
        default=None,
        help="End at this page number (default: all pages)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        sys.exit(1)

    output_dir = Path(args.output)
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Read and clean text
    logger.info("Reading: %s", input_path)
    markdown = input_path.read_text(encoding="utf-8")

    # Initialize text cleaner with book-specific dictionary
    init_for_content(markdown)

    pages = split_into_pages(markdown)
    logger.info("Found %d pages", len(pages))

    # Filter pages by range
    if args.end_page:
        pages = [p for p in pages if args.start_page <= p.number <= args.end_page]
    else:
        pages = [p for p in pages if p.number >= args.start_page]
    logger.info("Processing %d pages (range: %d-%s)", len(pages), args.start_page, args.end_page or "end")

    if not pages:
        logger.warning("No pages to process")
        sys.exit(0)

    # Save cleaned text for reference
    cleaned_text_path = output_dir / "cleaned_text.txt"
    with open(cleaned_text_path, "w", encoding="utf-8") as f:
        for page in pages:
            f.write(f"=== Page {page.number} ===\n")
            f.write(page.text)
            f.write("\n\n")
    logger.info("Saved cleaned text: %s", cleaned_text_path)

    # Step 2: Pre-compute all chunks for progress tracking
    page_chunks: list[tuple[Page, list[tuple[ChunkInfo, str]]]] = []
    all_chunk_infos: list[ChunkInfo] = []
    chunk_idx = 0

    for page in pages:
        text_chunks = split_text_into_chunks(page.text, args.max_chunk_chars)
        page_chunk_list: list[tuple[ChunkInfo, str]] = []
        for text in text_chunks:
            info = ChunkInfo(page_num=page.number, chunk_idx=chunk_idx, char_count=len(text))
            page_chunk_list.append((info, text))
            all_chunk_infos.append(info)
            chunk_idx += 1
        page_chunks.append((page, page_chunk_list))

    # Step 3: Load TTS model
    model = load_model(args.model, args.device, args.dtype)

    # Step 4: Generate audio per page with progress tracking
    tracker = ProgressTracker(chunks=all_chunk_infos, total_pages=len(pages))
    tracker.start()

    wav_files = []

    for page, chunks_with_info in page_chunks:
        page_start = time.time()
        logger.info("--- Page %d ---", page.number)
        logger.info("  %d chunks", len(chunks_with_info))

        page_audio = []
        page_sr = None

        for chunk_info, chunk_text in chunks_with_info:
            chunk_start = time.time()
            logger.info("  Chunk %d/%d (%d chars): %.40s...", chunk_info.chunk_idx + 1, len(all_chunk_infos), chunk_info.char_count, chunk_text)
            waveform, sr = generate_audio(
                model,
                text=chunk_text,
                language=args.language,
                speaker=args.speaker,
                instruct=args.instruct,
            )
            # Normalize each chunk to consistent volume
            waveform = normalize_audio(waveform, target_peak=0.9)
            page_audio.append(waveform)
            page_sr = sr

            chunk_time = time.time() - chunk_start
            tracker.on_chunk_done(chunk_info, chunk_time)

        if page_audio and page_sr:
            import numpy as np

            combined = np.concatenate(page_audio)
            page_path = pages_dir / f"page_{page.number:04d}.wav"
            save_audio(combined, page_sr, page_path)
            wav_files.append(page_path)

        page_time = time.time() - page_start
        tracker.on_page_done(page.number, page_time)

    # Step 5: Concatenate all pages
    if wav_files:
        combined_path = output_dir / "book.wav"
        concatenate_audio_files(wav_files, combined_path)

    tracker.finish()


if __name__ == "__main__":
    main()
