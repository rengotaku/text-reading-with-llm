"""Extract table of contents (TOC) structure from book markdown."""

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class TocEntry:
    """A single TOC entry."""

    title: str
    level: int  # 1 = #, 2 = ##, 3 = ###, etc.
    start_page: int
    end_page: int | None = None  # Filled in post-processing


def extract_toc(
    markdown: str,
    skip_toc_pages: bool = True,
    toc_end_marker: str | None = None,
) -> list[TocEntry]:
    """Extract TOC entries from book markdown.

    Args:
        markdown: Book markdown content
        skip_toc_pages: Skip entries from table of contents pages
        toc_end_marker: Pattern to detect end of TOC section (e.g., "第1章")

    Returns list of TocEntry with start_page and end_page populated.
    """
    entries: list[TocEntry] = []
    current_page = 0
    in_toc_section = False
    toc_ended = False

    # Page marker pattern
    page_pattern = re.compile(r"^--- Page (\d+) \(page_\d+\.png\) ---$")
    # Heading pattern (captures level and title)
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")
    # TOC page detection (lines like "第1章 SREとは" without # prefix)
    toc_line_pattern = re.compile(r"^第\d+章\s+\S")

    for line in markdown.split("\n"):
        # Check for page marker
        page_match = page_pattern.match(line)
        if page_match:
            current_page = int(page_match.group(1))
            continue

        # Detect TOC section (pages with chapter listings without # prefix)
        if skip_toc_pages and not toc_ended:
            if toc_line_pattern.match(line):
                in_toc_section = True
                continue

        # Check for heading
        heading_match = heading_pattern.match(line)
        if heading_match and current_page > 0:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()

            # Skip book title repetitions and horizontal rule markers
            if _should_skip_heading(title):
                continue

            # If we were in TOC section and now see a real heading, TOC ended
            if in_toc_section:
                toc_ended = True
                in_toc_section = False

            entries.append(
                TocEntry(
                    title=title,
                    level=level,
                    start_page=current_page,
                )
            )

    # Find last page number
    last_page = current_page

    # Fill in end_page for each entry
    _fill_end_pages(entries, last_page)

    return entries


def _should_skip_heading(title: str) -> bool:
    """Check if heading should be skipped."""
    skip_patterns = [
        r"^SREの知識地図",  # Book title repetition
        r"^[-─]+$",  # Horizontal rules
    ]
    for pattern in skip_patterns:
        if re.match(pattern, title):
            return True
    return False


def _fill_end_pages(entries: list[TocEntry], last_page: int | None = None) -> None:
    """Fill in end_page for each entry based on next entry's start_page."""
    for i, entry in enumerate(entries):
        if i + 1 < len(entries):
            # End page is one before next entry's start, or same if same page
            next_start = entries[i + 1].start_page
            entry.end_page = max(entry.start_page, next_start - 1)
        else:
            # Last entry: use last_page if provided
            entry.end_page = last_page


def recalculate_end_pages(
    entries: list[TocEntry] | list["Chapter"], last_page: int | None = None
) -> None:
    """Recalculate end_page for filtered entries or chapters."""
    for i, entry in enumerate(entries):
        if i + 1 < len(entries):
            next_start = entries[i + 1].start_page
            entry.end_page = max(entry.start_page, next_start - 1)
        else:
            entry.end_page = last_page


def filter_by_level(entries: list[TocEntry], max_level: int) -> list[TocEntry]:
    """Filter entries to only include headings up to max_level."""
    return [e for e in entries if e.level <= max_level]


def find_chapters(entries: list[TocEntry]) -> list[TocEntry]:
    """Find chapter-level entries (typically '第N章' pattern)."""
    chapter_pattern = re.compile(r"^第\d+章")
    return [e for e in entries if chapter_pattern.match(e.title)]


@dataclass
class Chapter:
    """A chapter grouping multiple sections."""

    number: int
    title: str
    start_page: int
    end_page: int | None


def group_by_chapter(entries: list[TocEntry]) -> list[Chapter]:
    """Group entries by chapter number (from 'Section N.M' pattern)."""
    section_pattern = re.compile(r"^Section (\d+)\.")
    chapters: dict[int, Chapter] = {}

    for entry in entries:
        match = section_pattern.match(entry.title)
        if match:
            chapter_num = int(match.group(1))
            if chapter_num not in chapters:
                chapters[chapter_num] = Chapter(
                    number=chapter_num,
                    title=f"第{chapter_num}章",
                    start_page=entry.start_page,
                    end_page=entry.end_page,
                )
            else:
                # Update end_page to latest section's end
                if entry.end_page:
                    chapters[chapter_num].end_page = entry.end_page

    return sorted(chapters.values(), key=lambda c: c.number)


def get_last_page(markdown: str) -> int:
    """Get the last page number from markdown."""
    page_pattern = re.compile(r"^--- Page (\d+) \(page_\d+\.png\) ---$", re.MULTILINE)
    matches = page_pattern.findall(markdown)
    return int(matches[-1]) if matches else 0


def to_json(entries: list[TocEntry] | list[Chapter], indent: int = 2) -> str:
    """Convert entries to JSON string."""
    return json.dumps(
        [asdict(e) for e in entries],
        ensure_ascii=False,
        indent=indent,
    )


def save_toc(entries: list[TocEntry], output_path: Path) -> None:
    """Save TOC entries to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(to_json(entries))


def load_toc(toc_path: Path) -> list[TocEntry]:
    """Load TOC entries from JSON file."""
    with open(toc_path, encoding="utf-8") as f:
        data = json.load(f)
    return [TocEntry(**entry) for entry in data]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract TOC from book markdown")
    parser.add_argument("input", help="Path to book.md")
    parser.add_argument("-o", "--output", help="Output JSON path")
    parser.add_argument(
        "--level",
        type=int,
        default=None,
        help="Max heading level to include (e.g., 2 for ## only)",
    )
    parser.add_argument(
        "--chapters-only",
        action="store_true",
        help="Only include chapter headings (第N章)",
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=None,
        help="Only include entries starting from this page",
    )
    parser.add_argument(
        "--group-chapters",
        action="store_true",
        help="Group 'Section N.M' entries into chapters",
    )
    args = parser.parse_args()

    markdown = Path(args.input).read_text(encoding="utf-8")
    entries = extract_toc(markdown)
    last_page = get_last_page(markdown)

    # Filter by start page
    if args.start_page:
        entries = [e for e in entries if e.start_page >= args.start_page]

    if args.chapters_only:
        entries = find_chapters(entries)
    elif args.level:
        entries = filter_by_level(entries, args.level)

    # Recalculate end pages after filtering
    if entries:
        recalculate_end_pages(entries, last_page)

    # Group by chapter if requested
    output_data: list[TocEntry] | list[Chapter] = entries
    if args.group_chapters:
        output_data = group_by_chapter(entries)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(to_json(output_data))
        print(f"Saved TOC to {args.output}")
    else:
        print(to_json(output_data))
