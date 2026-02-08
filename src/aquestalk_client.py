"""AquesTalk10 TTS client for audio synthesis.

This module provides a mock implementation of AquesTalk10 synthesizer.
AquesTalk10 library is not actually available, so we generate dummy 16kHz WAV data.

AquesTalk10 specifications:
- Sample rate: 16000Hz
- Parameters: speed (50-300), voice (0-200), pitch (50-200)
- Number tag: <NUM VAL=123> for natural number reading
- Punctuation: 。、？！ for pauses
"""

import io
import logging
import re
from dataclasses import dataclass

import numpy as np
import soundfile as sf

logger = logging.getLogger(__name__)

# AquesTalk10 sample rate
AQUESTALK_SAMPLE_RATE = 16000


@dataclass
class AquesTalkConfig:
    """AquesTalk10 configuration."""

    speed: int = 100  # 50-300
    voice: int = 100  # 0-200
    pitch: int = 100  # 50-200


class AquesTalkSynthesizer:
    """AquesTalk10 synthesizer (mock implementation).

    Since AquesTalk10 library is not available, this generates dummy audio.
    """

    def __init__(self, config: AquesTalkConfig | None = None):
        """Initialize synthesizer.

        Args:
            config: AquesTalk configuration. If None, uses default values.
        """
        self.config = config or AquesTalkConfig()
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the synthesizer.

        In real implementation, this would load AquesTalk10 library.

        Raises:
            ValueError: If config parameters are out of valid range
        """
        if self._initialized:
            return

        # Validate config parameters
        self._validate_parameters(
            self.config.speed,
            self.config.voice,
            self.config.pitch
        )

        logger.info("Initializing AquesTalk10 synthesizer (mock)...")
        logger.info(
            "Config: speed=%d, voice=%d, pitch=%d",
            self.config.speed,
            self.config.voice,
            self.config.pitch,
        )
        self._initialized = True

    def synthesize(
        self,
        text: str,
        speed: int | None = None,
        voice: int | None = None,
        pitch: int | None = None,
    ) -> bytes:
        """Synthesize text to audio.

        Args:
            text: Text to synthesize (can include AquesTalk tags like <NUM VAL=123>)
            speed: Override speed (50-300, default: use config.speed)
            voice: Override voice quality (0-200, default: use config.voice)
            pitch: Override pitch (50-200, default: use config.pitch)

        Returns:
            WAV audio data as bytes (16kHz, mono)

        Raises:
            ValueError: If any parameter is out of valid range
        """
        self.initialize()

        # Use provided values or fall back to config
        actual_speed = speed if speed is not None else self.config.speed
        actual_voice = voice if voice is not None else self.config.voice
        actual_pitch = pitch if pitch is not None else self.config.pitch

        # Validate parameters
        self._validate_parameters(actual_speed, actual_voice, actual_pitch)

        # Generate dummy audio (16kHz sine wave)
        # Length based on text length (rough approximation)
        duration = max(0.5, len(text) * 0.1)  # seconds
        num_samples = int(AQUESTALK_SAMPLE_RATE * duration)

        # Generate simple sine wave as dummy audio
        frequency = 440.0  # A4 note
        t = np.linspace(0, duration, num_samples, False)
        waveform = 0.3 * np.sin(2 * np.pi * frequency * t)

        # Convert to WAV bytes
        with io.BytesIO() as buffer:
            sf.write(buffer, waveform, AQUESTALK_SAMPLE_RATE, format="WAV")
            return buffer.getvalue()

    def _validate_parameters(
        self,
        speed: int,
        voice: int,
        pitch: int
    ) -> None:
        """Validate AquesTalk10 parameters.

        Args:
            speed: Speech speed (50-300)
            voice: Voice quality (0-200)
            pitch: Pitch (50-200)

        Raises:
            ValueError: If any parameter is out of valid range
        """
        if not (50 <= speed <= 300):
            raise ValueError(f"speed must be 50-300, got {speed}")
        if not (0 <= voice <= 200):
            raise ValueError(f"voice must be 0-200, got {voice}")
        if not (50 <= pitch <= 200):
            raise ValueError(f"pitch must be 50-200, got {pitch}")


def convert_numbers_to_num_tags(text: str) -> str:
    """Convert numbers to AquesTalk <NUM VAL=N> tags.

    Args:
        text: Input text with numbers

    Returns:
        Text with numbers replaced by <NUM VAL=N> tags

    Example:
        "価格は1000円です" -> "価格は<NUM VAL=1000>円です"
    """
    # Convert only integers (not decimals)
    # Strategy: First protect decimal numbers, then convert integers

    # Find all decimal numbers and replace with placeholders
    decimal_pattern = r'\d+\.\d+'
    decimals = re.findall(decimal_pattern, text)
    placeholders = {}
    for i, decimal in enumerate(decimals):
        # Use a placeholder that won't be matched by \d+
        placeholder = f"__DECIMAL_PROTECTED_{chr(ord('A') + i)}__"
        placeholders[placeholder] = decimal
        text = text.replace(decimal, placeholder, 1)

    # Now convert remaining integers to NUM tags
    integer_pattern = r'\d+'
    text = re.sub(integer_pattern, r'<NUM VAL=\g<0>>', text)

    # Restore decimal numbers
    for placeholder, decimal in placeholders.items():
        text = text.replace(placeholder, decimal)

    return text


def add_punctuation(text: str, is_heading: bool) -> str:
    """Add punctuation to end of text if missing.

    Adds 。 to heading/paragraph end if it doesn't already end with
    a sentence-ending punctuation mark (。！？).

    Avoids duplicate punctuation like 。。

    Args:
        text: Input text
        is_heading: True if this is a heading, False for paragraph

    Returns:
        Text with punctuation added if needed

    Example:
        "第1章 はじめに" -> "第1章 はじめに。"
        "すばらしい！" -> "すばらしい！" (no change)
    """
    if not text or not text.strip():
        return text

    # Check if text already ends with sentence-ending punctuation
    # Support both full-width and half-width
    ending_marks = ["。", "！", "？", "!", "?"]
    if any(text.rstrip().endswith(mark) for mark in ending_marks):
        return text

    # Add 。 to the end
    return text.rstrip() + "。"
