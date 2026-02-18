# Implementation Plan: 読み辞書生成のXMLファイル対応

**Branch**: `006-xml-dict-support` | **Date**: 2026-02-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-xml-dict-support/spec.md`

## Summary

`generate_reading_dict.py` の `main()` 関数にXMLファイル入力の分岐を追加する。XMLファイルは `parse_book2_xml()` でパースし、ContentItemをチャプター単位でグループ化してから技術用語を抽出する。辞書の保存・マージは既存の `dict_manager` をそのまま利用する。

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: xml.etree.ElementTree（標準ライブラリ）, src/xml2_parser, src/dict_manager, src/llm_reading_generator
**Storage**: Files（`data/{hash}/readings.json`）
**Testing**: pytest
**Target Platform**: Linux（ローカル開発環境）
**Project Type**: single
**Performance Goals**: N/A（バッチ処理、既存LLM呼び出しがボトルネック）
**Constraints**: 既存のMarkdownフローを変更しない
**Scale/Scope**: 単一ファイル（`generate_reading_dict.py`）の変更 + テスト追加

## Constitution Check

*Constitution file not found — gate check skipped.*

## Project Structure

### Documentation (this feature)

```text
specs/006-xml-dict-support/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── checklists/          # Quality checklists
│   └── requirements.md
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── generate_reading_dict.py  # 主な変更対象
├── xml2_parser.py            # 既存（変更なし）
├── dict_manager.py           # 既存（変更なし）
├── llm_reading_generator.py  # 既存（変更なし）
└── text_cleaner.py           # 既存（変更なし）

tests/
├── fixtures/
│   └── dict_test_book.xml    # 新規テストフィクスチャ
└── test_generate_reading_dict.py  # 新規テストファイル
```

**Structure Decision**: 既存の `src/` 直下構造に従い、`generate_reading_dict.py` のみを変更する。新規ファイルはテスト関連のみ。

## Implementation Phases

### Phase 1: XMLテキスト抽出と分岐ロジック (User Story 1 - P1)

**Goal**: `main()` に拡張子判定を追加し、XMLファイルからチャプター単位で用語抽出できるようにする

**Changes**:
1. `main()` 内で `input_path.suffix` を判定し `.xml` / `.md` / その他で分岐
2. XML分岐: `parse_book2_xml()` → `chapter_number` でグループ化 → チャプター毎に `extract_technical_terms()` を適用
3. 未対応拡張子: `logger.error()` + `sys.exit(1)`
4. 既存Markdownフローはそのまま維持

**Test**: XMLフィクスチャを用意し、用語抽出〜辞書生成の一連のフローをテスト

**Acceptance**: `make gen-dict INPUT=sample/book2.xml` で `readings.json` が生成される

### Phase 2: リグレッションテスト (User Story 2 - P1)

**Goal**: Markdown入力の既存動作が維持されることを確認

**Changes**:
1. 既存Markdownフローのテストケースを追加（拡張子判定の分岐カバレッジ）
2. エッジケース（空XML、不正XML、未対応拡張子）のテスト追加

**Test**: 全テストケースがパスすること

**Acceptance**: `python -m pytest tests/test_generate_reading_dict.py -v` が全パス
