"""Progress tracking with real-time ETA calculation."""

import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ChunkInfo:
    """Info about a single chunk for progress tracking."""

    page_num: int
    chunk_idx: int
    char_count: int


@dataclass
class ProgressTracker:
    """Track progress and calculate real-time ETA based on processing speed."""

    chunks: list[ChunkInfo]
    total_pages: int
    _start_time: float = field(default=0.0, init=False)
    _processed_chunks: int = field(default=0, init=False)
    _processed_chars: int = field(default=0, init=False)
    _completed_pages: int = field(default=0, init=False)

    @property
    def total_chunks(self) -> int:
        return len(self.chunks)

    @property
    def total_chars(self) -> int:
        return sum(c.char_count for c in self.chunks)

    @property
    def remaining_chars(self) -> int:
        return sum(c.char_count for c in self.chunks[self._processed_chunks :])

    def start(self) -> None:
        """Start the progress timer."""
        self._start_time = time.time()
        logger.info(
            "[Progress] Starting: %d pages, %d chunks, %d chars total",
            self.total_pages,
            self.total_chunks,
            self.total_chars,
        )

    def on_chunk_done(self, chunk: ChunkInfo, chunk_time: float) -> None:
        """Called when a chunk is processed."""
        self._processed_chunks += 1
        self._processed_chars += chunk.char_count

        elapsed = time.time() - self._start_time
        chars_per_sec = self._processed_chars / elapsed if elapsed > 0 else 0
        eta_seconds = self.remaining_chars / chars_per_sec if chars_per_sec > 0 else 0

        # _completed_pages is the count of fully done pages, so current page is +1
        current_page_idx = self._completed_pages + 1
        logger.info(
            "[Progress] Chunk %d/%d | Page %d/%d | Elapsed: %s | ETA: %s | Speed: %.0f chars/s",
            self._processed_chunks,
            self.total_chunks,
            current_page_idx,
            self.total_pages,
            self._format_time(elapsed),
            self._format_time(eta_seconds),
            chars_per_sec,
        )

    def on_page_done(self, page_num: int, page_time: float) -> None:
        """Called when a page is fully processed."""
        self._completed_pages += 1
        elapsed = time.time() - self._start_time
        chars_per_sec = self._processed_chars / elapsed if elapsed > 0 else 0
        eta_seconds = self.remaining_chars / chars_per_sec if chars_per_sec > 0 else 0

        logger.info(
            "[Progress] Page %d/%d done (%.1fs) | Elapsed: %s | ETA: %s",
            self._completed_pages,
            self.total_pages,
            page_time,
            self._format_time(elapsed),
            self._format_time(eta_seconds),
        )

    def finish(self) -> None:
        """Called when all processing is complete."""
        elapsed = time.time() - self._start_time
        avg_chars_per_sec = self._processed_chars / elapsed if elapsed > 0 else 0
        logger.info(
            "[Progress] Complete! %d pages in %s (avg %.0f chars/s)",
            self._completed_pages,
            self._format_time(elapsed),
            avg_chars_per_sec,
        )

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds as 'Xh Ym Zs' or 'Ym Zs' or 'Zs'."""
        if seconds < 0:
            return "0s"
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        if minutes > 0:
            return f"{minutes}m {secs}s"
        return f"{secs}s"
