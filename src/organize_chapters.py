"""Organize existing page audio files into chapter folders."""

import argparse
import json
import logging
import shutil
from pathlib import Path

from src.toc_extractor import Chapter
from src.voicevox_client import concatenate_audio_files

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_chapters(toc_path: Path) -> list[Chapter]:
    """Load chapters from TOC JSON file."""
    with open(toc_path, encoding="utf-8") as f:
        data = json.load(f)
    return [Chapter(**c) for c in data]


def organize_by_chapters(data_dir: Path, dry_run: bool = False) -> None:
    """Organize page WAV files into chapter folders.

    Args:
        data_dir: Directory containing toc.json and pages/ folder
        dry_run: If True, only show what would be done
    """
    toc_path = data_dir / "toc.json"
    pages_dir = data_dir / "pages"
    chapters_dir = data_dir / "chapters"

    if not toc_path.exists():
        logger.error("TOC not found: %s", toc_path)
        return

    if not pages_dir.exists():
        logger.error("Pages directory not found: %s", pages_dir)
        return

    chapters = load_chapters(toc_path)
    logger.info("Loaded %d chapters from TOC", len(chapters))

    # Get all page files
    page_files = sorted(pages_dir.glob("page_*.wav"))
    logger.info("Found %d page files", len(page_files))

    for chapter in chapters:
        chapter_dir = chapters_dir / f"chapter_{chapter.number:02d}"
        chapter_pages_dir = chapter_dir / "pages"

        # Find pages belonging to this chapter
        end_page = chapter.end_page or 9999
        chapter_files = [
            f for f in page_files
            if chapter.start_page <= int(f.stem.split("_")[1]) <= end_page
        ]

        if not chapter_files:
            logger.warning("No pages for %s (pages %d-%d)", chapter.title, chapter.start_page, end_page)
            continue

        logger.info("%s: %d pages (%d-%d)", chapter.title, len(chapter_files), chapter.start_page, end_page)

        if dry_run:
            for f in chapter_files:
                logger.info("  [DRY-RUN] Would move: %s -> %s", f.name, chapter_pages_dir / f.name)
            continue

        # Create chapter directory
        chapter_pages_dir.mkdir(parents=True, exist_ok=True)

        # Save chapter info
        info_path = chapter_dir / "info.json"
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump({
                "number": chapter.number,
                "title": chapter.title,
                "start_page": chapter.start_page,
                "end_page": chapter.end_page,
                "page_count": len(chapter_files),
            }, f, ensure_ascii=False, indent=2)

        # Move page files
        moved_files = []
        for page_file in chapter_files:
            dest = chapter_pages_dir / page_file.name
            shutil.move(str(page_file), str(dest))
            moved_files.append(dest)
            logger.info("  Moved: %s", page_file.name)

        # Concatenate chapter audio (save to chapters/ directly)
        chapter_wav = chapters_dir / f"chapter_{chapter.number:02d}.wav"
        concatenate_audio_files(moved_files, chapter_wav, silence_duration=0.3)

    # Remove empty pages directory
    if not dry_run and pages_dir.exists() and not list(pages_dir.glob("*.wav")):
        pages_dir.rmdir()
        logger.info("Removed empty pages directory")

    logger.info("Done!")


def main() -> None:
    parser = argparse.ArgumentParser(description="Organize page audio files into chapter folders")
    parser.add_argument("data_dir", help="Data directory containing toc.json and pages/")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    args = parser.parse_args()

    organize_by_chapters(Path(args.data_dir), dry_run=args.dry_run)


if __name__ == "__main__":
    main()
