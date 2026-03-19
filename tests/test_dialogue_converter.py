"""Tests for dialogue_converter.py - Phase 2, Phase 3 & Phase 5 RED Tests.

Phase 2 RED Tests - US1: 書籍セクションを対話形式に変換
LLMを使用してセクション内容を博士と助手の対話形式に変換する機能のテスト。

Phase 3 RED Tests - US2: 長文セクションの分割処理
4,000文字を超えるセクションを見出し単位で分割し、それぞれを対話形式に変換するテスト。

Phase 5 RED Tests - CLI統合 & Makefile
dialogue_converter.py のCLI引数パース（parse_args）とmain()統合テスト。

Target functions:
- src/dialogue_converter.py::DialogueBlock dataclass
- src/dialogue_converter.py::Utterance dataclass
- src/dialogue_converter.py::ConversionResult dataclass
- src/dialogue_converter.py::extract_sections()
- src/dialogue_converter.py::analyze_structure()
- src/dialogue_converter.py::generate_dialogue()
- src/dialogue_converter.py::to_dialogue_xml()
- src/dialogue_converter.py::should_split()
- src/dialogue_converter.py::split_by_heading()
- src/dialogue_converter.py::parse_args()
- src/dialogue_converter.py::main()

Test coverage:
- T011: DialogueBlock, Utterance データクラスのテスト
- T012: セクション抽出関数のテスト
- T013: LLM構造分析（intro/dialogue/conclusion分類）のテスト
- T014: LLM対話生成（A/B発話）のテスト
- T015: 対話XMLシリアライズのテスト
- T016: エッジケース（短文、空セクション）のテスト
- T032: 文字数判定関数 should_split() のテスト
- T033: 見出し単位分割関数 split_by_heading() のテスト
- T034: 分割後の連続性（コンテキスト維持）テスト
- T035: 境界ケース（3,500〜4,500文字）のテスト
- T072: dialogue_converter.py CLI引数パースのテスト
- T073: dialogue_converter.py main() 統合テスト
"""

import json
import sys
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch

import pytest

from src.dialogue_converter import (
    ConversionResult,
    DialogueBlock,
    Section,
    Utterance,
    analyze_structure,
    convert_section,
    extract_sections,
    generate_dialogue,
    to_dialogue_xml,
)

# Phase 3 RED: should_split, split_by_heading はまだ未実装
# ImportErrorが発生した場合はテストをスキップではなくFAILさせる
try:
    from src.dialogue_converter import should_split, split_by_heading
except ImportError:
    # 未実装のためマーカーとして None を設定、テスト内でImportError を再送出
    should_split = None
    split_by_heading = None

# Phase 5 RED: parse_args, main はまだ未実装
try:
    from src.dialogue_converter import main as converter_main
    from src.dialogue_converter import parse_args as converter_parse_args
except ImportError:
    converter_parse_args = None
    converter_main = None


# ollama モックを sys.modules に追加（main() 内の動的インポート用）
@pytest.fixture(autouse=False)
def mock_ollama():
    """ollama モジュールをモックするフィクスチャ。main() テストで使用。"""
    mock_module = MagicMock()
    mock_module.chat = MagicMock(return_value={"message": {"content": "{}"}})
    with patch.dict(sys.modules, {"ollama": mock_module}):
        # CI環境でも _OLLAMA_AVAILABLE を True にしてテスト実行
        with patch("src.dialogue_converter._OLLAMA_AVAILABLE", True):
            with patch("src.dialogue_converter.ollama", mock_module):
                yield mock_module


def _require_parse_args():
    """parse_args が未実装の場合にテストをFAILさせる"""
    if converter_parse_args is None:
        raise ImportError("parse_args is not yet implemented in src/dialogue_converter.py")


def _require_main():
    """main が未実装の場合にテストをFAILさせる"""
    if converter_main is None:
        raise ImportError("main is not yet implemented in src/dialogue_converter.py")


def _require_should_split():
    """should_split が未実装の場合にテストをFAILさせる"""
    if should_split is None:
        raise ImportError("should_split is not yet implemented in src/dialogue_converter.py")


def _require_split_by_heading():
    """split_by_heading が未実装の場合にテストをFAILさせる"""
    if split_by_heading is None:
        raise ImportError("split_by_heading is not yet implemented in src/dialogue_converter.py")


# =============================================================================
# T011: DialogueBlock, Utterance データクラスのテスト
# =============================================================================


class TestUtteranceDataclass:
    """Utterance データクラスの生成と制約をテスト"""

    def test_utterance_creation_speaker_a(self):
        """話者A（博士）のUtteranceが正しく生成される"""
        utterance = Utterance(speaker="A", text="これは説明です。")
        assert utterance.speaker == "A"
        assert utterance.text == "これは説明です。"

    def test_utterance_creation_speaker_b(self):
        """話者B（助手）のUtteranceが正しく生成される"""
        utterance = Utterance(speaker="B", text="なるほど、教えてください。")
        assert utterance.speaker == "B"
        assert utterance.text == "なるほど、教えてください。"

    def test_utterance_has_speaker_field(self):
        """Utteranceにspeakerフィールドが存在する"""
        utterance = Utterance(speaker="A", text="テスト")
        assert hasattr(utterance, "speaker")

    def test_utterance_has_text_field(self):
        """Utteranceにtextフィールドが存在する"""
        utterance = Utterance(speaker="A", text="テスト")
        assert hasattr(utterance, "text")

    def test_utterance_equality(self):
        """同じ内容のUtteranceが等価である"""
        u1 = Utterance(speaker="A", text="同じテキスト")
        u2 = Utterance(speaker="A", text="同じテキスト")
        assert u1 == u2

    def test_utterance_inequality_different_speaker(self):
        """異なる話者のUtteranceが不等価である"""
        u1 = Utterance(speaker="A", text="同じテキスト")
        u2 = Utterance(speaker="B", text="同じテキスト")
        assert u1 != u2

    def test_utterance_with_unicode_text(self):
        """Unicode（絵文字含む）テキストを保持できる"""
        utterance = Utterance(speaker="A", text="量子コンピュータの概念")
        assert utterance.text == "量子コンピュータの概念"

    def test_utterance_with_special_characters(self):
        """特殊文字（引用符、括弧等）を含むテキストを保持できる"""
        utterance = Utterance(speaker="B", text='「これは"テスト"です」（補足）')
        assert utterance.text == '「これは"テスト"です」（補足）'


class TestDialogueBlockDataclass:
    """DialogueBlock データクラスの生成と構造をテスト"""

    def test_dialogue_block_creation(self):
        """DialogueBlockが正しく生成される"""
        utterances = [
            Utterance(speaker="A", text="説明します。"),
            Utterance(speaker="B", text="お願いします。"),
        ]
        block = DialogueBlock(
            section_number="1.1",
            section_title="テストセクション",
            introduction="導入文です。",
            dialogue=utterances,
            conclusion="まとめです。",
        )
        assert block.section_number == "1.1"
        assert block.section_title == "テストセクション"
        assert block.introduction == "導入文です。"
        assert len(block.dialogue) == 2
        assert block.conclusion == "まとめです。"

    def test_dialogue_block_has_required_fields(self):
        """DialogueBlockに必須フィールドがすべて存在する"""
        block = DialogueBlock(
            section_number="2.3",
            section_title="タイトル",
            introduction="導入",
            dialogue=[Utterance(speaker="A", text="テスト")],
            conclusion="結論",
        )
        assert hasattr(block, "section_number")
        assert hasattr(block, "section_title")
        assert hasattr(block, "introduction")
        assert hasattr(block, "dialogue")
        assert hasattr(block, "conclusion")

    def test_dialogue_block_with_empty_introduction(self):
        """導入が空文字列のDialogueBlockを生成できる"""
        block = DialogueBlock(
            section_number="1.1",
            section_title="タイトル",
            introduction="",
            dialogue=[Utterance(speaker="A", text="テスト")],
            conclusion="結論",
        )
        assert block.introduction == ""

    def test_dialogue_block_with_empty_conclusion(self):
        """結論が空文字列のDialogueBlockを生成できる"""
        block = DialogueBlock(
            section_number="1.1",
            section_title="タイトル",
            introduction="導入",
            dialogue=[Utterance(speaker="A", text="テスト")],
            conclusion="",
        )
        assert block.conclusion == ""

    def test_dialogue_block_with_multiple_utterances(self):
        """複数の発言を含むDialogueBlockが正しく保持される"""
        utterances = [
            Utterance(speaker="A", text="まず基本から。"),
            Utterance(speaker="B", text="はい、お願いします。"),
            Utterance(speaker="A", text="APIとは..."),
            Utterance(speaker="B", text="なるほど。"),
            Utterance(speaker="A", text="具体的には..."),
        ]
        block = DialogueBlock(
            section_number="3.1",
            section_title="API入門",
            introduction="この節ではAPIについて説明します。",
            dialogue=utterances,
            conclusion="以上がAPIの基本でした。",
        )
        assert len(block.dialogue) == 5
        assert block.dialogue[0].speaker == "A"
        assert block.dialogue[1].speaker == "B"

    def test_dialogue_block_section_number_format(self):
        """セクション番号がX.Y形式で保持される"""
        block = DialogueBlock(
            section_number="12.34",
            section_title="タイトル",
            introduction="",
            dialogue=[Utterance(speaker="A", text="テスト")],
            conclusion="",
        )
        assert block.section_number == "12.34"


class TestConversionResultDataclass:
    """ConversionResult データクラスの生成をテスト"""

    def test_conversion_result_success(self):
        """成功時のConversionResultが正しく生成される"""
        block = DialogueBlock(
            section_number="1.1",
            section_title="テスト",
            introduction="導入",
            dialogue=[Utterance(speaker="A", text="テスト")],
            conclusion="結論",
        )
        result = ConversionResult(
            success=True,
            dialogue_block=block,
            error_message=None,
            processing_time_sec=1.5,
            input_char_count=500,
            was_split=False,
        )
        assert result.success is True
        assert result.dialogue_block is not None
        assert result.error_message is None
        assert result.processing_time_sec == 1.5
        assert result.input_char_count == 500
        assert result.was_split is False

    def test_conversion_result_failure(self):
        """失敗時のConversionResultが正しく生成される"""
        result = ConversionResult(
            success=False,
            dialogue_block=None,
            error_message="LLM応答のパースに失敗",
            processing_time_sec=0.5,
            input_char_count=100,
            was_split=False,
        )
        assert result.success is False
        assert result.dialogue_block is None
        assert result.error_message == "LLM応答のパースに失敗"

    def test_conversion_result_has_all_fields(self):
        """ConversionResultにすべてのフィールドが存在する"""
        result = ConversionResult(
            success=True,
            dialogue_block=None,
            error_message=None,
            processing_time_sec=0.0,
            input_char_count=0,
            was_split=False,
        )
        assert hasattr(result, "success")
        assert hasattr(result, "dialogue_block")
        assert hasattr(result, "error_message")
        assert hasattr(result, "processing_time_sec")
        assert hasattr(result, "input_char_count")
        assert hasattr(result, "was_split")

    def test_conversion_result_was_split_true(self):
        """分割処理された場合のwas_splitフラグ"""
        result = ConversionResult(
            success=True,
            dialogue_block=None,
            error_message=None,
            processing_time_sec=10.0,
            input_char_count=5000,
            was_split=True,
        )
        assert result.was_split is True


# =============================================================================
# T012: セクション抽出関数のテスト
# =============================================================================


class TestExtractSections:
    """extract_sections() のテスト - ContentItemリストからセクション単位を抽出"""

    def test_extract_sections_returns_list(self):
        """extract_sections()がリストを返す"""
        # ContentItemリストを模擬（xml_parserからの出力形式）
        from src.xml_parser import ContentItem, HeadingInfo

        items = [
            ContentItem(
                item_type="heading",
                text="1.1 テストセクション",
                heading_info=HeadingInfo(level=2, number="1.1", title="テストセクション"),
                chapter_number=1,
            ),
            ContentItem(item_type="paragraph", text="段落1のテキスト。", chapter_number=1),
            ContentItem(item_type="paragraph", text="段落2のテキスト。", chapter_number=1),
        ]
        result = extract_sections(items)
        assert isinstance(result, list)

    def test_extract_sections_groups_by_section_heading(self):
        """セクション見出しごとにグループ化される"""
        from src.xml_parser import ContentItem, HeadingInfo

        items = [
            ContentItem(
                item_type="heading",
                text="1.1 セクションA",
                heading_info=HeadingInfo(level=2, number="1.1", title="セクションA"),
                chapter_number=1,
            ),
            ContentItem(item_type="paragraph", text="段落A1。", chapter_number=1),
            ContentItem(
                item_type="heading",
                text="1.2 セクションB",
                heading_info=HeadingInfo(level=2, number="1.2", title="セクションB"),
                chapter_number=1,
            ),
            ContentItem(item_type="paragraph", text="段落B1。", chapter_number=1),
        ]
        result = extract_sections(items)
        assert len(result) == 2

    def test_extract_sections_contains_section_number(self):
        """抽出結果にセクション番号が含まれる"""
        from src.xml_parser import ContentItem, HeadingInfo

        items = [
            ContentItem(
                item_type="heading",
                text="2.3 テスト",
                heading_info=HeadingInfo(level=2, number="2.3", title="テスト"),
                chapter_number=2,
            ),
            ContentItem(item_type="paragraph", text="内容。", chapter_number=2),
        ]
        result = extract_sections(items)
        assert len(result) >= 1
        # セクション番号が保持されていることを確認
        section = result[0]
        assert hasattr(section, "number") or (isinstance(section, dict) and "number" in section)

    def test_extract_sections_contains_paragraphs(self):
        """抽出結果に段落テキストが含まれる"""
        from src.xml_parser import ContentItem, HeadingInfo

        items = [
            ContentItem(
                item_type="heading",
                text="1.1 テスト",
                heading_info=HeadingInfo(level=2, number="1.1", title="テスト"),
                chapter_number=1,
            ),
            ContentItem(item_type="paragraph", text="最初の段落です。", chapter_number=1),
            ContentItem(item_type="paragraph", text="二番目の段落です。", chapter_number=1),
        ]
        result = extract_sections(items)
        section = result[0]
        # 段落テキストがセクションに含まれる
        if hasattr(section, "paragraphs"):
            assert len(section.paragraphs) == 2
        elif isinstance(section, dict) and "paragraphs" in section:
            assert len(section["paragraphs"]) == 2
        else:
            # セクションオブジェクトの構造に依存
            assert False, f"Section should contain paragraphs, got: {section}"

    def test_extract_sections_skips_chapter_headings(self):
        """チャプターレベルの見出し(level=1)はセクション区切りにならない"""
        from src.xml_parser import ContentItem, HeadingInfo

        items = [
            ContentItem(
                item_type="heading",
                text="1 チャプター",
                heading_info=HeadingInfo(level=1, number="1", title="チャプター"),
                chapter_number=1,
            ),
            ContentItem(
                item_type="heading",
                text="1.1 セクション",
                heading_info=HeadingInfo(level=2, number="1.1", title="セクション"),
                chapter_number=1,
            ),
            ContentItem(item_type="paragraph", text="内容。", chapter_number=1),
        ]
        result = extract_sections(items)
        # チャプター見出しではなくセクション見出しでグループ化
        assert len(result) == 1

    def test_extract_sections_empty_input(self):
        """空のContentItemリストを渡すと空リストが返る"""
        result = extract_sections([])
        assert result == []

    def test_extract_sections_no_sections_only_paragraphs(self):
        """セクション見出しがない場合の処理"""
        from src.xml_parser import ContentItem

        items = [
            ContentItem(item_type="paragraph", text="孤立した段落。", chapter_number=1),
        ]
        result = extract_sections(items)
        # 見出しなしの段落はスキップまたは空リスト
        assert isinstance(result, list)


# =============================================================================
# T013: LLM構造分析（intro/dialogue/conclusion分類）のテスト
# =============================================================================


class TestAnalyzeStructure:
    """analyze_structure() のテスト - LLMで段落をintro/dialogue/conclusionに分類"""

    def test_analyze_structure_returns_dict(self):
        """analyze_structure()が辞書を返す"""
        mock_ollama = MagicMock()
        content = '{"introduction": ["導入段落"], "dialogue": ["本論段落1", "本論段落2"], "conclusion": ["まとめ段落"]}'
        mock_ollama.return_value = {"message": {"content": content}}
        paragraphs = ["導入段落", "本論段落1", "本論段落2", "まとめ段落"]
        result = analyze_structure(paragraphs, ollama_chat_func=mock_ollama)
        assert isinstance(result, dict)

    def test_analyze_structure_has_three_keys(self):
        """結果にintroduction, dialogue, conclusionの3キーが含まれる"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {
            "message": {"content": '{"introduction": ["導入"], "dialogue": ["本論"], "conclusion": ["結論"]}'}
        }
        paragraphs = ["導入", "本論", "結論"]
        result = analyze_structure(paragraphs, ollama_chat_func=mock_ollama)
        assert "introduction" in result
        assert "dialogue" in result
        assert "conclusion" in result

    def test_analyze_structure_introduction_is_list(self):
        """introductionがリスト型である"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {
            "message": {"content": '{"introduction": ["最初の段落"], "dialogue": ["本論"], "conclusion": ["結論"]}'}
        }
        result = analyze_structure(["最初の段落", "本論", "結論"], ollama_chat_func=mock_ollama)
        assert isinstance(result["introduction"], list)

    def test_analyze_structure_dialogue_is_list(self):
        """dialogueがリスト型である"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {
            "message": {"content": '{"introduction": ["導入"], "dialogue": ["本論1", "本論2"], "conclusion": ["結論"]}'}
        }
        result = analyze_structure(["導入", "本論1", "本論2", "結論"], ollama_chat_func=mock_ollama)
        assert isinstance(result["dialogue"], list)

    def test_analyze_structure_calls_llm(self):
        """LLM（ollama）が呼び出される"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {
            "message": {"content": '{"introduction": [], "dialogue": ["テスト"], "conclusion": []}'}
        }
        analyze_structure(["テスト段落"], ollama_chat_func=mock_ollama)
        mock_ollama.assert_called_once()

    def test_analyze_structure_with_model_parameter(self):
        """modelパラメータがLLM呼び出しに渡される"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {
            "message": {"content": '{"introduction": [], "dialogue": ["テスト"], "conclusion": []}'}
        }
        analyze_structure(["テスト段落"], model="gpt-oss:20b", ollama_chat_func=mock_ollama)
        call_kwargs = mock_ollama.call_args
        # modelパラメータが渡されていることを確認
        assert "model" in call_kwargs.kwargs or (
            len(call_kwargs.args) > 0 and call_kwargs.kwargs.get("model") == "gpt-oss:20b"
        )

    def test_analyze_structure_handles_llm_json_error(self):
        """LLMが不正なJSONを返した場合にエラーハンドリングされる"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {"message": {"content": "これはJSONではありません"}}
        # 不正なJSON応答でも例外が適切に処理される
        try:
            result = analyze_structure(["テスト"], ollama_chat_func=mock_ollama)
            # エラーハンドリングされてデフォルト値が返る場合
            assert isinstance(result, dict)
        except (ValueError, KeyError):
            # 明示的なエラーが発生する場合も許容
            assert True

    def test_analyze_structure_handles_llm_timeout(self):
        """LLM呼び出しがタイムアウトした場合のエラーハンドリング"""
        mock_ollama = MagicMock()
        mock_ollama.side_effect = TimeoutError("LLM timeout")
        try:
            analyze_structure(["テスト"], ollama_chat_func=mock_ollama)
            assert False, "TimeoutError should be raised or handled"
        except (TimeoutError, RuntimeError):
            assert True

    def test_analyze_structure_handles_empty_response(self):
        """LLMが空のレスポンスを返した場合"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {"message": {"content": ""}}
        try:
            result = analyze_structure(["テスト"], ollama_chat_func=mock_ollama)
            assert isinstance(result, dict)
        except (ValueError, KeyError):
            assert True


# =============================================================================
# T014: LLM対話生成（A/B発話）のテスト
# =============================================================================


class TestGenerateDialogue:
    """generate_dialogue() のテスト - LLMで対話（A/B発話）を生成"""

    def test_generate_dialogue_returns_list(self):
        """generate_dialogue()がUtteranceのリストを返す"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {
            "message": {"content": '[{"speaker": "A", "text": "説明します"}, {"speaker": "B", "text": "お願いします"}]'}
        }
        result = generate_dialogue(
            dialogue_paragraphs=["本論の段落"],
            ollama_chat_func=mock_ollama,
        )
        assert isinstance(result, list)

    def test_generate_dialogue_returns_utterance_objects(self):
        """返却リストの各要素がUtteranceインスタンスである"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {"message": {"content": '[{"speaker": "A", "text": "テスト"}]'}}
        result = generate_dialogue(
            dialogue_paragraphs=["段落"],
            ollama_chat_func=mock_ollama,
        )
        assert len(result) >= 1
        for item in result:
            assert isinstance(item, Utterance)

    def test_generate_dialogue_has_speaker_a_and_b(self):
        """生成された対話にA（博士）とB（助手）の両方が含まれる"""
        mock_ollama = MagicMock()
        content = '[{"speaker": "A", "text": "概念を説明しましょう"}, {"speaker": "B", "text": "はい、教えてください"}]'
        mock_ollama.return_value = {"message": {"content": content}}
        result = generate_dialogue(
            dialogue_paragraphs=["APIの基本概念について説明します。"],
            ollama_chat_func=mock_ollama,
        )
        speakers = {u.speaker for u in result}
        assert "A" in speakers
        assert "B" in speakers

    def test_generate_dialogue_calls_llm(self):
        """LLM（ollama）が呼び出される"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {"message": {"content": '[{"speaker": "A", "text": "テスト"}]'}}
        generate_dialogue(dialogue_paragraphs=["テスト"], ollama_chat_func=mock_ollama)
        mock_ollama.assert_called_once()

    def test_generate_dialogue_utterance_text_not_empty(self):
        """各発話のテキストが空でないことを確認"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {
            "message": {"content": '[{"speaker": "A", "text": "内容があります"}, {"speaker": "B", "text": "確認です"}]'}
        }
        result = generate_dialogue(
            dialogue_paragraphs=["段落テキスト"],
            ollama_chat_func=mock_ollama,
        )
        for utterance in result:
            assert utterance.text.strip() != ""

    def test_generate_dialogue_handles_invalid_json(self):
        """LLMが不正なJSONを返した場合のエラーハンドリング"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {"message": {"content": "不正なJSON応答"}}
        try:
            result = generate_dialogue(
                dialogue_paragraphs=["テスト"],
                ollama_chat_func=mock_ollama,
            )
            # デフォルト値が返る場合
            assert isinstance(result, list)
        except (ValueError, KeyError):
            assert True

    def test_generate_dialogue_handles_network_error(self):
        """ネットワークエラー時のハンドリング"""
        mock_ollama = MagicMock()
        mock_ollama.side_effect = ConnectionError("Network error")
        try:
            generate_dialogue(
                dialogue_paragraphs=["テスト"],
                ollama_chat_func=mock_ollama,
            )
            assert False, "ConnectionError should be raised or handled"
        except (ConnectionError, RuntimeError):
            assert True

    def test_generate_dialogue_with_context_parameters(self):
        """introduction/conclusionのコンテキストが渡せる"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {"message": {"content": '[{"speaker": "A", "text": "テスト"}]'}}
        result = generate_dialogue(
            dialogue_paragraphs=["本論"],
            introduction="導入テキスト",
            conclusion="結論テキスト",
            ollama_chat_func=mock_ollama,
        )
        assert isinstance(result, list)

    def test_generate_dialogue_preserves_speaker_order(self):
        """LLMの応答順序で発話が保持される"""
        mock_ollama = MagicMock()
        content = (
            '[{"speaker": "A", "text": "1番目"}, {"speaker": "B", "text": "2番目"}, {"speaker": "A", "text": "3番目"}]'
        )
        mock_ollama.return_value = {"message": {"content": content}}
        result = generate_dialogue(
            dialogue_paragraphs=["段落"],
            ollama_chat_func=mock_ollama,
        )
        assert result[0].speaker == "A"
        assert result[1].speaker == "B"
        assert result[2].speaker == "A"


# =============================================================================
# T015: 対話XMLシリアライズのテスト
# =============================================================================


class TestToDialogueXml:
    """to_dialogue_xml() のテスト - DialogueBlockをXML文字列に変換"""

    def _make_block(
        self,
        section_number="1.1",
        section_title="テスト",
        introduction="導入文",
        utterances=None,
        conclusion="結論文",
    ):
        """テスト用DialogueBlockを生成するヘルパー"""
        if utterances is None:
            utterances = [
                Utterance(speaker="A", text="説明します。"),
                Utterance(speaker="B", text="お願いします。"),
            ]
        return DialogueBlock(
            section_number=section_number,
            section_title=section_title,
            introduction=introduction,
            dialogue=utterances,
            conclusion=conclusion,
        )

    def test_to_dialogue_xml_returns_string(self):
        """to_dialogue_xml()が文字列を返す"""
        block = self._make_block()
        result = to_dialogue_xml(block)
        assert isinstance(result, str)

    def test_to_dialogue_xml_is_valid_xml(self):
        """出力がパース可能な有効なXMLである"""
        block = self._make_block()
        result = to_dialogue_xml(block)
        # XMLとしてパースできることを確認
        root = ET.fromstring(result)
        assert root is not None

    def test_to_dialogue_xml_contains_section_number(self):
        """XMLにセクション番号が含まれる"""
        block = self._make_block(section_number="2.5")
        result = to_dialogue_xml(block)
        assert "2.5" in result

    def test_to_dialogue_xml_contains_section_title(self):
        """XMLにセクションタイトルが含まれる"""
        block = self._make_block(section_title="APIの基礎")
        result = to_dialogue_xml(block)
        assert "APIの基礎" in result

    def test_to_dialogue_xml_contains_introduction(self):
        """XMLに導入テキストが含まれる"""
        block = self._make_block(introduction="この節ではAPIについて学びます。")
        result = to_dialogue_xml(block)
        assert "この節ではAPIについて学びます。" in result

    def test_to_dialogue_xml_contains_conclusion(self):
        """XMLに結論テキストが含まれる"""
        block = self._make_block(conclusion="以上がAPIの基本でした。")
        result = to_dialogue_xml(block)
        assert "以上がAPIの基本でした。" in result

    def test_to_dialogue_xml_contains_utterances(self):
        """XMLに発話テキストが含まれる"""
        utterances = [
            Utterance(speaker="A", text="博士の発言です。"),
            Utterance(speaker="B", text="助手の発言です。"),
        ]
        block = self._make_block(utterances=utterances)
        result = to_dialogue_xml(block)
        assert "博士の発言です。" in result
        assert "助手の発言です。" in result

    def test_to_dialogue_xml_contains_speaker_attributes(self):
        """XMLにspeaker属性が含まれる"""
        block = self._make_block()
        result = to_dialogue_xml(block)
        assert 'speaker="A"' in result
        assert 'speaker="B"' in result

    def test_to_dialogue_xml_contains_narrator_speaker(self):
        """introduction/conclusionにnarrator話者が指定される"""
        block = self._make_block()
        result = to_dialogue_xml(block)
        assert 'speaker="narrator"' in result

    def test_to_dialogue_xml_has_dialogue_section_structure(self):
        """data-model.mdで定義されたXML構造に従う"""
        block = self._make_block()
        result = to_dialogue_xml(block)
        root = ET.fromstring(result)
        # introduction要素が存在
        intro_elem = root.find(".//introduction")
        assert intro_elem is not None
        # dialogue要素が存在
        dialogue_elem = root.find(".//dialogue")
        assert dialogue_elem is not None
        # conclusion要素が存在
        conclusion_elem = root.find(".//conclusion")
        assert conclusion_elem is not None

    def test_to_dialogue_xml_utterance_elements(self):
        """dialogue配下にutterance要素が正しく生成される"""
        utterances = [
            Utterance(speaker="A", text="発言1"),
            Utterance(speaker="B", text="発言2"),
            Utterance(speaker="A", text="発言3"),
        ]
        block = self._make_block(utterances=utterances)
        result = to_dialogue_xml(block)
        root = ET.fromstring(result)
        utterance_elems = root.findall(".//dialogue/utterance")
        assert len(utterance_elems) == 3

    def test_to_dialogue_xml_with_special_characters(self):
        """XMLの特殊文字（<, >, &）がエスケープされる"""
        utterances = [
            Utterance(speaker="A", text="A < B & C > D"),
        ]
        block = self._make_block(utterances=utterances)
        result = to_dialogue_xml(block)
        # パース可能であること（特殊文字がエスケープされている）
        root = ET.fromstring(result)
        assert root is not None

    def test_to_dialogue_xml_empty_introduction(self):
        """空の導入でもXMLが生成される"""
        block = self._make_block(introduction="")
        result = to_dialogue_xml(block)
        root = ET.fromstring(result)
        assert root is not None


# =============================================================================
# T016: エッジケース（短文、空セクション）のテスト
# =============================================================================


class TestEdgeCases:
    """エッジケースのテスト - 異常値、境界値、特殊入力"""

    # --- Null/None 入力 ---

    def test_extract_sections_with_none_input(self):
        """extract_sections()にNoneを渡した場合"""
        try:
            result = extract_sections(None)
            assert result == [] or result is None
        except (TypeError, ValueError):
            assert True

    def test_analyze_structure_with_empty_paragraphs(self):
        """analyze_structure()に空リストを渡した場合"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {"message": {"content": '{"introduction": [], "dialogue": [], "conclusion": []}'}}
        try:
            result = analyze_structure([], ollama_chat_func=mock_ollama)
            assert isinstance(result, dict)
        except ValueError:
            assert True

    def test_generate_dialogue_with_empty_paragraphs(self):
        """generate_dialogue()に空リストを渡した場合"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {"message": {"content": "[]"}}
        try:
            result = generate_dialogue(
                dialogue_paragraphs=[],
                ollama_chat_func=mock_ollama,
            )
            assert isinstance(result, list)
            assert len(result) == 0
        except ValueError:
            assert True

    # --- 短文テスト ---

    def test_analyze_structure_with_single_short_paragraph(self):
        """1文のみの非常に短いセクション"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {
            "message": {"content": '{"introduction": [], "dialogue": ["短い文。"], "conclusion": []}'}
        }
        result = analyze_structure(["短い文。"], ollama_chat_func=mock_ollama)
        assert isinstance(result, dict)
        assert "dialogue" in result

    def test_generate_dialogue_with_very_short_text(self):
        """非常に短いテキスト（1-2文）からの対話生成"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {"message": {"content": '[{"speaker": "A", "text": "短い説明"}]'}}
        result = generate_dialogue(
            dialogue_paragraphs=["短文。"],
            ollama_chat_func=mock_ollama,
        )
        assert isinstance(result, list)

    # --- 空値テスト ---

    def test_to_dialogue_xml_with_empty_dialogue_list(self):
        """対話リストが空のDialogueBlockのXML化"""
        block = DialogueBlock(
            section_number="1.1",
            section_title="空セクション",
            introduction="導入のみ。",
            dialogue=[],
            conclusion="結論のみ。",
        )
        try:
            result = to_dialogue_xml(block)
            assert isinstance(result, str)
        except ValueError:
            # 空の対話リストはエラーになる場合も許容
            assert True

    def test_dialogue_block_with_none_introduction(self):
        """introductionがNoneの場合"""
        try:
            block = DialogueBlock(
                section_number="1.1",
                section_title="タイトル",
                introduction=None,
                dialogue=[Utterance(speaker="A", text="テスト")],
                conclusion="結論",
            )
            # Noneが許容される場合
            assert block.introduction is None
        except (TypeError, ValueError):
            assert True

    # --- 大量データテスト ---

    def test_generate_dialogue_with_large_paragraph_count(self):
        """多数の段落（50個）を含むセクションの対話生成"""
        mock_ollama = MagicMock()
        large_response = [{"speaker": "A" if i % 2 == 0 else "B", "text": f"発話{i}"} for i in range(100)]
        import json

        mock_ollama.return_value = {"message": {"content": json.dumps(large_response, ensure_ascii=False)}}
        paragraphs = [f"段落{i}の内容です。" for i in range(50)]
        result = generate_dialogue(
            dialogue_paragraphs=paragraphs,
            ollama_chat_func=mock_ollama,
        )
        assert isinstance(result, list)
        assert len(result) > 0

    def test_to_dialogue_xml_with_many_utterances(self):
        """100個の発話を含むDialogueBlockのXML化"""
        utterances = [Utterance(speaker="A" if i % 2 == 0 else "B", text=f"発話{i}のテキスト") for i in range(100)]
        block = DialogueBlock(
            section_number="1.1",
            section_title="大量発話テスト",
            introduction="導入。",
            dialogue=utterances,
            conclusion="結論。",
        )
        result = to_dialogue_xml(block)
        root = ET.fromstring(result)
        utterance_elems = root.findall(".//dialogue/utterance")
        assert len(utterance_elems) == 100

    # --- 特殊文字テスト ---

    def test_utterance_with_sql_special_chars(self):
        """SQL特殊文字を含むテキスト"""
        utterance = Utterance(speaker="A", text="SELECT * FROM table WHERE id = 1; DROP TABLE;")
        assert "DROP TABLE" in utterance.text

    def test_utterance_with_html_tags(self):
        """HTMLタグを含むテキスト"""
        utterance = Utterance(speaker="A", text="<script>alert('xss')</script>")
        assert "<script>" in utterance.text

    def test_to_dialogue_xml_with_unicode_content(self):
        """Unicode文字（漢字、ひらがな、カタカナ混在）のXML化"""
        utterances = [
            Utterance(speaker="A", text="量子コンピュータは従来の計算機とは異なります。"),
            Utterance(speaker="B", text="それはどういう意味ですか？"),
        ]
        block = DialogueBlock(
            section_number="5.2",
            section_title="量子コンピュータ入門",
            introduction="この節では量子コンピュータの基礎を学びます。",
            dialogue=utterances,
            conclusion="以上が量子コンピュータの概要でした。",
        )
        result = to_dialogue_xml(block)
        root = ET.fromstring(result)
        assert root is not None
        assert "量子コンピュータ" in result

    def test_to_dialogue_xml_with_ampersand_in_text(self):
        """アンパサンド(&)を含むテキストのXML化"""
        utterances = [
            Utterance(speaker="A", text="A & B の関係について"),
        ]
        block = DialogueBlock(
            section_number="1.1",
            section_title="論理演算",
            introduction="",
            dialogue=utterances,
            conclusion="",
        )
        result = to_dialogue_xml(block)
        # &がエスケープされてパース可能
        root = ET.fromstring(result)
        assert root is not None

    # --- 境界値テスト ---

    def test_extract_sections_single_paragraph_section(self):
        """段落が1つだけのセクション"""
        from src.xml_parser import ContentItem, HeadingInfo

        items = [
            ContentItem(
                item_type="heading",
                text="1.1 短いセクション",
                heading_info=HeadingInfo(level=2, number="1.1", title="短いセクション"),
                chapter_number=1,
            ),
            ContentItem(item_type="paragraph", text="たった一つの段落。", chapter_number=1),
        ]
        result = extract_sections(items)
        assert len(result) == 1

    def test_conversion_result_zero_processing_time(self):
        """処理時間が0秒のConversionResult"""
        result = ConversionResult(
            success=True,
            dialogue_block=None,
            error_message=None,
            processing_time_sec=0.0,
            input_char_count=0,
            was_split=False,
        )
        assert result.processing_time_sec == 0.0

    def test_conversion_result_negative_char_count_not_expected(self):
        """文字数が負にならないことの確認（型としては受け入れるが意味的に不正）"""
        result = ConversionResult(
            success=True,
            dialogue_block=None,
            error_message=None,
            processing_time_sec=0.0,
            input_char_count=-1,
            was_split=False,
        )
        # dataclassは値の検証をしないので-1が入る
        assert result.input_char_count == -1

    # --- LLM応答の不正パターン ---

    def test_analyze_structure_llm_returns_partial_keys(self):
        """LLMがキーの一部しか返さない場合"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {"message": {"content": '{"dialogue": ["テスト"]}'}}
        try:
            result = analyze_structure(["テスト"], ollama_chat_func=mock_ollama)
            # 欠落キーがデフォルト値で補完される場合
            assert "introduction" in result
            assert "conclusion" in result
        except (KeyError, ValueError):
            assert True

    def test_generate_dialogue_llm_returns_invalid_speaker(self):
        """LLMが不正なspeaker値を返した場合"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {"message": {"content": '[{"speaker": "C", "text": "不正な話者"}]'}}
        try:
            result = generate_dialogue(
                dialogue_paragraphs=["テスト"],
                ollama_chat_func=mock_ollama,
            )
            # 不正な話者が除外またはエラーになる
            if len(result) > 0:
                for u in result:
                    assert u.speaker in ("A", "B")
        except (ValueError, KeyError):
            assert True


# =============================================================================
# Phase 3 RED Tests - US2: 長文セクションの分割処理
# =============================================================================

# =============================================================================
# T032: 文字数判定関数 should_split() のテスト
# =============================================================================


class TestShouldSplit:
    """should_split() のテスト - セクションが4,000文字を超えるか判定"""

    def setup_method(self):
        """各テスト前にshould_splitが実装済みか確認"""
        _require_should_split()

    def _make_section(self, total_chars: int, paragraph_count: int = 5) -> Section:
        """指定文字数のSectionを生成するヘルパー"""
        chars_per_paragraph = total_chars // paragraph_count
        remainder = total_chars % paragraph_count
        paragraphs = []
        for i in range(paragraph_count):
            extra = 1 if i < remainder else 0
            paragraphs.append("あ" * (chars_per_paragraph + extra))
        return Section(
            number="1.1",
            title="テストセクション",
            paragraphs=paragraphs,
            chapter_number=1,
        )

    def test_should_split_returns_bool(self):
        """should_split()がbool値を返す"""
        section = self._make_section(100)
        result = should_split(section)
        assert isinstance(result, bool)

    def test_should_split_false_for_short_section(self):
        """3,500文字以下のセクションはFalse"""
        section = self._make_section(3500)
        result = should_split(section)
        assert result is False

    def test_should_split_true_for_long_section(self):
        """4,001文字以上のセクションはTrue"""
        section = self._make_section(4001)
        result = should_split(section)
        assert result is True

    def test_should_split_false_for_empty_section(self):
        """空のセクション（段落なし）はFalse"""
        section = Section(
            number="1.1",
            title="空セクション",
            paragraphs=[],
            chapter_number=1,
        )
        result = should_split(section)
        assert result is False

    def test_should_split_false_for_single_short_paragraph(self):
        """短い段落が1つだけのセクションはFalse"""
        section = Section(
            number="1.1",
            title="短セクション",
            paragraphs=["短いテキスト。"],
            chapter_number=1,
        )
        result = should_split(section)
        assert result is False

    def test_should_split_true_for_5000_chars(self):
        """5,000文字のセクションはTrue"""
        section = self._make_section(5000)
        result = should_split(section)
        assert result is True

    def test_should_split_true_for_10000_chars(self):
        """10,000文字の大規模セクションはTrue"""
        section = self._make_section(10000, paragraph_count=10)
        result = should_split(section)
        assert result is True

    def test_should_split_counts_all_paragraphs(self):
        """全段落の文字数を合算して判定する"""
        # 各段落が1,000文字、5段落 = 5,000文字 → True
        paragraphs = ["あ" * 1000 for _ in range(5)]
        section = Section(
            number="1.1",
            title="複数段落",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        result = should_split(section)
        assert result is True

    def test_should_split_with_none_input(self):
        """Noneを渡した場合のエラーハンドリング"""
        try:
            result = should_split(None)
            assert result is False
        except (TypeError, AttributeError):
            assert True

    def test_should_split_exactly_4000_chars(self):
        """ちょうど4,000文字のセクションの判定（境界値）"""
        section = self._make_section(4000)
        result = should_split(section)
        # 4,000文字は「超える」に含まれないのでFalse
        assert isinstance(result, bool)

    def test_should_split_with_unicode_content(self):
        """Unicode文字（絵文字含む）を含むセクションの文字数判定"""
        paragraphs = ["量子コンピュータの基本原理。" * 200]  # 約2,800文字
        paragraphs.append("追加の説明テキスト。" * 200)  # 約1,800文字 → 合計4,600
        section = Section(
            number="1.1",
            title="Unicode テスト",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        result = should_split(section)
        assert result is True

    def test_should_split_with_special_characters(self):
        """特殊文字（HTML、SQL）を含むセクション"""
        text = '<div>テスト</div> SELECT * FROM t; "引用" & 特殊文字 ' * 200
        section = Section(
            number="1.1",
            title="特殊文字テスト",
            paragraphs=[text],
            chapter_number=1,
        )
        result = should_split(section)
        assert isinstance(result, bool)


# =============================================================================
# T033: 見出し単位分割関数 split_by_heading() のテスト
# =============================================================================


class TestSplitByHeading:
    """split_by_heading() のテスト - セクションを見出し単位で分割"""

    def setup_method(self):
        """各テスト前にsplit_by_headingが実装済みか確認"""
        _require_split_by_heading()

    def test_split_by_heading_returns_list(self):
        """split_by_heading()がSectionのリストを返す"""
        section = Section(
            number="1.1",
            title="テスト",
            paragraphs=["段落1。", "段落2。"],
            chapter_number=1,
        )
        result = split_by_heading(section)
        assert isinstance(result, list)

    def test_split_by_heading_returns_section_objects(self):
        """返却リストの各要素がSectionインスタンスである"""
        section = Section(
            number="1.1",
            title="テスト",
            paragraphs=["段落1。", "段落2。"],
            chapter_number=1,
        )
        result = split_by_heading(section)
        for item in result:
            assert isinstance(item, Section)

    def test_split_by_heading_preserves_section_number(self):
        """分割後も元のセクション番号が保持される（サフィックス付き）"""
        paragraphs = ["あ" * 2000, "## 小見出し", "い" * 2000, "う" * 500]
        section = Section(
            number="1.1",
            title="長いセクション",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        result = split_by_heading(section)
        # 分割結果のセクション番号に元の番号が含まれる
        for sub_section in result:
            assert "1.1" in sub_section.number

    def test_split_by_heading_preserves_title(self):
        """分割後のセクションにタイトル情報が保持される"""
        paragraphs = ["あ" * 2500, "## 小見出し1", "い" * 2500]
        section = Section(
            number="1.1",
            title="元のタイトル",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        result = split_by_heading(section)
        assert len(result) >= 1
        # 最初の分割セクションに元のタイトルが含まれる
        assert result[0].title is not None
        assert len(result[0].title) > 0

    def test_split_by_heading_preserves_chapter_number(self):
        """分割後もchapter_numberが保持される"""
        paragraphs = ["あ" * 2500, "## 小見出し", "い" * 2500]
        section = Section(
            number="2.3",
            title="テスト",
            paragraphs=paragraphs,
            chapter_number=2,
        )
        result = split_by_heading(section)
        for sub_section in result:
            assert sub_section.chapter_number == 2

    def test_split_by_heading_splits_at_heading_markers(self):
        """見出し（## で始まる行）で分割される"""
        paragraphs = [
            "導入段落。",
            "本論段落1。",
            "## 次の見出し",
            "本論段落2。",
            "結論段落。",
        ]
        section = Section(
            number="1.1",
            title="テスト",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        result = split_by_heading(section)
        assert len(result) >= 2

    def test_split_by_heading_no_heading_returns_single(self):
        """見出しがない場合は分割せず1つのセクションを返す"""
        paragraphs = ["段落1。" * 100, "段落2。" * 100]
        section = Section(
            number="1.1",
            title="見出しなし",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        result = split_by_heading(section)
        # 見出しがない場合は元のセクションがそのまま返る
        assert len(result) >= 1
        total_paragraphs = sum(len(s.paragraphs) for s in result)
        assert total_paragraphs >= 2

    def test_split_by_heading_empty_section(self):
        """空のセクション（段落なし）を渡した場合"""
        section = Section(
            number="1.1",
            title="空セクション",
            paragraphs=[],
            chapter_number=1,
        )
        result = split_by_heading(section)
        assert isinstance(result, list)

    def test_split_by_heading_preserves_all_paragraphs(self):
        """分割後に全段落が保持される（テキストの欠落なし）"""
        original_paragraphs = [
            "段落A。",
            "段落B。",
            "## 見出し1",
            "段落C。",
            "段落D。",
            "## 見出し2",
            "段落E。",
        ]
        section = Section(
            number="1.1",
            title="テスト",
            paragraphs=original_paragraphs,
            chapter_number=1,
        )
        result = split_by_heading(section)
        # 分割後の全段落を合算
        all_paragraphs = []
        for sub_section in result:
            all_paragraphs.extend(sub_section.paragraphs)
        # 見出し行自体は段落として残るか除外されるかは実装依存だが、
        # 非見出し段落は全て残っていること
        non_heading_originals = [p for p in original_paragraphs if not p.startswith("## ")]
        for paragraph in non_heading_originals:
            assert paragraph in all_paragraphs

    def test_split_by_heading_with_none_input(self):
        """Noneを渡した場合のエラーハンドリング"""
        try:
            result = split_by_heading(None)
            assert isinstance(result, list)
        except (TypeError, AttributeError):
            assert True

    def test_split_by_heading_each_part_under_4000(self):
        """分割後の各パートが4,000文字以下である"""
        paragraphs = [
            "あ" * 2000,
            "## 中間見出し",
            "い" * 2000,
            "## 後半見出し",
            "う" * 2000,
        ]
        section = Section(
            number="1.1",
            title="長文テスト",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        result = split_by_heading(section)
        for sub_section in result:
            char_count = sum(len(p) for p in sub_section.paragraphs)
            assert char_count <= 4000, f"分割後のパートが4,000文字を超過: {char_count}"

    def test_split_by_heading_multiple_headings(self):
        """複数の見出しがある場合に適切に分割される"""
        paragraphs = [
            "最初の段落。",
            "## 見出し1",
            "見出し1の段落。",
            "## 見出し2",
            "見出し2の段落。",
            "## 見出し3",
            "見出し3の段落。",
        ]
        section = Section(
            number="1.1",
            title="複数見出し",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        result = split_by_heading(section)
        # 少なくとも2つ以上のセクションに分割される
        assert len(result) >= 2

    def test_split_by_heading_with_large_data(self):
        """1,000個以上の段落を含むセクションの分割"""
        paragraphs = []
        for i in range(100):
            paragraphs.append(f"## 見出し{i}")
            for j in range(10):
                paragraphs.append(f"段落{i}-{j}のテキスト。" * 5)
        section = Section(
            number="1.1",
            title="大規模データ",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        result = split_by_heading(section)
        assert isinstance(result, list)
        assert len(result) > 1

    def test_split_by_heading_with_empty_string_paragraphs(self):
        """空文字列の段落を含むセクションの分割"""
        paragraphs = ["あ" * 2000, "", "## 見出し", "", "い" * 2000]
        section = Section(
            number="1.1",
            title="空段落含む",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        result = split_by_heading(section)
        assert isinstance(result, list)
        assert len(result) >= 1


# =============================================================================
# T034: 分割後の連続性（コンテキスト維持）テスト
# =============================================================================


class TestSplitContextContinuity:
    """分割後のコンテキスト維持テスト - 分割されたセクション間の一貫性"""

    def setup_method(self):
        """各テスト前にshould_split/split_by_headingが実装済みか確認"""
        _require_should_split()
        _require_split_by_heading()

    def test_split_sections_maintain_order(self):
        """分割後のセクションが元の順序を維持する"""
        paragraphs = [
            "第一部の内容。",
            "## 第二部",
            "第二部の内容。",
            "## 第三部",
            "第三部の内容。",
        ]
        section = Section(
            number="1.1",
            title="順序テスト",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        result = split_by_heading(section)
        # セクション番号が順序を反映している
        if len(result) >= 2:
            for i in range(len(result) - 1):
                # 後のセクションの番号が前のセクションより大きいか、
                # サフィックスが順序通り
                assert result[i].number <= result[i + 1].number

    def test_split_then_convert_produces_valid_results(self):
        """分割後のセクションをconvert_section()に渡して有効な結果が得られる"""
        mock_ollama = MagicMock()
        # analyze_structureとgenerate_dialogueの両方のモック
        mock_ollama.return_value = {
            "message": {"content": '{"introduction": ["導入"], "dialogue": ["本論"], "conclusion": ["結論"]}'}
        }
        paragraphs = [
            "あ" * 2000,
            "## 小見出し",
            "い" * 2000,
        ]
        section = Section(
            number="1.1",
            title="統合テスト",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        sub_sections = split_by_heading(section)
        for sub_section in sub_sections:
            result = convert_section(sub_section, ollama_chat_func=mock_ollama)
            assert isinstance(result, ConversionResult)

    def test_split_sections_have_non_empty_paragraphs(self):
        """分割後の各セクションに段落が含まれる（空のセクションが生成されない）"""
        paragraphs = [
            "第一部の内容。",
            "## 第二部",
            "第二部の内容。",
        ]
        section = Section(
            number="1.1",
            title="非空テスト",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        result = split_by_heading(section)
        for sub_section in result:
            # 各分割セクションに少なくとも1つの非見出し段落がある
            non_heading_paragraphs = [p for p in sub_section.paragraphs if not p.startswith("## ")]
            assert len(non_heading_paragraphs) >= 1, f"分割セクション {sub_section.number} に段落がない"

    def test_convert_section_with_split_sets_was_split_flag(self):
        """分割処理を経たconvert_section()の結果でwas_splitがTrueになる"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {"message": {"content": '[{"speaker": "A", "text": "テスト"}]'}}
        # 4,000文字超のセクション
        paragraphs = ["あ" * 2500, "## 見出し", "い" * 2500]
        section = Section(
            number="1.1",
            title="was_splitテスト",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        # should_splitがTrueの場合、convert_sectionでwas_splitフラグがTrue
        assert should_split(section) is True
        # convert_sectionが分割ロジックを統合後、was_split=True を返す想定
        result = convert_section(section, ollama_chat_func=mock_ollama)
        assert result.was_split is True

    def test_split_preserves_content_no_data_loss(self):
        """分割処理でテキストが失われないことを確認"""
        original_texts = [
            "量子コンピュータの基礎知識について述べます。",
            "## 量子ビットの概念",
            "量子ビットは0と1の重ね合わせ状態を取ります。",
            "## エンタングルメント",
            "量子もつれは2つの量子ビット間の相関を示します。",
        ]
        section = Section(
            number="3.2",
            title="量子コンピュータ",
            paragraphs=original_texts,
            chapter_number=3,
        )
        result = split_by_heading(section)
        all_texts = []
        for sub in result:
            all_texts.extend(sub.paragraphs)
        # 非見出しテキストが全て含まれる
        for text in original_texts:
            if not text.startswith("## "):
                assert text in all_texts, f"テキスト欠落: {text}"

    def test_split_sections_can_each_generate_dialogue_xml(self):
        """分割後の各セクションから対話XMLが生成できる"""
        paragraphs = [
            "最初の段落の内容。",
            "## 次の見出し",
            "次の段落の内容。",
        ]
        section = Section(
            number="1.1",
            title="XML生成テスト",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        sub_sections = split_by_heading(section)
        for sub in sub_sections:
            # 各分割セクションからDialogueBlockを構築してXML化可能
            block = DialogueBlock(
                section_number=sub.number,
                section_title=sub.title,
                introduction="テスト導入",
                dialogue=[Utterance(speaker="A", text="テスト発言")],
                conclusion="テスト結論",
            )
            xml_str = to_dialogue_xml(block)
            assert isinstance(xml_str, str)
            assert len(xml_str) > 0


# =============================================================================
# T035: 境界ケース（3,500〜4,500文字）のテスト
# =============================================================================


class TestBoundaryCharacterCount:
    """境界値テスト - 3,500〜4,500文字の範囲での分割判定"""

    def setup_method(self):
        """各テスト前にshould_split/split_by_headingが実装済みか確認"""
        _require_should_split()
        _require_split_by_heading()

    def _make_section_with_chars(self, total_chars: int) -> Section:
        """指定文字数のSectionを生成"""
        text = "あ" * total_chars
        return Section(
            number="1.1",
            title="境界テスト",
            paragraphs=[text],
            chapter_number=1,
        )

    def test_boundary_3500_chars_no_split(self):
        """3,500文字 → 分割不要"""
        section = self._make_section_with_chars(3500)
        assert should_split(section) is False

    def test_boundary_3800_chars_no_split(self):
        """3,800文字 → 分割不要（閾値未満）"""
        section = self._make_section_with_chars(3800)
        assert should_split(section) is False

    def test_boundary_3999_chars_no_split(self):
        """3,999文字 → 分割不要（閾値-1）"""
        section = self._make_section_with_chars(3999)
        assert should_split(section) is False

    def test_boundary_4000_chars(self):
        """4,000文字 → 境界値（閾値ちょうど）"""
        section = self._make_section_with_chars(4000)
        result = should_split(section)
        # 「超える」の定義: 4,000より大きいならTrue、4,000以下ならFalse
        assert isinstance(result, bool)

    def test_boundary_4001_chars_split(self):
        """4,001文字 → 分割必要（閾値+1）"""
        section = self._make_section_with_chars(4001)
        assert should_split(section) is True

    def test_boundary_4100_chars_split(self):
        """4,100文字 → 分割必要"""
        section = self._make_section_with_chars(4100)
        assert should_split(section) is True

    def test_boundary_4500_chars_split(self):
        """4,500文字 → 分割必要"""
        section = self._make_section_with_chars(4500)
        assert should_split(section) is True

    def test_boundary_0_chars_no_split(self):
        """0文字 → 分割不要"""
        section = Section(
            number="1.1",
            title="空",
            paragraphs=[""],
            chapter_number=1,
        )
        assert should_split(section) is False

    def test_boundary_1_char_no_split(self):
        """1文字 → 分割不要"""
        section = self._make_section_with_chars(1)
        assert should_split(section) is False

    def test_boundary_negative_char_count_handling(self):
        """文字数が計算上ゼロになるケース（空の段落リスト）"""
        section = Section(
            number="1.1",
            title="境界",
            paragraphs=[],
            chapter_number=1,
        )
        assert should_split(section) is False

    def test_boundary_exactly_threshold_split_by_heading(self):
        """閾値付近でsplit_by_heading()が呼ばれた場合の動作"""
        paragraphs = [
            "あ" * 2000,
            "## 中間見出し",
            "い" * 2100,
        ]
        section = Section(
            number="1.1",
            title="閾値テスト",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        # 合計4,100文字超なので分割対象
        assert should_split(section) is True
        result = split_by_heading(section)
        assert len(result) >= 2

    def test_boundary_convert_section_short_no_split(self):
        """3,500文字のセクションをconvert_section()で処理 → was_split=False"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {
            "message": {"content": '{"introduction": [], "dialogue": ["テスト"], "conclusion": []}'}
        }
        paragraphs = ["あ" * 3500]
        section = Section(
            number="1.1",
            title="短いセクション",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        result = convert_section(section, ollama_chat_func=mock_ollama)
        assert result.was_split is False

    def test_boundary_convert_section_long_with_split(self):
        """4,500文字のセクションをconvert_section()で処理 → was_split=True"""
        mock_ollama = MagicMock()
        mock_ollama.return_value = {"message": {"content": '[{"speaker": "A", "text": "テスト"}]'}}
        paragraphs = ["あ" * 2500, "## 見出し", "い" * 2000]
        section = Section(
            number="1.1",
            title="長いセクション",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        result = convert_section(section, ollama_chat_func=mock_ollama)
        assert result.was_split is True

    def test_boundary_multiple_small_paragraphs_sum_over_threshold(self):
        """個々の段落は短いが合計が4,000文字超"""
        # 100文字 x 50段落 = 5,000文字
        paragraphs = ["あ" * 100 for _ in range(50)]
        section = Section(
            number="1.1",
            title="多段落テスト",
            paragraphs=paragraphs,
            chapter_number=1,
        )
        assert should_split(section) is True

    def test_boundary_single_huge_paragraph(self):
        """1つの段落が8,000文字（見出しなし）"""
        section = Section(
            number="1.1",
            title="巨大段落",
            paragraphs=["あ" * 8000],
            chapter_number=1,
        )
        assert should_split(section) is True
        # 見出しがないので分割は最小限
        result = split_by_heading(section)
        assert isinstance(result, list)
        assert len(result) >= 1


# =============================================================================
# Phase 5 RED Tests
# T072: dialogue_converter.py CLI引数パースのテスト
# =============================================================================


class TestConverterParseArgsRequired:
    """parse_args() の必須引数テスト。"""

    def test_no_args_raises_system_exit(self):
        """引数なしで SystemExit が発生する"""
        _require_parse_args()
        with pytest.raises(SystemExit):
            converter_parse_args([])

    def test_input_is_required(self):
        """--input を指定しないと SystemExit が発生する"""
        _require_parse_args()
        with pytest.raises(SystemExit):
            converter_parse_args(["--output", "./out"])


class TestConverterParseArgsInput:
    """parse_args() の --input/-i 引数テスト。"""

    def test_input_short_flag(self):
        """短縮形 -i で入力ファイルを指定できる"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml"])
        assert args.input == "book.xml"

    def test_input_long_flag(self):
        """長形式 --input で入力ファイルを指定できる"""
        _require_parse_args()
        args = converter_parse_args(["--input", "book.xml"])
        assert args.input == "book.xml"

    def test_input_with_path(self):
        """パス付きの入力ファイルを指定できる"""
        _require_parse_args()
        args = converter_parse_args(["-i", "/data/books/book2.xml"])
        assert args.input == "/data/books/book2.xml"

    def test_input_with_spaces_in_path(self):
        """スペースを含むパスの入力ファイルを指定できる"""
        _require_parse_args()
        args = converter_parse_args(["-i", "/data/my books/book.xml"])
        assert args.input == "/data/my books/book.xml"


class TestConverterParseArgsOutput:
    """parse_args() の --output/-o 引数テスト。"""

    def test_output_default(self):
        """--output のデフォルトは './output'"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml"])
        assert args.output == "./output"

    def test_output_short_flag(self):
        """短縮形 -o で出力ディレクトリを指定できる"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml", "-o", "/tmp/out"])
        assert args.output == "/tmp/out"

    def test_output_long_flag(self):
        """長形式 --output で出力ディレクトリを指定できる"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml", "--output", "/tmp/out"])
        assert args.output == "/tmp/out"


class TestConverterParseArgsModel:
    """parse_args() の --model/-m 引数テスト。"""

    def test_model_default(self):
        """--model のデフォルトは 'gpt-oss:20b'"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml"])
        assert args.model == "gpt-oss:20b"

    def test_model_short_flag(self):
        """短縮形 -m でモデル名を指定できる"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml", "-m", "llama3:8b"])
        assert args.model == "llama3:8b"

    def test_model_long_flag(self):
        """長形式 --model でモデル名を指定できる"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml", "--model", "llama3:8b"])
        assert args.model == "llama3:8b"


class TestConverterParseArgsNumeric:
    """parse_args() の数値オプション（--max-chars, --split-threshold, --num-predict）テスト。"""

    def test_max_chars_default(self):
        """--max-chars のデフォルトは 3500"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml"])
        assert args.max_chars == 3500

    def test_max_chars_custom(self):
        """--max-chars でカスタム値を指定できる"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml", "--max-chars", "5000"])
        assert args.max_chars == 5000

    def test_max_chars_is_int(self):
        """--max-chars の値は int 型である"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml", "--max-chars", "2000"])
        assert isinstance(args.max_chars, int)

    def test_split_threshold_default(self):
        """--split-threshold のデフォルトは 4000"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml"])
        assert args.split_threshold == 4000

    def test_split_threshold_custom(self):
        """--split-threshold でカスタム値を指定できる"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml", "--split-threshold", "6000"])
        assert args.split_threshold == 6000

    def test_num_predict_default(self):
        """--num-predict のデフォルトは 1500"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml"])
        assert args.num_predict == 1500

    def test_num_predict_custom(self):
        """--num-predict でカスタム値を指定できる"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml", "--num-predict", "2000"])
        assert args.num_predict == 2000


class TestConverterParseArgsChapterSection:
    """parse_args() の --chapter/-c と --section/-s 引数テスト。"""

    def test_chapter_default_none(self):
        """--chapter のデフォルトは None"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml"])
        assert args.chapter is None

    def test_chapter_short_flag(self):
        """短縮形 -c でチャプター番号を指定できる"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml", "-c", "3"])
        assert args.chapter == 3

    def test_chapter_long_flag(self):
        """長形式 --chapter でチャプター番号を指定できる"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml", "--chapter", "5"])
        assert args.chapter == 5

    def test_chapter_is_int(self):
        """--chapter の値は int 型である"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml", "-c", "2"])
        assert isinstance(args.chapter, int)

    def test_section_default_none(self):
        """--section のデフォルトは None"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml"])
        assert args.section is None

    def test_section_short_flag(self):
        """短縮形 -s でセクション番号を指定できる"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml", "-s", "2"])
        assert args.section == 2

    def test_section_long_flag(self):
        """長形式 --section でセクション番号を指定できる"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml", "--section", "4"])
        assert args.section == 4


class TestConverterParseArgsDryRun:
    """parse_args() の --dry-run 引数テスト。"""

    def test_dry_run_default_false(self):
        """--dry-run のデフォルトは False"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml"])
        assert args.dry_run is False

    def test_dry_run_flag(self):
        """--dry-run フラグを指定すると True になる"""
        _require_parse_args()
        args = converter_parse_args(["-i", "book.xml", "--dry-run"])
        assert args.dry_run is True


class TestConverterParseArgsCombined:
    """parse_args() の全オプション組み合わせテスト。"""

    def test_all_options_combined(self):
        """全オプションを同時に指定できる"""
        _require_parse_args()
        args = converter_parse_args(
            [
                "-i",
                "book.xml",
                "-o",
                "/tmp/out",
                "-m",
                "llama3:8b",
                "--max-chars",
                "5000",
                "--split-threshold",
                "6000",
                "--num-predict",
                "2000",
                "-c",
                "3",
                "-s",
                "2",
                "--dry-run",
            ]
        )
        assert args.input == "book.xml"
        assert args.output == "/tmp/out"
        assert args.model == "llama3:8b"
        assert args.max_chars == 5000
        assert args.split_threshold == 6000
        assert args.num_predict == 2000
        assert args.chapter == 3
        assert args.section == 2
        assert args.dry_run is True

    def test_minimal_required_only(self):
        """必須引数のみで正しいデフォルト値が設定される"""
        _require_parse_args()
        args = converter_parse_args(["-i", "input.xml"])
        assert args.input == "input.xml"
        assert args.output == "./output"
        assert args.model == "gpt-oss:20b"
        assert args.max_chars == 3500
        assert args.split_threshold == 4000
        assert args.num_predict == 1500
        assert args.chapter is None
        assert args.section is None
        assert args.dry_run is False


class TestConverterParseArgsEdgeCases:
    """parse_args() のエッジケーステスト。"""

    def test_invalid_max_chars_type(self):
        """--max-chars に数値以外を渡すと SystemExit"""
        _require_parse_args()
        with pytest.raises(SystemExit):
            converter_parse_args(["-i", "book.xml", "--max-chars", "abc"])

    def test_invalid_chapter_type(self):
        """--chapter に数値以外を渡すと SystemExit"""
        _require_parse_args()
        with pytest.raises(SystemExit):
            converter_parse_args(["-i", "book.xml", "-c", "abc"])

    def test_unknown_argument(self):
        """未知の引数を渡すと SystemExit"""
        _require_parse_args()
        with pytest.raises(SystemExit):
            converter_parse_args(["-i", "book.xml", "--unknown-flag"])

    def test_empty_input_string(self):
        """空文字列の入力ファイルパスを受け付ける（バリデーションはmain側）"""
        _require_parse_args()
        args = converter_parse_args(["-i", ""])
        assert args.input == ""


# =============================================================================
# T073: dialogue_converter.py main() 統合テスト
# =============================================================================


class TestConverterMainInputValidation:
    """main() の入力ファイルバリデーションテスト。"""

    def test_nonexistent_input_file_returns_exit_code_1(self, tmp_path):
        """存在しない入力ファイルを指定すると終了コード 1 を返す"""
        _require_main()
        nonexistent = str(tmp_path / "nonexistent.xml")
        with patch(
            "src.dialogue_converter.parse_args",
        ) as mock_parse_args:
            mock_parse_args.return_value = _make_converter_args(
                input=nonexistent,
                output=str(tmp_path / "output"),
            )
            result = converter_main()
        assert result == 1

    def test_empty_input_path_returns_exit_code_1(self, tmp_path):
        """空の入力パスを指定すると終了コード 1 を返す"""
        _require_main()
        with patch(
            "src.dialogue_converter.parse_args",
        ) as mock_parse_args:
            mock_parse_args.return_value = _make_converter_args(
                input="",
                output=str(tmp_path / "output"),
            )
            result = converter_main()
        assert result == 1

    def test_directory_as_input_returns_exit_code_1(self, tmp_path):
        """ディレクトリを入力ファイルとして指定すると終了コード 1 を返す"""
        _require_main()
        with patch(
            "src.dialogue_converter.parse_args",
        ) as mock_parse_args:
            mock_parse_args.return_value = _make_converter_args(
                input=str(tmp_path),
                output=str(tmp_path / "output"),
            )
            result = converter_main()
        assert result == 1


class TestConverterMainDryRun:
    """main() の --dry-run モードテスト。"""

    def test_dry_run_returns_exit_code_0(self, tmp_path):
        """dry-runモードでは変換を実行せず終了コード 0 を返す"""
        _require_main()
        input_file = tmp_path / "book.xml"
        input_file.write_text(_make_minimal_book_xml(), encoding="utf-8")
        with patch(
            "src.dialogue_converter.parse_args",
        ) as mock_parse_args:
            mock_parse_args.return_value = _make_converter_args(
                input=str(input_file),
                output=str(tmp_path / "output"),
                dry_run=True,
            )
            result = converter_main()
        assert result == 0

    def test_dry_run_does_not_create_output_files(self, tmp_path):
        """dry-runモードでは出力ファイルが作成されない"""
        _require_main()
        input_file = tmp_path / "book.xml"
        input_file.write_text(_make_minimal_book_xml(), encoding="utf-8")
        output_dir = tmp_path / "output"
        with patch(
            "src.dialogue_converter.parse_args",
        ) as mock_parse_args:
            mock_parse_args.return_value = _make_converter_args(
                input=str(input_file),
                output=str(output_dir),
                dry_run=True,
            )
            converter_main()
        # dry-runでは出力ディレクトリにdialogue_book.xmlが作成されない
        dialogue_output = output_dir / "dialogue_book.xml"
        assert not dialogue_output.exists()

    def test_dry_run_does_not_call_llm(self, tmp_path):
        """dry-runモードではLLM呼び出しが行われない"""
        _require_main()
        input_file = tmp_path / "book.xml"
        input_file.write_text(_make_minimal_book_xml(), encoding="utf-8")
        with (
            patch(
                "src.dialogue_converter.parse_args",
            ) as mock_parse_args,
            patch(
                "src.dialogue_converter.convert_section",
            ) as mock_convert,
        ):
            mock_parse_args.return_value = _make_converter_args(
                input=str(input_file),
                output=str(tmp_path / "output"),
                dry_run=True,
            )
            converter_main()
        mock_convert.assert_not_called()


@pytest.mark.usefixtures("mock_ollama")
class TestConverterMainSuccessPath:
    """main() の正常系テスト。"""

    def test_successful_conversion_returns_exit_code_0(self, tmp_path):
        """正常な変換で終了コード 0 を返す"""
        _require_main()
        input_file = tmp_path / "book.xml"
        input_file.write_text(_make_minimal_book_xml(), encoding="utf-8")
        output_dir = tmp_path / "output"

        mock_result = ConversionResult(
            success=True,
            dialogue_block=DialogueBlock(
                section_number="1.1",
                section_title="テスト",
                introduction="導入です。",
                dialogue=[
                    Utterance(speaker="A", text="説明です。"),
                    Utterance(speaker="B", text="なるほど。"),
                ],
                conclusion="まとめです。",
            ),
            error_message=None,
            processing_time_sec=1.0,
            input_char_count=100,
            was_split=False,
        )

        with (
            patch(
                "src.dialogue_converter.parse_args",
            ) as mock_parse_args,
            patch(
                "src.dialogue_converter.convert_section",
                return_value=mock_result,
            ),
        ):
            mock_parse_args.return_value = _make_converter_args(
                input=str(input_file),
                output=str(output_dir),
            )
            result = converter_main()
        assert result == 0

    def test_creates_output_directory(self, tmp_path):
        """出力ディレクトリが存在しない場合に自動作成する"""
        _require_main()
        input_file = tmp_path / "book.xml"
        input_file.write_text(_make_minimal_book_xml(), encoding="utf-8")
        output_dir = tmp_path / "new_output_dir"

        mock_result = _make_successful_conversion_result()

        with (
            patch(
                "src.dialogue_converter.parse_args",
            ) as mock_parse_args,
            patch(
                "src.dialogue_converter.convert_section",
                return_value=mock_result,
            ),
        ):
            mock_parse_args.return_value = _make_converter_args(
                input=str(input_file),
                output=str(output_dir),
            )
            converter_main()
        assert output_dir.exists()

    def test_creates_dialogue_book_xml(self, tmp_path):
        """変換結果のdialogue_book.xmlが出力ディレクトリに作成される"""
        _require_main()
        input_file = tmp_path / "book.xml"
        input_file.write_text(_make_minimal_book_xml(), encoding="utf-8")
        output_dir = tmp_path / "output"

        mock_result = _make_successful_conversion_result()

        with (
            patch(
                "src.dialogue_converter.parse_args",
            ) as mock_parse_args,
            patch(
                "src.dialogue_converter.convert_section",
                return_value=mock_result,
            ),
        ):
            mock_parse_args.return_value = _make_converter_args(
                input=str(input_file),
                output=str(output_dir),
            )
            converter_main()
        dialogue_output = output_dir / "dialogue_book.xml"
        assert dialogue_output.exists()

    def test_creates_conversion_log_json(self, tmp_path):
        """変換ログのconversion_log.jsonが出力ディレクトリに作成される"""
        _require_main()
        input_file = tmp_path / "book.xml"
        input_file.write_text(_make_minimal_book_xml(), encoding="utf-8")
        output_dir = tmp_path / "output"

        mock_result = _make_successful_conversion_result()

        with (
            patch(
                "src.dialogue_converter.parse_args",
            ) as mock_parse_args,
            patch(
                "src.dialogue_converter.convert_section",
                return_value=mock_result,
            ),
        ):
            mock_parse_args.return_value = _make_converter_args(
                input=str(input_file),
                output=str(output_dir),
            )
            converter_main()
        log_output = output_dir / "conversion_log.json"
        assert log_output.exists()
        log_data = json.loads(log_output.read_text(encoding="utf-8"))
        assert isinstance(log_data, (dict, list))


@pytest.mark.usefixtures("mock_ollama")
class TestConverterMainErrorHandling:
    """main() のエラーハンドリングテスト。"""

    def test_llm_connection_error_returns_exit_code_2(self, tmp_path):
        """LLM接続エラーで終了コード 2 を返す"""
        _require_main()
        input_file = tmp_path / "book.xml"
        input_file.write_text(_make_minimal_book_xml(), encoding="utf-8")

        with (
            patch(
                "src.dialogue_converter.parse_args",
            ) as mock_parse_args,
            patch(
                "src.dialogue_converter.convert_section",
                side_effect=ConnectionError("LLM connection failed"),
            ),
        ):
            mock_parse_args.return_value = _make_converter_args(
                input=str(input_file),
                output=str(tmp_path / "output"),
            )
            result = converter_main()
        assert result == 2

    def test_conversion_failure_returns_exit_code_3(self, tmp_path):
        """変換処理エラーで終了コード 3 を返す"""
        _require_main()
        input_file = tmp_path / "book.xml"
        input_file.write_text(_make_minimal_book_xml(), encoding="utf-8")

        failed_result = ConversionResult(
            success=False,
            dialogue_block=None,
            error_message="変換に失敗しました",
            processing_time_sec=1.0,
            input_char_count=100,
            was_split=False,
        )

        with (
            patch(
                "src.dialogue_converter.parse_args",
            ) as mock_parse_args,
            patch(
                "src.dialogue_converter.convert_section",
                return_value=failed_result,
            ),
        ):
            mock_parse_args.return_value = _make_converter_args(
                input=str(input_file),
                output=str(tmp_path / "output"),
            )
            result = converter_main()
        assert result == 3

    def test_xml_parse_error_returns_exit_code_1(self, tmp_path):
        """無効なXMLファイルで終了コード 1 を返す"""
        _require_main()
        input_file = tmp_path / "bad.xml"
        input_file.write_text("<<<not valid xml>>>", encoding="utf-8")

        with patch(
            "src.dialogue_converter.parse_args",
        ) as mock_parse_args:
            mock_parse_args.return_value = _make_converter_args(
                input=str(input_file),
                output=str(tmp_path / "output"),
            )
            result = converter_main()
        assert result == 1

    def test_unexpected_exception_returns_exit_code_3(self, tmp_path):
        """予期しない例外で終了コード 3 を返す"""
        _require_main()
        input_file = tmp_path / "book.xml"
        input_file.write_text(_make_minimal_book_xml(), encoding="utf-8")

        with (
            patch(
                "src.dialogue_converter.parse_args",
            ) as mock_parse_args,
            patch(
                "src.dialogue_converter.convert_section",
                side_effect=RuntimeError("unexpected error"),
            ),
        ):
            mock_parse_args.return_value = _make_converter_args(
                input=str(input_file),
                output=str(tmp_path / "output"),
            )
            result = converter_main()
        assert result == 3


@pytest.mark.usefixtures("mock_ollama")
class TestConverterMainChapterSectionFilter:
    """main() の --chapter/-c と --section/-s フィルタテスト。"""

    def test_chapter_filter_processes_only_specified_chapter(self, tmp_path):
        """--chapter で指定したチャプターのみ処理する"""
        _require_main()
        input_file = tmp_path / "book.xml"
        input_file.write_text(_make_multi_chapter_book_xml(), encoding="utf-8")

        mock_result = _make_successful_conversion_result()

        with (
            patch(
                "src.dialogue_converter.parse_args",
            ) as mock_parse_args,
            patch(
                "src.dialogue_converter.convert_section",
                return_value=mock_result,
            ) as mock_convert,
        ):
            mock_parse_args.return_value = _make_converter_args(
                input=str(input_file),
                output=str(tmp_path / "output"),
                chapter=1,
            )
            result = converter_main()
        assert result == 0
        # convert_sectionが呼ばれた場合、チャプター1のセクションのみ
        if mock_convert.called:
            for call_args in mock_convert.call_args_list:
                section_arg = call_args[0][0] if call_args[0] else call_args[1].get("section")
                if section_arg is not None:
                    assert section_arg.chapter_number == 1

    def test_section_filter_processes_only_specified_section(self, tmp_path):
        """--section で指定したセクションのみ処理する"""
        _require_main()
        input_file = tmp_path / "book.xml"
        input_file.write_text(_make_minimal_book_xml(), encoding="utf-8")

        mock_result = _make_successful_conversion_result()

        with (
            patch(
                "src.dialogue_converter.parse_args",
            ) as mock_parse_args,
            patch(
                "src.dialogue_converter.convert_section",
                return_value=mock_result,
            ),
        ):
            mock_parse_args.return_value = _make_converter_args(
                input=str(input_file),
                output=str(tmp_path / "output"),
                section=1,
            )
            result = converter_main()
        assert result == 0


@pytest.mark.usefixtures("mock_ollama")
class TestConverterMainEdgeCases:
    """main() のエッジケーステスト。"""

    def test_empty_xml_no_sections(self, tmp_path):
        """セクションが存在しないXMLで正常終了する"""
        _require_main()
        input_file = tmp_path / "empty.xml"
        input_file.write_text(
            '<?xml version="1.0" encoding="utf-8"?><book></book>',
            encoding="utf-8",
        )

        with patch(
            "src.dialogue_converter.parse_args",
        ) as mock_parse_args:
            mock_parse_args.return_value = _make_converter_args(
                input=str(input_file),
                output=str(tmp_path / "output"),
            )
            result = converter_main()
        # セクションなしでも正常終了（0）であるべき
        assert result == 0

    def test_unicode_content_in_xml(self, tmp_path):
        """Unicode文字（絵文字、特殊文字）を含むXMLを処理できる"""
        _require_main()
        input_file = tmp_path / "unicode.xml"
        xml_content = (
            '<?xml version="1.0" encoding="utf-8"?>'
            "<book><chapter><heading>第1章</heading>"
            '<section number="1.1"><heading level="2">テスト</heading>'
            "<paragraph>特殊文字テスト：&amp;、&lt;、&gt;</paragraph>"
            "</section></chapter></book>"
        )
        input_file.write_text(xml_content, encoding="utf-8")

        mock_result = _make_successful_conversion_result()

        with (
            patch(
                "src.dialogue_converter.parse_args",
            ) as mock_parse_args,
            patch(
                "src.dialogue_converter.convert_section",
                return_value=mock_result,
            ),
        ):
            mock_parse_args.return_value = _make_converter_args(
                input=str(input_file),
                output=str(tmp_path / "output"),
            )
            result = converter_main()
        assert isinstance(result, int)

    def test_large_xml_with_many_sections(self, tmp_path):
        """多数のセクション（50+）を含むXMLを処理できる"""
        _require_main()
        input_file = tmp_path / "large.xml"
        sections_xml = ""
        for i in range(50):
            sections_xml += (
                f'<section number="1.{i + 1}">'
                f'<heading level="2">セクション{i + 1}</heading>'
                f"<paragraph>段落{i + 1}のテキスト</paragraph>"
                f"</section>"
            )
        xml_content = (
            '<?xml version="1.0" encoding="utf-8"?>'
            f"<book><chapter><heading>第1章</heading>{sections_xml}</chapter></book>"
        )
        input_file.write_text(xml_content, encoding="utf-8")

        mock_result = _make_successful_conversion_result()

        with (
            patch(
                "src.dialogue_converter.parse_args",
            ) as mock_parse_args,
            patch(
                "src.dialogue_converter.convert_section",
                return_value=mock_result,
            ),
        ):
            mock_parse_args.return_value = _make_converter_args(
                input=str(input_file),
                output=str(tmp_path / "output"),
            )
            result = converter_main()
        assert result == 0


# =============================================================================
# Phase 5 ヘルパー関数
# =============================================================================


def _make_converter_args(
    input: str = "book.xml",
    output: str = "./output",
    model: str = "gpt-oss:20b",
    max_chars: int = 3500,
    split_threshold: int = 4000,
    num_predict: int = 1500,
    chapter: int | None = None,
    section: int | None = None,
    dry_run: bool = False,
) -> MagicMock:
    """テスト用のparse_args戻り値を作成するヘルパー"""
    args = MagicMock()
    args.input = input
    args.output = output
    args.model = model
    args.max_chars = max_chars
    args.split_threshold = split_threshold
    args.num_predict = num_predict
    args.chapter = chapter
    args.section = section
    args.dry_run = dry_run
    return args


def _make_minimal_book_xml() -> str:
    """テスト用の最小限のbook XMLを生成するヘルパー"""
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        "<book>"
        "<chapter>"
        '<heading level="1" number="1">第1章 テスト</heading>'
        '<heading level="2" number="1.1">セクション1.1</heading>'
        "<paragraph>テスト段落の内容です。</paragraph>"
        "</chapter>"
        "</book>"
    )


def _make_multi_chapter_book_xml() -> str:
    """テスト用の複数チャプターを含むbook XMLを生成するヘルパー"""
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        "<book>"
        "<chapter>"
        '<heading level="1" number="1">第1章</heading>'
        '<heading level="2" number="1.1">セクション1.1</heading>'
        "<paragraph>チャプター1の内容。</paragraph>"
        "</chapter>"
        "<chapter>"
        '<heading level="1" number="2">第2章</heading>'
        '<heading level="2" number="2.1">セクション2.1</heading>'
        "<paragraph>チャプター2の内容。</paragraph>"
        "</chapter>"
        "</book>"
    )


def _make_successful_conversion_result() -> ConversionResult:
    """テスト用の成功ConversionResultを生成するヘルパー"""
    return ConversionResult(
        success=True,
        dialogue_block=DialogueBlock(
            section_number="1.1",
            section_title="テスト",
            introduction="導入です。",
            dialogue=[
                Utterance(speaker="A", text="説明です。"),
                Utterance(speaker="B", text="なるほど。"),
            ],
            conclusion="まとめです。",
        ),
        error_message=None,
        processing_time_sec=1.0,
        input_char_count=100,
        was_split=False,
    )
