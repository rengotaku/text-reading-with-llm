# Implementation Plan: TTS前処理パターン置換

**Branch**: `009-tts-pattern-replace` | **Date**: 2026-02-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-tts-pattern-replace/spec.md`

## Summary

TTS読み上げ時の不自然なパターン（URL、ISBN、No.X）を自然な日本語表現に置換する機能を追加する。既存の`text_cleaner.py`のパターン処理フローに統合し、`_clean_urls()`の修正（削除→置換）、`No.X`→「ナンバーX」変換、`Chapter X`→「だいXしょう」変換を実装する。

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: re (標準ライブラリ)、fugashi/unidic-lite (既存)
**Storage**: N/A (テキスト処理のみ)
**Testing**: pytest
**Target Platform**: Linux (CLI)
**Project Type**: single
**Performance Goals**: テキスト処理は既存パイプラインと同等速度
**Constraints**: 既存テストの回帰なし
**Scale/Scope**: 単一モジュール修正 (src/text_cleaner.py)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution ファイルが存在しないため、プロジェクトの既存パターンに従う:
- [x] 既存のパターン定数命名規則に従う (`*_PATTERN`)
- [x] 既存の関数命名規則に従う (`_clean_*`, `_normalize_*`)
- [x] 既存のテスト構造に従う (pytest, クラスベース)
- [x] 処理順序を維持する (`clean_page_text()` 内の順序)

**GATE STATUS**: ✅ PASS

## Project Structure

### Documentation (this feature)

```text
specs/009-tts-pattern-replace/
├── spec.md              # 機能仕様書 (完了)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── quickstart.md        # Phase 1 output (実装ガイド)
├── checklists/
│   └── requirements.md  # 要件チェックリスト (完了)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── text_cleaner.py      # 主な修正対象
│   ├── _clean_urls()    # 修正: 削除→「ウェブサイト」置換
│   ├── _clean_number_prefix()  # 新規: No.X → ナンバーX
│   └── _clean_chapter()        # 新規: Chapter X → だいXしょう
└── number_normalizer.py # 参照のみ (既存の数値正規化)

tests/
├── test_url_cleaning.py         # 修正: 置換テスト追加
├── test_number_prefix.py        # 新規: No.X テスト
└── test_chapter_conversion.py   # 新規: Chapter X テスト
```

**Structure Decision**: 既存の単一プロジェクト構造を維持。`src/text_cleaner.py` への関数追加と既存関数の修正のみ。

## Complexity Tracking

Constitution 違反なし - 追跡不要。
