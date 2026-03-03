# Implementation Plan: XML関連ファイル名の統一

**Branch**: `025-rename-test-xml-parser` | **Date**: 2026-03-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/025-rename-test-xml-parser/spec.md`

## Summary

`xml2_` プレフィックスを持つすべてのソース・テストファイルを `xml_` にリネームし、関連するインポート文を更新する。ファイル命名の一貫性向上が目的。

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: なし（ファイルリネームのみ）
**Storage**: N/A
**Testing**: pytest, pytest-cov
**Target Platform**: Linux/macOS
**Project Type**: single（CLIツール）
**Performance Goals**: N/A（リファクタリング）
**Constraints**: git履歴でリネーム追跡可能であること
**Scale/Scope**: 8ファイルリネーム + 14ファイルのインポート更新

## Constitution Check

*Constitution ファイルが存在しないため、ゲートチェックはスキップ*

✅ このタスクは単純なリファクタリングであり、新機能追加や依存関係追加を含まない。

## Project Structure

### Documentation (this feature)

```text
specs/025-rename-test-xml-parser/
├── spec.md              # 機能仕様
├── plan.md              # この計画書
├── research.md          # Phase 0 出力（リネーム対象の完全リスト）
└── checklists/
    └── requirements.md  # 品質チェックリスト
```

### Source Code (repository root)

```text
src/
├── xml_parser.py        # ← xml2_parser.py からリネーム
├── xml_pipeline.py      # ← xml2_pipeline.py からリネーム
├── text_cleaner_cli.py  # インポート更新必要
├── chapter_processor.py # インポート更新必要
├── generate_reading_dict.py # インポート更新必要
└── dict_manager.py      # インポート更新必要

tests/
├── test_xml_parser.py   # ← test_xml2_parser.py からリネーム
├── test_xml_pipeline_args.py           # ← リネーム
├── test_xml_pipeline_cleaned_text.py   # ← リネーム
├── test_xml_pipeline_integration.py    # ← リネーム
├── test_xml_pipeline_output.py         # ← リネーム
├── test_xml_pipeline_processing.py     # ← リネーム
├── test_dict_integration.py            # インポート更新必要
├── test_generate_reading_dict.py       # インポート更新必要
└── test_file_split.py                  # インポート更新必要
```

**Structure Decision**: 既存構造を維持。ファイル名のみ変更。

## Complexity Tracking

該当なし - 単純なリファクタリング

---

## Phase 0: Research Output

### リネーム対象ファイル（8ファイル）

| # | 変更前 | 変更後 |
|---|--------|--------|
| 1 | `src/xml2_parser.py` | `src/xml_parser.py` |
| 2 | `src/xml2_pipeline.py` | `src/xml_pipeline.py` |
| 3 | `tests/test_xml2_parser.py` | `tests/test_xml_parser.py` |
| 4 | `tests/test_xml2_pipeline_args.py` | `tests/test_xml_pipeline_args.py` |
| 5 | `tests/test_xml2_pipeline_cleaned_text.py` | `tests/test_xml_pipeline_cleaned_text.py` |
| 6 | `tests/test_xml2_pipeline_integration.py` | `tests/test_xml_pipeline_integration.py` |
| 7 | `tests/test_xml2_pipeline_output.py` | `tests/test_xml_pipeline_output.py` |
| 8 | `tests/test_xml2_pipeline_processing.py` | `tests/test_xml_pipeline_processing.py` |

### インポート更新対象ファイル（14ファイル）

**ソースファイル（4ファイル）**:
- `src/text_cleaner_cli.py` - `xml2_parser` → `xml_parser`
- `src/chapter_processor.py` - `xml2_parser` → `xml_parser`
- `src/generate_reading_dict.py` - `xml2_parser` → `xml_parser`
- `src/dict_manager.py` - `xml2_parser` → `xml_parser`

**テストファイル（10ファイル）** - リネーム対象含む:
- `tests/test_xml2_parser.py` → `test_xml_parser.py`
- `tests/test_xml2_pipeline_*.py` (5ファイル) → `test_xml_pipeline_*.py`
- `tests/test_dict_integration.py` - インポートのみ更新
- `tests/test_generate_reading_dict.py` - インポートのみ更新
- `tests/test_file_split.py` - インポートのみ更新

### インポートパターン更新一覧

| パターン | 置換後 | 出現数 |
|----------|--------|--------|
| `from src.xml2_parser` | `from src.xml_parser` | 多数 |
| `from src.xml2_pipeline` | `from src.xml_pipeline` | 多数 |
| `import xml2_parser` | `import xml_parser` | 0 |
| `import xml2_pipeline` | `import xml_pipeline` | 0 |

### リスク分析

**低リスク**:
- ファイルリネームは `git mv` で履歴追跡可能
- インポート更新は一括置換で実施可能
- テスト実行で検証可能

**注意点**:
- `src/xml2_pipeline.py` 内で `xml2_parser` をインポートしている（自己参照更新必要）
- キャッシュファイル（`.mypy_cache/`, `__pycache__/`）は自動再生成

---

## Phase 1: Design

### データモデル

該当なし - ファイルリネームのみ

### APIコントラクト

該当なし - 内部リファクタリング

### 実装順序

1. **ソースファイルのリネーム**（依存関係の根本）
   - `src/xml2_parser.py` → `src/xml_parser.py`
   - `src/xml2_pipeline.py` → `src/xml_pipeline.py`

2. **ソースファイル内のインポート更新**
   - `src/xml_pipeline.py` 内の自己参照更新
   - `src/text_cleaner_cli.py`
   - `src/chapter_processor.py`
   - `src/generate_reading_dict.py`
   - `src/dict_manager.py`

3. **テストファイルのリネーム**
   - 6ファイルを順次リネーム

4. **テストファイル内のインポート更新**
   - リネーム済みテストファイル内の更新
   - `test_dict_integration.py`
   - `test_generate_reading_dict.py`
   - `test_file_split.py`

5. **検証**
   - 全テスト実行
   - カバレッジ確認
   - 残存参照チェック

---

## User Story Phases (for /speckit.tasks)

### Phase 1: ソースファイルリネーム (P1)

**Goal**: ソースファイルを `xml_` プレフィックスにリネームし、インポートを更新

**Acceptance**:
- [ ] `src/xml2_parser.py` → `src/xml_parser.py` 完了
- [ ] `src/xml2_pipeline.py` → `src/xml_pipeline.py` 完了
- [ ] ソースファイル内のインポート更新完了
- [ ] `python -c "from src.xml_parser import parse_book2_xml"` 成功

### Phase 2: テストファイルリネーム (P2)

**Goal**: テストファイルを `xml_` プレフィックスにリネームし、インポートを更新

**Acceptance**:
- [ ] 6テストファイルのリネーム完了
- [ ] テストファイル内のインポート更新完了
- [ ] `pytest --collect-only` で全テスト検出確認

### Phase 3: 検証 (P3)

**Goal**: 全テスト通過とカバレッジ確認

**Acceptance**:
- [ ] `pytest` 全テスト通過
- [ ] カバレッジ維持（±1%以内）
- [ ] `grep -r "xml2_parser\|xml2_pipeline" src/ tests/` で残存参照なし
