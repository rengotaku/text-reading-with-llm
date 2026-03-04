# Research: XML関連ファイル名の統一

**Date**: 2026-03-03
**Branch**: `025-rename-test-xml-parser`

## 調査目的

`xml2_` プレフィックスを持つファイルのリネームに必要な情報を収集する。

## 調査結果

### 1. リネーム対象ファイル

#### ソースファイル（2ファイル）

| ファイル | 行数 | 主要エクスポート |
|----------|------|------------------|
| `src/xml2_parser.py` | - | `parse_book2_xml`, `ContentItem`, `HeadingInfo`, `CHAPTER_MARKER`, `SECTION_MARKER` |
| `src/xml2_pipeline.py` | - | `main`, `parse_args`, `load_sound`, `process_content`, `process_chapters`, `sanitize_filename`, `get_pid_file_path`, `kill_existing_process`, `write_pid_file`, `cleanup_pid_file` |

#### テストファイル（6ファイル）

| ファイル | テスト対象 |
|----------|-----------|
| `tests/test_xml2_parser.py` | `xml2_parser` の全機能 |
| `tests/test_xml2_pipeline_args.py` | `parse_args` |
| `tests/test_xml2_pipeline_cleaned_text.py` | `main` (クリーンテキスト出力) |
| `tests/test_xml2_pipeline_integration.py` | `main` (統合テスト) |
| `tests/test_xml2_pipeline_output.py` | `sanitize_filename`, `process_chapters` |
| `tests/test_xml2_pipeline_processing.py` | `load_sound`, `process_content` |

### 2. インポート依存関係グラフ

```
xml2_parser.py
    ├── xml2_pipeline.py (CHAPTER_MARKER, SECTION_MARKER, ContentItem, parse_book2_xml)
    ├── text_cleaner_cli.py (CHAPTER_MARKER, SECTION_MARKER, parse_book2_xml)
    ├── chapter_processor.py (CHAPTER_MARKER, SECTION_MARKER, ContentItem)
    ├── generate_reading_dict.py (parse_book2_xml)
    ├── dict_manager.py (parse_book2_xml)
    └── tests/
        ├── test_xml2_parser.py
        ├── test_dict_integration.py
        ├── test_generate_reading_dict.py
        └── test_xml2_pipeline_*.py (複数)

xml2_pipeline.py
    └── tests/
        ├── test_xml2_pipeline_*.py (5ファイル)
        └── test_file_split.py
```

### 3. インポート文の詳細

#### `from src.xml2_parser import ...` パターン

| ファイル | インポート内容 |
|----------|---------------|
| `src/xml2_pipeline.py:42` | `CHAPTER_MARKER, SECTION_MARKER, ContentItem, parse_book2_xml` |
| `src/text_cleaner_cli.py:20` | `CHAPTER_MARKER, SECTION_MARKER, parse_book2_xml` |
| `src/chapter_processor.py:18` | `CHAPTER_MARKER, SECTION_MARKER, ContentItem` |
| `src/generate_reading_dict.py:22` | `parse_book2_xml` |
| `src/dict_manager.py:46` | `parse_book2_xml` |
| `tests/test_dict_integration.py:8` | `parse_book2_xml` |
| `tests/test_generate_reading_dict.py:22` | `ContentItem, HeadingInfo` |
| `tests/test_xml2_parser.py:16` | 複数シンボル |
| `tests/test_xml2_pipeline_processing.py` | `ContentItem`, `CHAPTER_MARKER`, etc. (複数箇所) |
| `tests/test_xml2_pipeline_output.py` | `CHAPTER_MARKER`, `ContentItem`, `HeadingInfo` (複数箇所) |

#### `from src.xml2_pipeline import ...` パターン

| ファイル | インポート内容 |
|----------|---------------|
| `tests/test_xml2_pipeline_args.py` | `parse_args` (多数) |
| `tests/test_xml2_pipeline_cleaned_text.py` | `main` (多数) |
| `tests/test_xml2_pipeline_integration.py` | `main` (多数) |
| `tests/test_xml2_pipeline_output.py` | `sanitize_filename`, `process_chapters` (多数) |
| `tests/test_xml2_pipeline_processing.py` | `load_sound`, `process_content` (多数) |
| `tests/test_file_split.py` | 複数関数 (多数) |

### 4. 置換戦略

**Decision**: 一括置換を使用

**Rationale**:
- パターンが明確で競合なし
- `xml2_parser` と `xml2_pipeline` は他の文字列と重複しない
- テスト実行で検証可能

**Alternatives considered**:
- 手動置換: 作業量が多く、ミスのリスクあり → 却下
- AST解析による置換: 過剰な複雑性 → 却下

### 5. 実行順序の根拠

**Decision**: ソースファイル → テストファイルの順

**Rationale**:
- ソースファイルが依存の根本
- テストはソースをインポートするため、ソース先行が自然
- 中間状態でもテスト可能（段階的検証）

### 6. リスクと対策

| リスク | 対策 |
|--------|------|
| インポートエラー | 各フェーズ後にテスト実行 |
| git履歴の分断 | `git mv` を使用して追跡可能性を維持 |
| キャッシュ問題 | `__pycache__/`, `.mypy_cache/` は自動再生成 |
| 残存参照 | `grep` で最終確認 |

## 結論

このリファクタリングは低リスクで、標準的な置換操作で実施可能。
