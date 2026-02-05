"""Generate speech audio using Qwen3-TTS."""

import logging
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel

logger = logging.getLogger(__name__)


def load_model(
    model_name: str,
    device: str = "cuda:0",
    dtype: str = "bfloat16",
) -> Qwen3TTSModel:
    """Load the Qwen3-TTS model."""
    dtype_map = {
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }
    torch_dtype = dtype_map.get(dtype, torch.bfloat16)

    logger.info("Loading model: %s on %s (%s)", model_name, device, dtype)
    model = Qwen3TTSModel.from_pretrained(
        model_name,
        device_map=device,
        dtype=torch_dtype,
    )
    logger.info("Model loaded successfully")
    return model


def generate_audio(
    model: Qwen3TTSModel,
    text: str,
    language: str = "Japanese",
    speaker: str = "Ono_Anna",
    instruct: str = "",
) -> tuple[np.ndarray, int]:
    """Generate audio for a text chunk.

    Returns (waveform, sample_rate).
    """
    kwargs = {
        "text": text,
        "language": language,
        "speaker": speaker,
    }
    if instruct:
        kwargs["instruct"] = instruct

    wavs, sr = model.generate_custom_voice(**kwargs)
    return wavs[0], sr


def normalize_audio(waveform: np.ndarray, target_peak: float = 0.9) -> np.ndarray:
    """Normalize audio to target peak level.

    Args:
        waveform: Input audio waveform
        target_peak: Target peak amplitude (0.0-1.0)

    Returns:
        Normalized waveform
    """
    current_peak = np.abs(waveform).max()
    if current_peak > 0:
        return waveform * (target_peak / current_peak)
    return waveform


def save_audio(waveform: np.ndarray, sample_rate: int, output_path: Path) -> None:
    """Save waveform to a WAV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output_path), waveform, sample_rate)
    logger.info("Saved: %s", output_path)


def concatenate_audio_files(wav_files: list[Path], output_path: Path) -> None:
    """Concatenate multiple WAV files into a single file."""
    if not wav_files:
        logger.warning("No WAV files to concatenate")
        return

    all_audio = []
    sample_rate = None

    for wav_file in sorted(wav_files):
        data, sr = sf.read(str(wav_file))
        if sample_rate is None:
            sample_rate = sr
        elif sr != sample_rate:
            logger.warning(
                "Sample rate mismatch: %s has %d, expected %d",
                wav_file,
                sr,
                sample_rate,
            )
        all_audio.append(data)

        # Add 0.5s silence between pages
        silence = np.zeros(int(sample_rate * 0.5))
        all_audio.append(silence)

    combined = np.concatenate(all_audio)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output_path), combined, sample_rate)
    logger.info("Saved combined audio: %s", output_path)
