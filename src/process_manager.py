"""PID file management for xml2_pipeline processes.

This module provides PID file handling functionality to ensure
only one instance of xml2_pipeline runs per input file.
"""

import logging
import os
import signal
from pathlib import Path

logger = logging.getLogger(__name__)


def get_pid_file_path(input_file: str) -> Path:
    """Get PID file path for the given input file.

    Args:
        input_file: Input XML file path

    Returns:
        Path to PID file
    """
    # Create tmp/pids directory (Rails-style)
    pid_dir = Path("tmp/pids")
    pid_dir.mkdir(parents=True, exist_ok=True)

    # Use input filename as PID file name
    input_name = Path(input_file).stem
    return pid_dir / f"xml2_pipeline_{input_name}.pid"


def kill_existing_process(pid_file: Path) -> bool:
    """Kill existing process using PID file.

    Args:
        pid_file: Path to PID file

    Returns:
        True if a process was killed, False otherwise
    """
    if not pid_file.exists():
        return False

    try:
        with open(pid_file, "r") as f:
            old_pid = int(f.read().strip())

        # Check if process exists and kill it
        try:
            os.kill(old_pid, signal.SIGTERM)
            logger.warning(f"Killed existing process PID {old_pid}")
            # Wait a bit for process to terminate
            import time

            time.sleep(0.5)
            # Force kill if still alive
            try:
                os.kill(old_pid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # Already dead
            return True
        except ProcessLookupError:
            # Process already dead, just remove stale PID file
            logger.debug(f"Stale PID file found (PID {old_pid} not running)")
            pid_file.unlink()
            return False
    except (ValueError, IOError) as e:
        logger.warning(f"Failed to read PID file: {e}")
        pid_file.unlink()
        return False


def write_pid_file(pid_file: Path) -> None:
    """Write current process PID to file.

    Args:
        pid_file: Path to PID file
    """
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))


def cleanup_pid_file(pid_file: Path) -> None:
    """Remove PID file on exit.

    Args:
        pid_file: Path to PID file
    """
    if pid_file.exists():
        pid_file.unlink()
