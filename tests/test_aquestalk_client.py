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
