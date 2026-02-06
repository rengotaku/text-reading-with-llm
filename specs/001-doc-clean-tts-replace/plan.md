# Implementation Plan: ドキュメントクリーン TTS代替置換機能

**Branch**: `001-doc-clean-tts-replace` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-doc-clean-tts-replace/spec.md`

## Summary

TTS用テキストクリーニングの拡張。URL処理、図表参照正規化、括弧付き英語除去、不適切な読点挿入の修正、コロン/鉤括弧の変換を実装。既存の `text_cleaner.py` と `punctuation_normalizer.py` を拡張し、処理パイプラインに統合する。

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: fugashi (MeCab), re (標準ライブラリ)
**Storage**: N/A (ステートレス変換)
**Testing**: pytest (`make test`)
**Target Platform**: Linux
**Project Type**: single
**Performance Goals**: 既存処理から10%以内の増加 (SC-006)
**Constraints**: 冪等性保証 (FR-009)
**Scale/Scope**: sample/book.md (30+ URLs, 多数の図表参照)

## Constitution Check

*GATE: 憲法ファイルなし - スキップ*

## Project Structure

### Documentation (this feature)

```text
specs/001-doc-clean-tts-replace/
├── plan.md              # This file
├── research.md          # Phase 0 output ✅
├── data-model.md        # Phase 1 output ✅
├── quickstart.md        # Phase 1 output ✅
├── contracts/           # Phase 1 output ✅
│   ├── text_cleaner_api.md
│   └── punctuation_normalizer_api.md
└── tasks.md             # Phase 2 output (speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── text_cleaner.py          # MODIFY: URL/ISBN/括弧/参照処理追加
├── punctuation_normalizer.py # MODIFY: コロン/鉤括弧/除外パターン追加
└── ...

tests/
├── test_url_cleaning.py         # NEW
├── test_reference_normalization.py  # NEW
├── test_punctuation_rules.py    # NEW
└── ...
```

**Structure Decision**: 既存の単一プロジェクト構造を維持。新規モジュールは不要（既存ファイルへの関数追加で対応）。

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | - | - |

## Phase Summary

| Phase | Type | Description | FR Coverage |
|-------|------|-------------|-------------|
| 1 | Setup | テスト環境準備 | - |
| 2 | TDD | URL処理実装 | FR-001,002,003 |
| 3 | TDD | 図表・注釈参照正規化 | FR-004,005,006 |
| 4 | TDD | ISBN処理 | FR-007 |
| 5 | TDD | 括弧付き英語除去 | FR-010 |
| 6 | TDD | 読点除外パターン | FR-011 |
| 7 | TDD | コロン変換 | FR-012 |
| 8 | TDD | 鉤括弧変換 | FR-013 |
| 9 | TDD | パイプライン統合 | FR-008,009 |
| 10 | Polish | パフォーマンス検証・リファクタ | SC-006 |

## Artifacts

- [research.md](./research.md) - 技術調査結果
- [data-model.md](./data-model.md) - 変換ルール定義
- [contracts/text_cleaner_api.md](./contracts/text_cleaner_api.md) - text_cleaner API
- [contracts/punctuation_normalizer_api.md](./contracts/punctuation_normalizer_api.md) - punctuation_normalizer API
- [quickstart.md](./quickstart.md) - 開発クイックスタート
