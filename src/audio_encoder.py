"""MP3エンコードユーティリティモジュール.

numpy 配列の波形データを MP3 ファイルとして保存する機能を提供する。
内部的に pydub (ffmpeg wrapper) を使用してエンコードを行う。
"""

import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_MP3_BITRATE = "128k"


def save_as_mp3(
    waveform: np.ndarray,
    sample_rate: int,
    output_path: Path,
    bitrate: str = DEFAULT_MP3_BITRATE,
) -> None:
    """波形データを MP3 ファイルとして保存する.

    Args:
        waveform: float32 の波形データ（-1.0 〜 1.0）
        sample_rate: サンプルレート (Hz)
        output_path: 出力先パス（.mp3 拡張子推奨）
        bitrate: MP3 ビットレート（例: "128k", "192k", "256k"）

    Raises:
        ImportError: pydub がインストールされていない場合
        RuntimeError: ffmpeg が見つからない場合
    """
    from pydub import AudioSegment

    # float32 → int16 に変換（クリッピング付き）
    clipped = np.clip(waveform, -1.0, 1.0)
    int16_data = (clipped * 32767).astype(np.int16)

    # AudioSegment を生データから構築
    audio = AudioSegment(
        data=int16_data.tobytes(),
        sample_width=2,  # 16-bit
        frame_rate=sample_rate,
        channels=1,  # mono
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audio.export(str(output_path), format="mp3", bitrate=bitrate)
    logger.info("Saved MP3: %s (bitrate=%s)", output_path, bitrate)
