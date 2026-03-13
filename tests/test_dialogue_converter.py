"""Tests for dialogue_converter.py - Phase 2 RED Tests.

Phase 2 RED Tests - US1: 書籍セクションを対話形式に変換
LLMを使用してセクション内容を博士と助手の対話形式に変換する機能のテスト。

Target functions:
- src/dialogue_converter.py::DialogueBlock dataclass
- src/dialogue_converter.py::Utterance dataclass
- src/dialogue_converter.py::ConversionResult dataclass
- src/dialogue_converter.py::extract_sections()
- src/dialogue_converter.py::analyze_structure()
- src/dialogue_converter.py::generate_dialogue()
- src/dialogue_converter.py::to_dialogue_xml()

Test coverage:
- T011: DialogueBlock, Utterance データクラスのテスト
- T012: セクション抽出関数のテスト
- T013: LLM構造分析（intro/dialogue/conclusion分類）のテスト
- T014: LLM対話生成（A/B発話）のテスト
- T015: 対話XMLシリアライズのテスト
- T016: エッジケース（短文、空セクション）のテスト
"""

import xml.etree.ElementTree as ET
from unittest.mock import MagicMock

from src.dialogue_converter import (
    ConversionResult,
    DialogueBlock,
    Utterance,
    analyze_structure,
    extract_sections,
    generate_dialogue,
    to_dialogue_xml,
)

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
