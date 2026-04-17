"""Tests for audio_encoder.py - MP3 encoding utility."""

from pathlib import Path

import numpy as np

from src.audio_encoder import save_as_mp3


class TestSaveAsMp3:
    """save_as_mp3() のテスト."""

    def test_creates_mp3_file(self, tmp_path: Path) -> None:
        """MP3 ファイルが生成される."""
        waveform = np.zeros(24000, dtype=np.float32)
        output = tmp_path / "test.mp3"
        save_as_mp3(waveform, 24000, output)
        assert output.exists()
        assert output.stat().st_size > 0

    def test_mp3_smaller_than_wav(self, tmp_path: Path) -> None:
        """MP3 は WAV より小さい."""
        import soundfile as sf

        waveform = np.random.randn(24000 * 10).astype(np.float32) * 0.5
        sr = 24000

        wav_path = tmp_path / "test.wav"
        mp3_path = tmp_path / "test.mp3"

        sf.write(str(wav_path), waveform, sr, subtype="PCM_16")
        save_as_mp3(waveform, sr, mp3_path)

        assert mp3_path.stat().st_size < wav_path.stat().st_size

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """親ディレクトリが自動作成される."""
        waveform = np.zeros(2400, dtype=np.float32)
        output = tmp_path / "a" / "b" / "test.mp3"
        save_as_mp3(waveform, 24000, output)
        assert output.exists()

    def test_custom_bitrate(self, tmp_path: Path) -> None:
        """ビットレート指定で生成できる."""
        waveform = np.zeros(24000, dtype=np.float32)
        output = tmp_path / "test.mp3"
        save_as_mp3(waveform, 24000, output, bitrate="64k")
        assert output.exists()

    def test_clipping_preserves_range(self, tmp_path: Path) -> None:
        """範囲外の値がクリッピングされる."""
        waveform = np.array([2.0, -2.0, 0.5], dtype=np.float32)
        output = tmp_path / "test.mp3"
        save_as_mp3(waveform, 24000, output)
        assert output.exists()

    def test_string_path_accepted(self, tmp_path: Path) -> None:
        """文字列パスも受け付ける."""
        waveform = np.zeros(2400, dtype=np.float32)
        output = tmp_path / "test.mp3"
        save_as_mp3(waveform, 24000, output)
        assert output.exists()
