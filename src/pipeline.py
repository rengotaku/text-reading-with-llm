"""TTS pipeline: markdown → cleaned text → audio files.

VOICEVOX Core を使用した音声合成パイプライン。
出力は入力ファイルのハッシュに基づいたフォルダに保存される。
"""

import argparse
import logging
import sys
import time
from pathlib import Path

import yaml

from src.dict_manager import get_content_hash
from src.progress import ChunkInfo, ProgressTracker
from src.text_cleaner import Page, init_for_content, split_into_pages, split_text_into_chunks
from src.toc_extractor import Chapter, extract_toc, get_last_page, group_by_chapter, recalculate_end_pages, to_json
from src.voicevox_client import (
    AOYAMA_RYUSEI_STYLE_ID,
    VoicevoxConfig,
    VoicevoxSynthesizer,
    concatenate_audio_files,
    generate_audio,
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
    voicevox_config = config.get("voicevox", {})

    parser = argparse.ArgumentParser(
        description="Generate TTS audio from markdown text using VOICEVOX"
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
    # VOICEVOX settings
    parser.add_argument(
        "--voicevox-dir",
        default=voicevox_config.get("dir", "voicevox_core"),
        help="VOICEVOX Core directory (default: %(default)s)",
    )
    parser.add_argument(
        "--style-id",
        type=int,
        default=voicevox_config.get("style_id", AOYAMA_RYUSEI_STYLE_ID),
        help="VOICEVOX style ID (default: %(default)s = 青山龍星)",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=voicevox_config.get("speed", 1.0),
        help="Speech speed (default: %(default)s)",
    )
    parser.add_argument(
        "--pitch",
        type=float,
        default=voicevox_config.get("pitch", 0.0),
        help="Pitch adjustment (default: %(default)s)",
    )
    parser.add_argument(
        "--volume",
        type=float,
        default=voicevox_config.get("volume", 1.0),
        help="Volume (default: %(default)s)",
    )
    # Chunk settings
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
    # Chapter-based processing
    parser.add_argument(
        "--toc",
        help="Path to TOC JSON file for chapter-based processing",
    )
    parser.add_argument(
        "--generate-toc",
        action="store_true",
        help="Auto-generate TOC and save to output directory",
    )
    parser.add_argument(
        "--toc-start-page",
        type=int,
        default=1,
        help="Start page for TOC extraction (skip front matter)",
    )
    return parser.parse_args()


def process_pages(
    pages: list[Page],
    synthesizer: VoicevoxSynthesizer,
    output_dir: Path,
    args: argparse.Namespace,
    output_filename: str = "combined.wav",
    combined_output_path: Path | None = None,
) -> list[Path]:
    """Process pages and generate audio files.

    Args:
        combined_output_path: If specified, save combined audio here instead of output_dir/output_filename

    Returns list of generated WAV file paths.
    """
    import numpy as np

    pages_dir = output_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    # Pre-compute chunks
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

    if not all_chunk_infos:
        return []

    # Generate audio
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
                synthesizer,
                text=chunk_text,
                style_id=args.style_id,
                speed_scale=args.speed,
            )
            waveform = normalize_audio(waveform, target_peak=0.9)
            page_audio.append(waveform)
            page_sr = sr

            chunk_time = time.time() - chunk_start
            tracker.on_chunk_done(chunk_info, chunk_time)

        if page_audio and page_sr:
            combined = np.concatenate(page_audio)
            page_path = pages_dir / f"page_{page.number:04d}.wav"
            save_audio(combined, page_sr, page_path)
            wav_files.append(page_path)

        page_time = time.time() - page_start
        tracker.on_page_done(page.number, page_time)

    # Concatenate all pages
    if wav_files:
        combined_path = combined_output_path or (output_dir / output_filename)
        concatenate_audio_files(wav_files, combined_path)

    tracker.finish()
    return wav_files


def generate_toc(markdown: str, start_page: int) -> list[Chapter]:
    """Generate TOC from markdown content."""
    entries = extract_toc(markdown)
    entries = [e for e in entries if e.start_page >= start_page]
    last_page = get_last_page(markdown)
    chapters = group_by_chapter(entries)
    recalculate_end_pages(chapters, last_page)
    return chapters


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        sys.exit(1)

    # Step 1: Read markdown
    logger.info("Reading: %s", input_path)
    markdown = input_path.read_text(encoding="utf-8")

    # Generate hash-based output directory
    content_hash = get_content_hash(markdown)
    output_base = Path(args.output)
    output_dir = output_base / content_hash
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Output directory: %s", output_dir)

    # Initialize text cleaner
    init_for_content(markdown)

    all_pages = split_into_pages(markdown)
    logger.info("Found %d pages total", len(all_pages))

    # Step 2: Initialize VOICEVOX synthesizer
    voicevox_dir = Path(args.voicevox_dir)
    config = VoicevoxConfig(
        onnxruntime_dir=voicevox_dir / "onnxruntime" / "lib",
        open_jtalk_dict_dir=voicevox_dir / "dict" / "open_jtalk_dic_utf_8-1.11",
        vvm_dir=voicevox_dir / "models" / "vvms",
        style_id=args.style_id,
        speed_scale=args.speed,
        pitch_scale=args.pitch,
        volume_scale=args.volume,
    )
    synthesizer = VoicevoxSynthesizer(config)
    synthesizer.initialize()
    synthesizer.load_all_models()
    logger.info("VOICEVOX initialized (style_id=%d)", args.style_id)

    # Step 3: Determine processing mode
    chapters: list[Chapter] | None = None

    if args.toc:
        # Load TOC from file
        import json
        with open(args.toc, encoding="utf-8") as f:
            data = json.load(f)
        chapters = [Chapter(**c) for c in data]
        logger.info("Loaded TOC: %d chapters", len(chapters))

    elif args.generate_toc:
        # Auto-generate TOC
        chapters = generate_toc(markdown, args.toc_start_page)
        toc_path = output_dir / "toc.json"
        with open(toc_path, "w", encoding="utf-8") as f:
            f.write(to_json(chapters))
        logger.info("Generated TOC: %d chapters -> %s", len(chapters), toc_path)

    # Save cleaned text (always, before TTS processing)
    cleaned_text_path = output_dir / "cleaned_text.txt"
    with open(cleaned_text_path, "w", encoding="utf-8") as f:
        for page in all_pages:
            f.write(f"=== Page {page.number} ===\n")
            f.write(page.text)
            f.write("\n\n")
    logger.info("Saved cleaned text: %s", cleaned_text_path)

    # Step 4: Process based on mode
    if chapters:
        # Chapter-based processing
        chapters_dir = output_dir / "chapters"
        chapters_dir.mkdir(parents=True, exist_ok=True)

        for chapter in chapters:
            logger.info("=== %s (pages %d-%s) ===", chapter.title, chapter.start_page, chapter.end_page or "end")

            # Filter pages for this chapter
            end_page = chapter.end_page or max(p.number for p in all_pages)
            chapter_pages = [p for p in all_pages if chapter.start_page <= p.number <= end_page]

            if not chapter_pages:
                logger.warning("No pages for %s", chapter.title)
                continue

            # Create chapter directory
            chapter_dir = chapters_dir / f"chapter_{chapter.number:02d}"
            chapter_dir.mkdir(parents=True, exist_ok=True)

            # Save chapter info
            info_path = chapter_dir / "info.json"
            import json
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump({
                    "number": chapter.number,
                    "title": chapter.title,
                    "start_page": chapter.start_page,
                    "end_page": chapter.end_page,
                    "page_count": len(chapter_pages),
                }, f, ensure_ascii=False, indent=2)

            # Process pages (combined audio goes to chapters/ directly)
            chapter_wav = chapters_dir / f"chapter_{chapter.number:02d}.wav"
            process_pages(
                chapter_pages,
                synthesizer,
                chapter_dir,
                args,
                combined_output_path=chapter_wav,
            )

        logger.info("Completed all chapters")

    else:
        # Single range processing (original behavior)
        if args.end_page:
            pages = [p for p in all_pages if args.start_page <= p.number <= args.end_page]
        else:
            pages = [p for p in all_pages if p.number >= args.start_page]
        logger.info("Processing %d pages (range: %d-%s)", len(pages), args.start_page, args.end_page or "end")

        if not pages:
            logger.warning("No pages to process")
            sys.exit(0)

        # Process pages
        process_pages(pages, synthesizer, output_dir, args, output_filename="book.wav")


if __name__ == "__main__":
    main()
