# Phase 2 Output: 書籍セクションを対話形式に変換

**Date**: 2026-03-13
**Status**: Completed
**User Story**: US1 - 書籍セクションを対話形式に変換

## 実行タスク

- [x] T019 REDテストを読む: specs/041-book-dialogue-conversion/red-tests/ph2-test.md
- [x] T020 [P] [US1] DialogueBlock, Utterance, ConversionResult データクラスを実装: src/dialogue_converter.py
- [x] T021 [P] [US1] セクション抽出関数 extract_sections() を実装: src/dialogue_converter.py
- [x] T022 [US1] LLM構造分析関数 analyze_structure() を実装: src/dialogue_converter.py
- [x] T023 [US1] LLM対話生成関数 generate_dialogue() を実装: src/dialogue_converter.py
- [x] T024 [US1] 対話XMLシリアライズ関数 to_dialogue_xml() を実装: src/dialogue_converter.py
- [x] T025 [US1] convert_section() 統合関数を実装: src/dialogue_converter.py
- [x] T026 `make test` で PASS (GREEN) を確認
- [x] T027 `make test` ですべてのテストがパスすることを確認
- [x] T028 `make coverage` でカバレッジ70%以上を確認
- [x] T029 Edit: specs/041-book-dialogue-conversion/tasks/ph2-output.md

## 変更ファイル

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/dialogue_converter.py | 新規 | 対話変換モジュール（データクラス、関数群すべて実装） |
| specs/041-book-dialogue-conversion/tasks/ph2-output.md | 新規 | このファイル |
| specs/041-book-dialogue-conversion/tasks.md | 修正 | Phase 2 タスクを完了状態に更新 |

## テスト結果

```
============================= 663 passed in 5.98s ==============================

Coverage:
src/dialogue_converter.py  130  21  84%
TOTAL                     1598 376  76%

Required test coverage of 70% reached. Total coverage: 76.47%
663 passed in 5.07s
```

**カバレッジ**: 76%（目標: 70%以上） — 達成

## 実装詳細

### データクラス

- `Utterance`: speaker（Literal["A", "B"]）、text フィールドを持つ dataclass
- `DialogueBlock`: section_number, section_title, introduction, dialogue（list[Utterance]）, conclusion フィールド
- `ConversionResult`: success, dialogue_block, error_message, processing_time_sec, input_char_count, was_split フィールド
- `Section`（内部用）: extract_sections() の返却型

### 関数

- `extract_sections(items: list[ContentItem]) -> list[Section]`: level=2見出しでグループ化、level=1はスキップ
- `analyze_structure(paragraphs, model, ollama_chat_func) -> dict`: introduction/dialogue/conclusionに分類、JSON応答パース
- `generate_dialogue(dialogue_paragraphs, model, ollama_chat_func, introduction, conclusion) -> list[Utterance]`: A/B発話JSON取得
- `to_dialogue_xml(block: DialogueBlock) -> str`: xml.etree.ElementTreeで `<dialogue-section>` 構造を生成
- `convert_section(section, model, ollama_chat_func) -> ConversionResult`: 統合関数

### LLM呼び出しパターン

llm_reading_generator.py と同様のパターンを採用:
```python
response = ollama_chat_func(model=model, messages=messages)
response_text = response.get("message", {}).get("content", "")
```

JSON応答の抽出には regex を使用し、パース失敗時はフォールバック値を返す。

## 発見した問題

特になし。テストはすべてファーストパスで全74件PASS。

## 次フェーズへの引き継ぎ

Phase 3（US2: 長文セクションの分割処理）で実装:

- `should_split(section: Section) -> bool`: 4,000文字超の判定
- `split_by_heading(section: Section) -> list[Section]`: 見出し単位で分割
- `convert_section()` に分割ロジックを統合
- `ConversionResult.was_split` フラグの活用

**依存関係**:
- `Section` データクラスは Phase 2 で実装済み（`src/dialogue_converter.py`）
- `convert_section()` は Phase 3 で拡張される

**注意事項**:
- analyze_structure / generate_dialogue は空リストでも動作する（LLMがモックなら空のデフォルト値を返す）
- `dialogue_converter.py` の `convert_section()` は現時点では分割なし（was_split=False 固定）
