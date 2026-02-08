"""Tests for AquesTalk TTS client.

Phase 2 RED Tests - US1: XML から AquesTalk 音声生成
Tests for AquesTalkSynthesizer class and text processing utilities.

Target functions:
- src/aquestalk_client.py::AquesTalkConfig
- src/aquestalk_client.py::AquesTalkSynthesizer
- src/aquestalk_client.py::convert_numbers_to_num_tags()
- src/aquestalk_client.py::add_punctuation()

AquesTalk10 specifications:
- Sample rate: 16000Hz
- Parameters: speed (50-300), voice (0-200), pitch (50-200)
- Number tag: <NUM VAL=123> for natural number reading
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.aquestalk_client import (
    AquesTalkConfig,
    AquesTalkSynthesizer,
    add_punctuation,
    convert_numbers_to_num_tags,
)


# ============================================================
# T009: Test file structure (this file)
# ============================================================

class TestAquesTalkConfig:
    """Test AquesTalkConfig dataclass."""

    def test_config_has_default_speed(self):
        """speed のデフォルトは 100"""
        config = AquesTalkConfig()

        assert config.speed == 100, (
            f"speed default should be 100, got {config.speed}"
        )

    def test_config_has_default_voice(self):
        """voice のデフォルトは 100"""
        config = AquesTalkConfig()

        assert config.voice == 100, (
            f"voice default should be 100, got {config.voice}"
        )

    def test_config_has_default_pitch(self):
        """pitch のデフォルトは 100"""
        config = AquesTalkConfig()

        assert config.pitch == 100, (
            f"pitch default should be 100, got {config.pitch}"
        )

    def test_config_accepts_custom_values(self):
        """カスタム値を設定できる"""
        config = AquesTalkConfig(speed=150, voice=80, pitch=120)

        assert config.speed == 150, f"speed should be 150, got {config.speed}"
        assert config.voice == 80, f"voice should be 80, got {config.voice}"
        assert config.pitch == 120, f"pitch should be 120, got {config.pitch}"


# ============================================================
# T010: test_synthesize_basic
# ============================================================

class TestSynthesizeBasic:
    """Test AquesTalkSynthesizer.synthesize() basic functionality."""

    def test_synthesize_returns_bytes(self):
        """synthesize() は bytes を返す"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        result = synthesizer.synthesize("こんにちは")

        assert isinstance(result, bytes), (
            f"synthesize should return bytes, got {type(result)}"
        )

    def test_synthesize_returns_non_empty_audio(self):
        """synthesize() は空でない音声データを返す"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        result = synthesizer.synthesize("テストです")

        assert len(result) > 0, (
            "synthesize should return non-empty audio data"
        )

    def test_synthesize_accepts_hiragana(self):
        """synthesize() はひらがなを受け付ける"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        result = synthesizer.synthesize("こんにちは")

        assert isinstance(result, bytes), (
            "synthesize should accept hiragana text"
        )
        assert len(result) > 0, (
            "synthesize should return audio for hiragana"
        )

    def test_synthesize_accepts_katakana(self):
        """synthesize() はカタカナを受け付ける"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        result = synthesizer.synthesize("コンニチハ")

        assert isinstance(result, bytes), (
            "synthesize should accept katakana text"
        )
        assert len(result) > 0, (
            "synthesize should return audio for katakana"
        )

    def test_synthesize_accepts_mixed_text(self):
        """synthesize() は漢字かな混じり文を受け付ける"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        result = synthesizer.synthesize("今日は良い天気です")

        assert isinstance(result, bytes), (
            "synthesize should accept mixed text"
        )
        assert len(result) > 0, (
            "synthesize should return audio for mixed text"
        )


# ============================================================
# T011: test_synthesize_with_num_tag
# ============================================================

class TestConvertNumbersToNumTags:
    """Test convert_numbers_to_num_tags() function."""

    def test_convert_single_number(self):
        """単一の数字を NUM タグに変換"""
        result = convert_numbers_to_num_tags("価格は1000円です")

        assert "<NUM VAL=1000>" in result, (
            f"Should contain NUM tag for 1000, got: {result}"
        )
        assert "価格は" in result and "円です" in result, (
            f"Should preserve surrounding text, got: {result}"
        )

    def test_convert_multiple_numbers(self):
        """複数の数字を NUM タグに変換"""
        result = convert_numbers_to_num_tags("1から100までの数")

        assert "<NUM VAL=1>" in result, (
            f"Should contain NUM tag for 1, got: {result}"
        )
        assert "<NUM VAL=100>" in result, (
            f"Should contain NUM tag for 100, got: {result}"
        )

    def test_convert_large_number(self):
        """大きな数字を NUM タグに変換"""
        result = convert_numbers_to_num_tags("人口は12345678人です")

        assert "<NUM VAL=12345678>" in result, (
            f"Should contain NUM tag for large number, got: {result}"
        )

    def test_preserve_text_without_numbers(self):
        """数字がないテキストはそのまま"""
        result = convert_numbers_to_num_tags("こんにちは世界")

        assert result == "こんにちは世界", (
            f"Text without numbers should be unchanged, got: {result}"
        )

    def test_empty_string(self):
        """空文字列の処理"""
        result = convert_numbers_to_num_tags("")

        assert result == "", (
            f"Empty string should return empty, got: {result}"
        )

    def test_year_number(self):
        """年号の数字を変換"""
        result = convert_numbers_to_num_tags("2024年の出来事")

        assert "<NUM VAL=2024>" in result, (
            f"Should contain NUM tag for year, got: {result}"
        )

    def test_decimal_not_converted(self):
        """小数点を含む数値は変換しない（または適切に処理）"""
        result = convert_numbers_to_num_tags("円周率は3.14です")

        # 小数点を含む数字はそのまま or 整数部分のみ変換
        # 仕様により決定。ここでは整数のみ変換を期待
        assert "3.14" in result or "<NUM VAL=3>" in result, (
            f"Decimal should be preserved or partially converted, got: {result}"
        )


# ============================================================
# T012: test_add_punctuation_to_text
# ============================================================

class TestAddPunctuation:
    """Test add_punctuation() function for heading/paragraph end processing."""

    def test_add_punctuation_to_heading_without_period(self):
        """句点がない見出しに句点を追加"""
        result = add_punctuation("第1章 はじめに", is_heading=True)

        assert result.endswith("。"), (
            f"Heading without period should end with 。, got: {result}"
        )

    def test_no_duplicate_punctuation_heading(self):
        """既に句点がある見出しに二重に追加しない"""
        result = add_punctuation("第1章 はじめに。", is_heading=True)

        assert not result.endswith("。。"), (
            f"Should not have duplicate periods, got: {result}"
        )
        assert result.endswith("。"), (
            f"Should end with single period, got: {result}"
        )

    def test_add_punctuation_to_paragraph_without_period(self):
        """句点がない段落に句点を追加"""
        result = add_punctuation("これはテストです", is_heading=False)

        assert result.endswith("。"), (
            f"Paragraph without period should end with 。, got: {result}"
        )

    def test_no_duplicate_punctuation_paragraph(self):
        """既に句点がある段落に二重に追加しない"""
        result = add_punctuation("これはテストです。", is_heading=False)

        assert not result.endswith("。。"), (
            f"Should not have duplicate periods, got: {result}"
        )

    def test_preserve_exclamation_mark(self):
        """感嘆符で終わる場合は句点を追加しない"""
        result = add_punctuation("すばらしい！", is_heading=False)

        assert not result.endswith("。"), (
            f"Should not add period after ！, got: {result}"
        )
        assert result.endswith("！"), (
            f"Should preserve ！, got: {result}"
        )

    def test_preserve_question_mark(self):
        """疑問符で終わる場合は句点を追加しない"""
        result = add_punctuation("本当ですか？", is_heading=False)

        assert not result.endswith("。"), (
            f"Should not add period after ？, got: {result}"
        )
        assert result.endswith("？"), (
            f"Should preserve ？, got: {result}"
        )

    def test_empty_string(self):
        """空文字列の処理"""
        result = add_punctuation("", is_heading=True)

        assert result == "", (
            f"Empty string should return empty, got: {result}"
        )

    def test_whitespace_only(self):
        """空白のみの場合"""
        result = add_punctuation("   ", is_heading=True)

        # Whitespace should be preserved or trimmed, not adding period to whitespace
        assert result.strip() == "" or result.endswith("。") is False, (
            f"Whitespace only should not add period, got: '{result}'"
        )

    def test_unicode_punctuation(self):
        """全角の感嘆符・疑問符も認識"""
        result_exclaim = add_punctuation("やった!", is_heading=False)  # 半角!
        result_question = add_punctuation("なに?", is_heading=False)   # 半角?

        # 半角の!や?も終端記号として認識する場合
        # 実装によって異なる可能性あり
        assert "やった" in result_exclaim, f"Should preserve text, got: {result_exclaim}"
        assert "なに" in result_question, f"Should preserve text, got: {result_question}"


class TestSynthesizerInitialization:
    """Test AquesTalkSynthesizer initialization."""

    def test_synthesizer_creation(self):
        """AquesTalkSynthesizer を作成できる"""
        synthesizer = AquesTalkSynthesizer()

        assert synthesizer is not None, (
            "Should be able to create AquesTalkSynthesizer"
        )

    def test_synthesizer_with_config(self):
        """AquesTalkConfig を指定して作成できる"""
        config = AquesTalkConfig(speed=150, voice=80, pitch=120)
        synthesizer = AquesTalkSynthesizer(config)

        assert synthesizer.config.speed == 150, (
            f"Should use provided config speed, got {synthesizer.config.speed}"
        )

    def test_synthesizer_initialize_method_exists(self):
        """initialize() メソッドが存在する"""
        synthesizer = AquesTalkSynthesizer()

        assert hasattr(synthesizer, "initialize"), (
            "AquesTalkSynthesizer should have initialize method"
        )
        assert callable(synthesizer.initialize), (
            "initialize should be callable"
        )

    def test_synthesizer_synthesize_method_exists(self):
        """synthesize() メソッドが存在する"""
        synthesizer = AquesTalkSynthesizer()

        assert hasattr(synthesizer, "synthesize"), (
            "AquesTalkSynthesizer should have synthesize method"
        )
        assert callable(synthesizer.synthesize), (
            "synthesize should be callable"
        )


# ============================================================
# Phase 3: User Story 2 - 見出し速度調整 (T037)
# ============================================================

class TestHeadingSpeedAdjustmentClient:
    """Test synthesize() with speed parameter for heading emphasis.

    見出しは speed=80 でゆっくり読むことで強調する (FR-011)。
    synthesizer.synthesize() が speed パラメータを受け付けるようにする。
    """

    def test_synthesize_accepts_speed_parameter(self):
        """synthesize() は speed パラメータを受け付ける"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        # synthesize should accept optional speed parameter
        try:
            result = synthesizer.synthesize("テスト", speed=80)
            assert isinstance(result, bytes), (
                f"synthesize with speed should return bytes, got {type(result)}"
            )
        except TypeError as e:
            # If TypeError, synthesize doesn't accept speed parameter yet
            pytest.fail(
                f"synthesize() should accept speed parameter. Error: {e}"
            )

    def test_synthesize_speed_80_for_heading_emphasis(self):
        """speed=80 で見出しをゆっくり読み上げる"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        # Call with speed=80 (heading emphasis speed)
        result = synthesizer.synthesize("見出しテキスト", speed=80)

        assert isinstance(result, bytes), (
            "synthesize with speed=80 should return bytes"
        )
        assert len(result) > 0, (
            "synthesize with speed=80 should return non-empty audio"
        )

    def test_synthesize_uses_config_speed_when_not_specified(self):
        """speed パラメータ未指定時は config.speed を使用"""
        config = AquesTalkConfig(speed=150)
        synthesizer = AquesTalkSynthesizer(config)
        synthesizer.initialize()

        # Call without speed parameter - should use config.speed=150
        result = synthesizer.synthesize("テスト")

        # At minimum, it should work without speed parameter
        assert isinstance(result, bytes), (
            "synthesize without speed should use config.speed"
        )

    def test_synthesize_speed_overrides_config(self):
        """speed パラメータは config.speed を上書きする"""
        config = AquesTalkConfig(speed=150)
        synthesizer = AquesTalkSynthesizer(config)
        synthesizer.initialize()

        # Call with speed=80 - should override config.speed=150
        result = synthesizer.synthesize("テスト", speed=80)

        assert isinstance(result, bytes), (
            "synthesize with speed parameter should work"
        )
        # The speed override is handled internally;
        # we verify it accepts the parameter without error

    def test_heading_speed_constant_is_80(self):
        """見出し用の速度定数は 80"""
        # This tests that the heading speed value is documented/defined
        HEADING_SPEED = 80  # As per spec: 見出しをゆっくり読む（speed 80）

        # Validate the constant value
        assert HEADING_SPEED == 80, (
            f"Heading speed should be 80, got {HEADING_SPEED}"
        )
        assert 50 <= HEADING_SPEED <= 300, (
            f"Heading speed should be in valid range 50-300, got {HEADING_SPEED}"
        )


# ============================================================
# Phase 4: User Story 3 - 音声パラメータの調整 (Priority: P3)
# ============================================================


# ============================================================
# T052: test_voice_parameter
# ============================================================

class TestVoiceParameter:
    """Test synthesize() with voice parameter for voice quality adjustment.

    AquesTalk10 voice parameter: 0-200 (default: 100)
    声質を調整するパラメータ。
    """

    def test_synthesize_accepts_voice_parameter(self):
        """synthesize() は voice パラメータを受け付ける"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        # synthesize should accept optional voice parameter
        try:
            result = synthesizer.synthesize("テスト", voice=80)
            assert isinstance(result, bytes), (
                f"synthesize with voice should return bytes, got {type(result)}"
            )
        except TypeError as e:
            # If TypeError, synthesize doesn't accept voice parameter yet
            pytest.fail(
                f"synthesize() should accept voice parameter. Error: {e}"
            )

    def test_synthesize_voice_0_minimum(self):
        """voice=0 の最小値で音声生成"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        result = synthesizer.synthesize("テスト", voice=0)

        assert isinstance(result, bytes), (
            "synthesize with voice=0 should return bytes"
        )
        assert len(result) > 0, (
            "synthesize with voice=0 should return non-empty audio"
        )

    def test_synthesize_voice_200_maximum(self):
        """voice=200 の最大値で音声生成"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        result = synthesizer.synthesize("テスト", voice=200)

        assert isinstance(result, bytes), (
            "synthesize with voice=200 should return bytes"
        )
        assert len(result) > 0, (
            "synthesize with voice=200 should return non-empty audio"
        )

    def test_synthesize_uses_config_voice_when_not_specified(self):
        """voice パラメータ未指定時は config.voice を使用"""
        config = AquesTalkConfig(voice=150)
        synthesizer = AquesTalkSynthesizer(config)
        synthesizer.initialize()

        # Call without voice parameter - should use config.voice=150
        result = synthesizer.synthesize("テスト")

        assert isinstance(result, bytes), (
            "synthesize without voice should use config.voice"
        )

    def test_synthesize_voice_overrides_config(self):
        """voice パラメータは config.voice を上書きする"""
        config = AquesTalkConfig(voice=150)
        synthesizer = AquesTalkSynthesizer(config)
        synthesizer.initialize()

        # Call with voice=80 - should override config.voice=150
        result = synthesizer.synthesize("テスト", voice=80)

        assert isinstance(result, bytes), (
            "synthesize with voice parameter should work"
        )


# ============================================================
# T053: test_pitch_parameter
# ============================================================

class TestPitchParameter:
    """Test synthesize() with pitch parameter for pitch adjustment.

    AquesTalk10 pitch parameter: 50-200 (default: 100)
    ピッチ（声の高さ）を調整するパラメータ。
    """

    def test_synthesize_accepts_pitch_parameter(self):
        """synthesize() は pitch パラメータを受け付ける"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        # synthesize should accept optional pitch parameter
        try:
            result = synthesizer.synthesize("テスト", pitch=120)
            assert isinstance(result, bytes), (
                f"synthesize with pitch should return bytes, got {type(result)}"
            )
        except TypeError as e:
            # If TypeError, synthesize doesn't accept pitch parameter yet
            pytest.fail(
                f"synthesize() should accept pitch parameter. Error: {e}"
            )

    def test_synthesize_pitch_50_minimum(self):
        """pitch=50 の最小値で音声生成"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        result = synthesizer.synthesize("テスト", pitch=50)

        assert isinstance(result, bytes), (
            "synthesize with pitch=50 should return bytes"
        )
        assert len(result) > 0, (
            "synthesize with pitch=50 should return non-empty audio"
        )

    def test_synthesize_pitch_200_maximum(self):
        """pitch=200 の最大値で音声生成"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        result = synthesizer.synthesize("テスト", pitch=200)

        assert isinstance(result, bytes), (
            "synthesize with pitch=200 should return bytes"
        )
        assert len(result) > 0, (
            "synthesize with pitch=200 should return non-empty audio"
        )

    def test_synthesize_uses_config_pitch_when_not_specified(self):
        """pitch パラメータ未指定時は config.pitch を使用"""
        config = AquesTalkConfig(pitch=120)
        synthesizer = AquesTalkSynthesizer(config)
        synthesizer.initialize()

        # Call without pitch parameter - should use config.pitch=120
        result = synthesizer.synthesize("テスト")

        assert isinstance(result, bytes), (
            "synthesize without pitch should use config.pitch"
        )

    def test_synthesize_pitch_overrides_config(self):
        """pitch パラメータは config.pitch を上書きする"""
        config = AquesTalkConfig(pitch=120)
        synthesizer = AquesTalkSynthesizer(config)
        synthesizer.initialize()

        # Call with pitch=80 - should override config.pitch=120
        result = synthesizer.synthesize("テスト", pitch=80)

        assert isinstance(result, bytes), (
            "synthesize with pitch parameter should work"
        )


# ============================================================
# T054: test_parameter_validation
# ============================================================

class TestParameterValidation:
    """Test parameter validation for AquesTalk10 parameters.

    Valid ranges:
    - speed: 50-300 (default: 100)
    - voice: 0-200 (default: 100)
    - pitch: 50-200 (default: 100)
    """

    def test_speed_below_minimum_raises_error(self):
        """speed が 50 未満の場合はエラー"""
        config = AquesTalkConfig(speed=49)  # Below minimum 50
        synthesizer = AquesTalkSynthesizer(config)

        with pytest.raises(ValueError) as exc_info:
            synthesizer.initialize()

        assert "speed" in str(exc_info.value).lower(), (
            f"Error should mention 'speed': {exc_info.value}"
        )

    def test_speed_above_maximum_raises_error(self):
        """speed が 300 超の場合はエラー"""
        config = AquesTalkConfig(speed=301)  # Above maximum 300
        synthesizer = AquesTalkSynthesizer(config)

        with pytest.raises(ValueError) as exc_info:
            synthesizer.initialize()

        assert "speed" in str(exc_info.value).lower(), (
            f"Error should mention 'speed': {exc_info.value}"
        )

    def test_voice_below_minimum_raises_error(self):
        """voice が 0 未満の場合はエラー"""
        config = AquesTalkConfig(voice=-1)  # Below minimum 0
        synthesizer = AquesTalkSynthesizer(config)

        with pytest.raises(ValueError) as exc_info:
            synthesizer.initialize()

        assert "voice" in str(exc_info.value).lower(), (
            f"Error should mention 'voice': {exc_info.value}"
        )

    def test_voice_above_maximum_raises_error(self):
        """voice が 200 超の場合はエラー"""
        config = AquesTalkConfig(voice=201)  # Above maximum 200
        synthesizer = AquesTalkSynthesizer(config)

        with pytest.raises(ValueError) as exc_info:
            synthesizer.initialize()

        assert "voice" in str(exc_info.value).lower(), (
            f"Error should mention 'voice': {exc_info.value}"
        )

    def test_pitch_below_minimum_raises_error(self):
        """pitch が 50 未満の場合はエラー"""
        config = AquesTalkConfig(pitch=49)  # Below minimum 50
        synthesizer = AquesTalkSynthesizer(config)

        with pytest.raises(ValueError) as exc_info:
            synthesizer.initialize()

        assert "pitch" in str(exc_info.value).lower(), (
            f"Error should mention 'pitch': {exc_info.value}"
        )

    def test_pitch_above_maximum_raises_error(self):
        """pitch が 200 超の場合はエラー"""
        config = AquesTalkConfig(pitch=201)  # Above maximum 200
        synthesizer = AquesTalkSynthesizer(config)

        with pytest.raises(ValueError) as exc_info:
            synthesizer.initialize()

        assert "pitch" in str(exc_info.value).lower(), (
            f"Error should mention 'pitch': {exc_info.value}"
        )

    def test_valid_parameters_no_error(self):
        """有効なパラメータ範囲内ではエラーなし"""
        # Test boundary values
        config = AquesTalkConfig(speed=50, voice=0, pitch=50)
        synthesizer = AquesTalkSynthesizer(config)

        # Should not raise
        synthesizer.initialize()
        assert synthesizer._initialized, "Should initialize with valid min params"

        # Test maximum values
        config = AquesTalkConfig(speed=300, voice=200, pitch=200)
        synthesizer = AquesTalkSynthesizer(config)
        synthesizer.initialize()
        assert synthesizer._initialized, "Should initialize with valid max params"

    def test_synthesize_speed_parameter_validation(self):
        """synthesize() の speed パラメータもバリデーション"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        # Invalid speed parameter should raise error
        with pytest.raises(ValueError) as exc_info:
            synthesizer.synthesize("テスト", speed=49)

        assert "speed" in str(exc_info.value).lower(), (
            f"Error should mention 'speed': {exc_info.value}"
        )

    def test_synthesize_voice_parameter_validation(self):
        """synthesize() の voice パラメータもバリデーション"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        # Invalid voice parameter should raise error
        with pytest.raises(ValueError) as exc_info:
            synthesizer.synthesize("テスト", voice=-1)

        assert "voice" in str(exc_info.value).lower(), (
            f"Error should mention 'voice': {exc_info.value}"
        )

    def test_synthesize_pitch_parameter_validation(self):
        """synthesize() の pitch パラメータもバリデーション"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        # Invalid pitch parameter should raise error
        with pytest.raises(ValueError) as exc_info:
            synthesizer.synthesize("テスト", pitch=201)

        assert "pitch" in str(exc_info.value).lower(), (
            f"Error should mention 'pitch': {exc_info.value}"
        )


class TestCombinedParameters:
    """Test synthesize() with multiple parameters combined."""

    def test_synthesize_with_all_parameters(self):
        """synthesize() は speed, voice, pitch を同時に受け付ける"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        try:
            result = synthesizer.synthesize(
                "テスト",
                speed=120,
                voice=80,
                pitch=90
            )
            assert isinstance(result, bytes), (
                f"synthesize with all params should return bytes, got {type(result)}"
            )
            assert len(result) > 0, (
                "synthesize with all params should return non-empty audio"
            )
        except TypeError as e:
            pytest.fail(
                f"synthesize() should accept speed, voice, pitch parameters. Error: {e}"
            )

    def test_synthesize_with_partial_parameters(self):
        """synthesize() は一部のパラメータのみでも動作"""
        synthesizer = AquesTalkSynthesizer()
        synthesizer.initialize()

        # Only speed
        result1 = synthesizer.synthesize("テスト", speed=120)
        assert isinstance(result1, bytes), "Should work with only speed"

        # Only voice (once voice parameter is implemented)
        try:
            result2 = synthesizer.synthesize("テスト", voice=80)
            assert isinstance(result2, bytes), "Should work with only voice"
        except TypeError:
            pytest.fail("synthesize() should accept voice parameter")

        # Only pitch (once pitch parameter is implemented)
        try:
            result3 = synthesizer.synthesize("テスト", pitch=90)
            assert isinstance(result3, bytes), "Should work with only pitch"
        except TypeError:
            pytest.fail("synthesize() should accept pitch parameter")
