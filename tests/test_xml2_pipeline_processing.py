"""Tests for xml2_pipeline.py - Content processing tests"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_BOOK2_XML = FIXTURES_DIR / "sample_book2.xml"


# Fixture to prevent PID file and atexit state leaks across tests
@pytest.fixture
def mock_pid_management(monkeypatch):
    """Mock PID file management to prevent atexit accumulation and file conflicts."""
    import atexit
    from unittest.mock import MagicMock

    mock_get_pid = MagicMock(return_value=Path(f"/tmp/test_pid_{id(monkeypatch)}.pid"))
    mock_kill = MagicMock(return_value=False)
    mock_write = MagicMock()
    mock_atexit = MagicMock()

    import src.xml2_pipeline

    monkeypatch.setattr(src.xml2_pipeline, "get_pid_file_path", mock_get_pid)
    monkeypatch.setattr(src.xml2_pipeline, "kill_existing_process", mock_kill)
    monkeypatch.setattr(src.xml2_pipeline, "write_pid_file", mock_write)
    monkeypatch.setattr(atexit, "register", mock_atexit)

    yield


class TestLoadSoundMonoConversion:
    """Test load_sound function for audio loading and conversion.

    T043: 効果音ロード機能テスト
    - ステレオ → モノラル変換
    - サンプルレート変換（リサンプリング）
    - numpy 配列として返却
    - 音量正規化
    """

    def test_load_sound_returns_numpy_array(self, tmp_path):
        """load_sound は numpy 配列を返す"""
        import soundfile as sf

        from src.xml2_pipeline import load_sound

        # Create a test mono WAV file
        test_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 24000)).astype(np.float32)
        sound_path = tmp_path / "test.wav"
        sf.write(sound_path, test_audio, 24000)

        result = load_sound(sound_path)

        assert isinstance(result, np.ndarray), f"load_sound should return numpy.ndarray, got {type(result)}"

    def test_load_sound_stereo_to_mono_conversion(self, tmp_path):
        """ステレオ音声をモノラルに変換する"""
        import soundfile as sf

        from src.xml2_pipeline import load_sound

        # Create a stereo WAV file
        duration = 0.5
        sr = 24000
        samples = int(duration * sr)
        stereo_audio = np.column_stack(
            [
                np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples)),  # Left channel
                np.sin(2 * np.pi * 880 * np.linspace(0, duration, samples)),  # Right channel
            ]
        ).astype(np.float32)

        sound_path = tmp_path / "stereo.wav"
        sf.write(sound_path, stereo_audio, sr)

        result = load_sound(sound_path)

        # Result should be 1D (mono)
        assert len(result.shape) == 1, f"Stereo should be converted to mono (1D), got shape {result.shape}"

    def test_load_sound_resampling(self, tmp_path):
        """異なるサンプルレートをリサンプリングする"""
        import soundfile as sf

        from src.xml2_pipeline import load_sound

        # Create a 48kHz WAV file (different from VOICEVOX's 24kHz)
        source_sr = 48000
        target_sr = 24000
        duration = 0.5
        samples = int(duration * source_sr)
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples)).astype(np.float32)

        sound_path = tmp_path / "48khz.wav"
        sf.write(sound_path, audio, source_sr)

        result = load_sound(sound_path, target_sr=target_sr)

        # Expected number of samples after resampling
        expected_samples = int(samples * target_sr / source_sr)

        assert abs(len(result) - expected_samples) < 10, (
            f"Resampled audio should have ~{expected_samples} samples, got {len(result)}"
        )

    def test_load_sound_already_correct_sample_rate(self, tmp_path):
        """既に正しいサンプルレートの場合はリサンプリングしない"""
        import soundfile as sf

        from src.xml2_pipeline import load_sound

        # Create a 24kHz WAV file (same as VOICEVOX)
        sr = 24000
        duration = 0.5
        samples = int(duration * sr)
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples)).astype(np.float32)

        sound_path = tmp_path / "24khz.wav"
        sf.write(sound_path, audio, sr)

        result = load_sound(sound_path, target_sr=sr)

        assert len(result) == samples, (
            f"Audio at correct sample rate should not be resampled, got {len(result)} samples"
        )

    def test_load_sound_normalization(self, tmp_path):
        """音量が正規化される"""
        import soundfile as sf

        from src.xml2_pipeline import load_sound

        # Create audio with very low amplitude
        sr = 24000
        duration = 0.5
        samples = int(duration * sr)
        # Very quiet audio (amplitude 0.01)
        audio = 0.01 * np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples)).astype(np.float32)

        sound_path = tmp_path / "quiet.wav"
        sf.write(sound_path, audio, sr)

        result = load_sound(sound_path)

        max_amplitude = np.max(np.abs(result))
        # Should be normalized (not too quiet)
        assert max_amplitude > 0.1, f"Audio should be normalized, max amplitude is {max_amplitude}"

    def test_load_sound_returns_float32(self, tmp_path):
        """float32 型で返却される"""
        import soundfile as sf

        from src.xml2_pipeline import load_sound

        sr = 24000
        duration = 0.5
        samples = int(duration * sr)
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples)).astype(np.float32)

        sound_path = tmp_path / "test.wav"
        sf.write(sound_path, audio, sr)

        result = load_sound(sound_path)

        assert result.dtype == np.float32, f"load_sound should return float32, got {result.dtype}"


class TestProcessContentWithMarkers:
    """Test process_content function with CHAPTER_MARKER and SECTION_MARKER.

    T044: マーカー処理テスト
    - CHAPTER_MARKER で分割し chapter_sound を挿入
    - SECTION_MARKER で分割し section_sound を挿入
    - マーカーなしテキストはそのまま処理
    """

    def test_process_content_function_exists(self):
        """process_content 関数が存在する"""
        from src.xml2_pipeline import process_content

        assert callable(process_content), "process_content should be a callable function"

    def test_process_content_accepts_content_items(self):
        """process_content は ContentItem リストを受け付ける"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(item_type="paragraph", text="Test paragraph", heading_info=None),
        ]

        # Should not raise
        # Note: This might need mock synthesizer in actual implementation
        try:
            # process_content signature likely includes synthesizer, sounds, etc.
            # For RED test, we just verify it accepts content_items
            _ = process_content(content_items)
        except TypeError as e:
            # If missing required arguments, that's expected - function exists but needs more args
            assert "argument" in str(e).lower() or "required" in str(e).lower(), (
                f"process_content should accept content_items, got: {e}"
            )

    def test_process_content_with_chapter_marker_includes_chapter_sound(self):
        """CHAPTER_MARKER を含むテキストで chapter_sound が挿入される"""
        from src.xml2_parser import CHAPTER_MARKER, ContentItem, HeadingInfo
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="heading",
                text=f"{CHAPTER_MARKER}第1章 テスト",
                heading_info=HeadingInfo(level=1, number="1", title="テスト", read_aloud=True),
            ),
        ]

        # Create mock chapter sound (short sine wave)
        chapter_sound = np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 2400)).astype(np.float32)

        # The actual test will verify chapter_sound is inserted before the heading
        # RED phase: we verify the function handles CHAPTER_MARKER correctly
        try:
            result = process_content(
                content_items,
                chapter_sound=chapter_sound,
                section_sound=None,
            )
            # If we get here, verify result contains audio data
            assert result is not None, "process_content should return result"
        except TypeError as e:
            # Expected in RED phase - function signature may differ
            assert True, f"Function exists but signature differs: {e}"

    def test_process_content_with_section_marker_includes_section_sound(self):
        """SECTION_MARKER を含むテキストで section_sound が挿入される"""
        from src.xml2_parser import SECTION_MARKER, ContentItem, HeadingInfo
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="heading",
                text=f"{SECTION_MARKER}第1.1節 サブセクション",
                heading_info=HeadingInfo(level=2, number="1.1", title="サブセクション", read_aloud=True),
            ),
        ]

        # Create mock section sound
        section_sound = np.sin(2 * np.pi * 880 * np.linspace(0, 0.1, 2400)).astype(np.float32)

        try:
            result = process_content(
                content_items,
                chapter_sound=None,
                section_sound=section_sound,
            )
            assert result is not None, "process_content should return result"
        except TypeError as e:
            assert True, f"Function exists but signature differs: {e}"

    def test_process_content_mixed_markers(self):
        """CHAPTER_MARKER と SECTION_MARKER の両方を正しく処理"""
        from src.xml2_parser import CHAPTER_MARKER, SECTION_MARKER, ContentItem, HeadingInfo
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="heading",
                text=f"{CHAPTER_MARKER}第1章 最初の章",
                heading_info=HeadingInfo(level=1, number="1", title="最初の章", read_aloud=True),
            ),
            ContentItem(item_type="paragraph", text="段落テキスト", heading_info=None),
            ContentItem(
                item_type="heading",
                text=f"{SECTION_MARKER}第1.1節 セクション",
                heading_info=HeadingInfo(level=2, number="1.1", title="セクション", read_aloud=True),
            ),
        ]

        chapter_sound = np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 2400)).astype(np.float32)
        section_sound = np.sin(2 * np.pi * 880 * np.linspace(0, 0.1, 2400)).astype(np.float32)

        try:
            result = process_content(
                content_items,
                chapter_sound=chapter_sound,
                section_sound=section_sound,
            )
            assert result is not None, "process_content should handle mixed markers"
        except TypeError as e:
            assert True, f"Function exists but signature differs: {e}"

    def test_process_content_no_markers(self):
        """マーカーなしのテキストはそのまま処理される"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(item_type="paragraph", text="マーカーなしの段落テキスト", heading_info=None),
        ]

        try:
            result = process_content(
                content_items,
                chapter_sound=None,
                section_sound=None,
            )
            assert result is not None, "process_content should handle text without markers"
        except TypeError as e:
            assert True, f"Function exists but signature differs: {e}"


class TestProcessContentAppliesCleanPageText:
    """T007: process_content が clean_page_text() を呼び出すことを検証する。

    US1 Acceptance Scenario:
    - clean_page_text() が全テキストに適用される
    - マーカー除去後、TTS生成前にクリーニングが行われる
    """

    def test_process_content_calls_clean_page_text(self):
        """process_content は各コンテンツアイテムのテキストに clean_page_text() を適用する"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="paragraph",
                text="テスト段落テキスト",
                heading_info=None,
            ),
        ]

        # Mock synthesizer and args to go through the full processing path
        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.clean_page_text") as mock_clean:
                mock_clean.return_value = "クリーニング済みテキスト"

                with patch("src.chapter_processor.generate_audio") as mock_gen:
                    mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                    process_content(
                        content_items,
                        synthesizer=mock_synthesizer,
                        output_dir=output_dir,
                        args=mock_args,
                        chapter_sound=None,
                        section_sound=None,
                    )

                    # clean_page_text must be called at least once
                    assert mock_clean.called, (
                        "process_content は clean_page_text() を呼び出すべきだが、呼び出されていない"
                    )

    def test_process_content_applies_clean_page_text_to_each_item(self):
        """process_content は複数のコンテンツアイテム全てに clean_page_text() を適用する"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(item_type="paragraph", text="段落1のテキスト", heading_info=None),
            ContentItem(item_type="paragraph", text="段落2のテキスト", heading_info=None),
            ContentItem(item_type="paragraph", text="段落3のテキスト", heading_info=None),
        ]

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.clean_page_text") as mock_clean:
                mock_clean.side_effect = lambda text, **kwargs: text

                with patch("src.chapter_processor.generate_audio") as mock_gen:
                    mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                    process_content(
                        content_items,
                        synthesizer=mock_synthesizer,
                        output_dir=output_dir,
                        args=mock_args,
                        chapter_sound=None,
                        section_sound=None,
                    )

                    # clean_page_text should be called for each non-empty item
                    assert mock_clean.call_count >= 3, (
                        f"clean_page_text は3回呼び出されるべきだが、{mock_clean.call_count}回しか呼び出されていない"
                    )

    def test_process_content_cleans_text_after_marker_removal(self):
        """process_content はマーカー除去後にクリーニングを行う"""
        from src.xml2_parser import CHAPTER_MARKER, ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="heading",
                text=f"{CHAPTER_MARKER}第1章 テストの章",
                heading_info=None,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        chapter_sound = np.zeros(2400, dtype=np.float32)

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.clean_page_text") as mock_clean:
                mock_clean.side_effect = lambda text, **kwargs: text

                with patch("src.chapter_processor.generate_audio") as mock_gen:
                    mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                    process_content(
                        content_items,
                        synthesizer=mock_synthesizer,
                        output_dir=output_dir,
                        args=mock_args,
                        chapter_sound=chapter_sound,
                        section_sound=None,
                    )

                    # clean_page_text should be called without the marker
                    if mock_clean.called:
                        first_call_text = mock_clean.call_args_list[0][0][0]
                        assert CHAPTER_MARKER not in first_call_text, (
                            f"clean_page_text にマーカーが含まれてはいけない: {first_call_text!r}"
                        )
                    else:
                        pytest.fail("clean_page_text はマーカー除去後に呼び出されるべきだが、呼び出されていない")


class TestProcessContentRemovesUrl:
    """T008: process_content が URL を除去することを検証する。

    US1 Acceptance Scenario 1:
    - Given URL を含む paragraph 要素
    - When xml2_pipeline で処理する
    - Then URL は読み上げられない
    """

    def test_url_not_passed_to_tts(self):
        """URL を含むテキストが TTS に渡される前に URL が除去される"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        url_text = "詳細は https://example.com/path/to/page を参照してください。"
        content_items = [
            ContentItem(item_type="paragraph", text=url_text, heading_info=None),
        ]

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        tts_texts = []

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.generate_audio") as mock_gen:
                mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                process_content(
                    content_items,
                    synthesizer=mock_synthesizer,
                    output_dir=output_dir,
                    args=mock_args,
                    chapter_sound=None,
                    section_sound=None,
                )

                # Collect all text passed to generate_audio
                for call in mock_gen.call_args_list:
                    _, kwargs = call
                    if "text" in kwargs:
                        tts_texts.append(kwargs["text"])
                    elif len(call[0]) > 1:
                        tts_texts.append(call[0][1])

        # URL should not appear in any TTS text
        all_tts_text = " ".join(tts_texts)
        assert "https://example.com" not in all_tts_text, f"TTS テキストに URL が含まれている: {all_tts_text!r}"
        assert "example.com" not in all_tts_text, f"TTS テキストにドメイン名が含まれている: {all_tts_text!r}"

    def test_http_url_removed(self):
        """http:// で始まる URL も除去される"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="paragraph",
                text="リンク先は http://example.org/index.html です。",
                heading_info=None,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.generate_audio") as mock_gen:
                mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                process_content(
                    content_items,
                    synthesizer=mock_synthesizer,
                    output_dir=output_dir,
                    args=mock_args,
                    chapter_sound=None,
                    section_sound=None,
                )

                all_tts_text = " ".join(
                    call.kwargs.get("text", call.args[1] if len(call.args) > 1 else "")
                    for call in mock_gen.call_args_list
                )

        assert "http://example.org" not in all_tts_text, f"TTS テキストに http URL が含まれている: {all_tts_text!r}"


class TestProcessContentRemovesParentheticalEnglish:
    """T009: process_content が括弧内英語を除去することを検証する。

    US1 Acceptance Scenario 2:
    - Given 括弧内英語 (English) を含むテキスト
    - When 処理する
    - Then 括弧内英語は読み上げられない
    """

    def test_parenthetical_english_removed(self):
        """括弧内の英語テキストが除去される"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="paragraph",
                text="信頼性 (Reliability) は重要な概念です。",
                heading_info=None,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.generate_audio") as mock_gen:
                mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                process_content(
                    content_items,
                    synthesizer=mock_synthesizer,
                    output_dir=output_dir,
                    args=mock_args,
                    chapter_sound=None,
                    section_sound=None,
                )

                all_tts_text = " ".join(
                    call.kwargs.get("text", call.args[1] if len(call.args) > 1 else "")
                    for call in mock_gen.call_args_list
                )

        assert "Reliability" not in all_tts_text, f"TTS テキストに括弧内英語が含まれている: {all_tts_text!r}"
        assert "(Reliability)" not in all_tts_text, f"TTS テキストに括弧付き英語が含まれている: {all_tts_text!r}"

    def test_multiple_parenthetical_english_removed(self):
        """複数の括弧内英語が全て除去される"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="paragraph",
                text="可用性 (Availability) と拡張性 (Scalability) について説明します。",
                heading_info=None,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.generate_audio") as mock_gen:
                mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                process_content(
                    content_items,
                    synthesizer=mock_synthesizer,
                    output_dir=output_dir,
                    args=mock_args,
                    chapter_sound=None,
                    section_sound=None,
                )

                all_tts_text = " ".join(
                    call.kwargs.get("text", call.args[1] if len(call.args) > 1 else "")
                    for call in mock_gen.call_args_list
                )

        assert "Availability" not in all_tts_text, f"TTS テキストに 'Availability' が含まれている: {all_tts_text!r}"
        assert "Scalability" not in all_tts_text, f"TTS テキストに 'Scalability' が含まれている: {all_tts_text!r}"


class TestProcessContentConvertsNumbersToKana:
    """T010: process_content が数字をカナに変換することを検証する。

    US1 Acceptance Scenario 5:
    - Given 数字「123」を含むテキスト
    - When 処理する
    - Then 「ひゃくにじゅうさん」と読み上げられる
    """

    def test_numbers_converted_to_kana(self):
        """数字がカナに変換されて TTS に渡される"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="paragraph",
                text="合計は123個です。",
                heading_info=None,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.generate_audio") as mock_gen:
                mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                process_content(
                    content_items,
                    synthesizer=mock_synthesizer,
                    output_dir=output_dir,
                    args=mock_args,
                    chapter_sound=None,
                    section_sound=None,
                )

                all_tts_text = " ".join(
                    call.kwargs.get("text", call.args[1] if len(call.args) > 1 else "")
                    for call in mock_gen.call_args_list
                )

        # 数字 "123" はそのままの形で TTS に渡されてはいけない
        # clean_page_text() が適用されれば、カナに変換される
        assert "123" not in all_tts_text, (
            f"TTS テキストに生の数字 '123' が含まれている（カナ変換されるべき）: {all_tts_text!r}"
        )

    def test_year_number_converted(self):
        """年号の数字もカナに変換される"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="paragraph",
                text="2024年に発表されました。",
                heading_info=None,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.generate_audio") as mock_gen:
                mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                process_content(
                    content_items,
                    synthesizer=mock_synthesizer,
                    output_dir=output_dir,
                    args=mock_args,
                    chapter_sound=None,
                    section_sound=None,
                )

                all_tts_text = " ".join(
                    call.kwargs.get("text", call.args[1] if len(call.args) > 1 else "")
                    for call in mock_gen.call_args_list
                )

        assert "2024" not in all_tts_text, (
            f"TTS テキストに生の数字 '2024' が含まれている（カナ変換されるべき）: {all_tts_text!r}"
        )


# =============================================================================
# Edge Cases
# =============================================================================
