"""GPU memory management for ollama and voicevox coordination.

This module provides utilities to manage GPU memory between ollama (LLM) and
voicevox (TTS) to prevent CUDA out of memory errors.
"""

from __future__ import annotations

import logging
import subprocess
import time

import requests

logger = logging.getLogger(__name__)

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_REQUIRED_GPU_MB = 2000
DEFAULT_UNLOAD_WAIT_SECONDS = 2


def get_gpu_memory_usage() -> tuple[int, int]:
    """Get GPU memory usage.

    Returns:
        Tuple of (used_mb, total_mb). Returns (0, 0) if nvidia-smi is unavailable.
    """
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        # Parse first GPU's memory (in case of multi-GPU)
        first_line = result.stdout.strip().split("\n")[0]
        used, total = map(int, first_line.split(", "))
        return used, total
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
        logger.warning("Failed to get GPU memory usage: %s", e)
        return 0, 0


def is_gpu_memory_available(required_mb: int = DEFAULT_REQUIRED_GPU_MB) -> bool:
    """Check if required GPU memory is available.

    Args:
        required_mb: Required free memory in MB (default: 2000 MB)

    Returns:
        True if enough memory is available, False otherwise.
    """
    used, total = get_gpu_memory_usage()
    if total == 0:
        # nvidia-smi not available, assume GPU is available
        logger.info("GPU memory info unavailable, assuming GPU is available")
        return True

    available = total - used
    is_available = available >= required_mb
    logger.info(
        "GPU memory: %d/%d MB used, %d MB available (required: %d MB) -> %s",
        used,
        total,
        available,
        required_mb,
        "OK" if is_available else "INSUFFICIENT",
    )
    return is_available


def unload_ollama_model(
    model: str,
    base_url: str = DEFAULT_OLLAMA_BASE_URL,
    timeout: int = 30,
) -> bool:
    """Unload ollama model to free GPU memory.

    Uses ollama API with keep_alive=0 to immediately unload the model.

    Args:
        model: Model name to unload (e.g., "gemma3:27b", "gpt-oss:20b")
        base_url: Ollama API base URL
        timeout: Request timeout in seconds

    Returns:
        True if unload was successful, False otherwise.
    """
    try:
        logger.info("Unloading ollama model: %s", model)
        response = requests.post(
            f"{base_url}/api/generate",
            json={"model": model, "keep_alive": 0},
            timeout=timeout,
        )
        response.raise_for_status()
        logger.info("Successfully unloaded ollama model: %s", model)
        return True
    except requests.RequestException as e:
        logger.warning("Failed to unload ollama model %s: %s", model, e)
        return False


def wait_for_gpu_memory(
    required_mb: int = DEFAULT_REQUIRED_GPU_MB,
    max_wait_seconds: int = 30,
    check_interval: float = 1.0,
) -> bool:
    """Wait for GPU memory to become available.

    Args:
        required_mb: Required free memory in MB
        max_wait_seconds: Maximum time to wait
        check_interval: Time between checks in seconds

    Returns:
        True if memory became available, False if timed out.
    """
    start_time = time.time()
    while time.time() - start_time < max_wait_seconds:
        if is_gpu_memory_available(required_mb):
            return True
        logger.info("Waiting for GPU memory to be freed...")
        time.sleep(check_interval)

    logger.warning(
        "Timed out waiting for GPU memory (required: %d MB, waited: %d sec)",
        required_mb,
        max_wait_seconds,
    )
    return False


def release_gpu_for_voicevox(
    ollama_model: str | None = None,
    required_mb: int = DEFAULT_REQUIRED_GPU_MB,
    base_url: str = DEFAULT_OLLAMA_BASE_URL,
    wait_seconds: int = DEFAULT_UNLOAD_WAIT_SECONDS,
) -> bool:
    """Release GPU memory for voicevox by unloading ollama model.

    This is a convenience function that combines unloading ollama model
    and waiting for GPU memory.

    Args:
        ollama_model: Model to unload. If None, skips unloading.
        required_mb: Required free memory in MB for voicevox
        base_url: Ollama API base URL
        wait_seconds: Seconds to wait after unloading

    Returns:
        True if GPU memory is available after release, False otherwise.
    """
    # Check if already have enough memory
    if is_gpu_memory_available(required_mb):
        logger.info("GPU memory already available, skipping ollama unload")
        return True

    # Unload ollama model if specified
    if ollama_model:
        unload_ollama_model(ollama_model, base_url)
        # Wait for memory to be freed
        time.sleep(wait_seconds)

    # Check again
    return is_gpu_memory_available(required_mb)
