# Implementation Plan: チャプター分割とクリーニング

**Branch**: `005-chapter-split-cleaning` | **Date**: 2026-02-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-chapter-split-cleaning/spec.md`

## Summary

xml2_pipeline に既存 xml_pipeline の機能（テキストクリーニング、分割出力）を統合する。
- `clean_page_text()` を全テキストに適用して音声品質を向上
- chapter 単位での WAV ファイル分割出力を実装
- cleaned_text.txt にクリーニング済みテキストを出力

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: xml.etree.ElementTree（標準ライブラリ）, voicevox_core, soundfile, numpy, MeCab（text_cleaner経由）
**Storage**: Files（WAV 出力、assets/sounds/*.mp3）
**Testing**: pytest
**Target Platform**: Linux (Ubuntu)
**Project Type**: Single project（src/, tests/ at repository root）
**Performance Goals**: 既存パイプラインと同等の処理速度
**Constraints**: メモリ効率（chapter 単位で処理することで大きな書籍も対応）
**Scale/Scope**: 単一書籍の処理（数百ページ、数十 chapter）

## Constitution Check

*Constitution file not found - skipping gate check*

## Project Structure

### Documentation (this feature)

```text
specs/005-chapter-split-cleaning/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # N/A (CLI tool, no API)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── xml2_parser.py       # 修正: ContentItem に chapter_number 追加
├── xml2_pipeline.py     # 修正: clean_page_text 適用、chapter 分割出力
└── text_cleaner.py      # 既存: clean_page_text()（変更なし）

tests/
├── test_xml2_parser.py  # 追加: chapter_number テスト
└── test_xml2_pipeline.py # 追加: クリーニング・分割出力テスト
```

**Structure Decision**: 既存の single project 構造を維持。xml2_parser.py と xml2_pipeline.py のみを修正。

## Complexity Tracking

> 違反なし - 既存実装の修正のみで新規アーキテクチャパターン不要

## Implementation Approach

### 修正対象ファイル

| ファイル | 変更内容 |
|----------|----------|
| `src/xml2_parser.py` | ContentItem に `chapter_number` 属性追加、parse_book2_xml で chapter 追跡 |
| `src/xml2_pipeline.py` | `clean_page_text()` 呼び出し追加、chapter 分割出力ロジック追加 |
| `tests/test_xml2_parser.py` | chapter_number テスト追加 |
| `tests/test_xml2_pipeline.py` | クリーニング・分割出力テスト追加 |

### 依存関係

```
xml2_parser.py (ContentItem 修正)
       ↓
xml2_pipeline.py (process_content 修正)
       ↓
text_cleaner.py (既存、変更なし)
```

### リスク

| リスク | 対策 |
|--------|------|
| ContentItem 変更による既存テスト破損 | chapter_number をオプショナル（デフォルト None）にする |
| ファイル名サニタイズ不足 | 日本語タイトル→ローマ字/番号のみに変換する関数を追加 |
| 大量 chapter でのメモリ問題 | chapter 単位で逐次処理・出力する設計 |
