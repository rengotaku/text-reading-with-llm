# Phase 2 RED Tests: 書籍セクションを対話形式に変換

**Date**: 2026-03-13
**Status**: RED (FAIL verified)
**User Story**: US1 - 書籍セクションを対話形式に変換

## Summary

| 項目 | 値 |
|------|-------|
| 作成テスト数 | 74 |
| 失敗数 | 74（モジュール未存在によるImportError） |
| テストファイル | tests/test_dialogue_converter.py |

## 失敗テスト

| テストファイル | テストクラス | テスト数 | 期待する動作 |
|-----------|-------------|---------|-------------------|
| tests/test_dialogue_converter.py | TestUtteranceDataclass | 8 | Utterance(speaker, text)の生成、等価性、特殊文字対応 |
| tests/test_dialogue_converter.py | TestDialogueBlockDataclass | 6 | DialogueBlock(section_number, title, intro, dialogue, conclusion)の生成、フィールド検証 |
| tests/test_dialogue_converter.py | TestConversionResultDataclass | 4 | 成功/失敗時のConversionResult生成、全フィールド検証 |
| tests/test_dialogue_converter.py | TestExtractSections | 7 | ContentItemリストからセクション単位に抽出、チャプター見出しスキップ、空入力 |
| tests/test_dialogue_converter.py | TestAnalyzeStructure | 9 | LLMでintro/dialogue/conclusion分類、JSON応答パース、エラーハンドリング |
| tests/test_dialogue_converter.py | TestGenerateDialogue | 10 | LLMでA/B発話生成、Utteranceリスト返却、コンテキストパラメータ |
| tests/test_dialogue_converter.py | TestToDialogueXml | 13 | DialogueBlockからXML文字列生成、構造検証、特殊文字エスケープ |
| tests/test_dialogue_converter.py | TestEdgeCases | 17 | Null/None入力、短文、空リスト、大量データ、特殊文字、境界値、不正LLM応答 |

## 実装ヒント

- `DialogueBlock`, `Utterance`, `ConversionResult`: `dataclasses.dataclass`で定義。data-model.mdのフィールド定義に従う
- `extract_sections(items: list[ContentItem]) -> list`: xml_parserのContentItemリストからlevel=2見出しでグループ化
- `analyze_structure(paragraphs, ollama_chat_func, model)`: ollama.chat()でJSON応答取得、3キー(introduction/dialogue/conclusion)に分類
- `generate_dialogue(dialogue_paragraphs, ollama_chat_func, introduction, conclusion)`: ollama.chat()でA/B発話JSON取得、Utteranceリスト返却
- `to_dialogue_xml(block: DialogueBlock) -> str`: xml.etree.ElementTreeでXML生成、data-model.mdのスキーマに従う
- エッジケース: LLMの不正JSON応答、空入力、None入力、特殊文字のXMLエスケープ

## make test 出力（抜粋）

```
ERROR collecting tests/test_dialogue_converter.py
tests/test_dialogue_converter.py:27: in <module>
    from src.dialogue_converter import (
E   ModuleNotFoundError: No module named 'src.dialogue_converter'
=========================== short test summary info ============================
ERROR tests/test_dialogue_converter.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.27s ==============================
```

## 既存テスト影響

既存589テストは引き続きすべてパス（`--ignore=tests/test_dialogue_converter.py` で確認済み）。
