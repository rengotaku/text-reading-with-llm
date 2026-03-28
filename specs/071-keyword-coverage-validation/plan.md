# Implementation Plan: キーワード抽出とカバー率検証

**Branch**: `071-keyword-coverage-validation` | **Date**: 2026-03-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/071-keyword-coverage-validation/spec.md`

## Summary

対話生成の品質向上のため、原文からキーワードを抽出し（LLM使用）、生成された対話XMLのカバー率を検証する（文字列マッチング）機能を実装する。既存の prompt_loader.py パターンを活用し、新規プロンプトファイルとモジュールを追加する。

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: ollama (LLM), pytest (テスト)
**Storage**: N/A（メモリ内処理、JSON出力）
**Testing**: pytest
**Target Platform**: Linux（CLI）
**Project Type**: single
**Performance Goals**: キーワード抽出 5秒/セクション、カバー率検証 1秒/対話
**Constraints**: LLMはキーワード抽出のみ、カバー率検証はLLM不使用
**Scale/Scope**: 1セクションあたり10-50キーワード程度

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution ファイルが存在しないため、スキップ。プロジェクトの既存パターンに従う。

## Project Structure

### Documentation (this feature)

```text
specs/071-keyword-coverage-validation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── prompts/
│   ├── extract_keywords.txt   # 新規: キーワード抽出プロンプト
│   └── (existing prompts)
├── keyword_extractor.py       # 新規: キーワード抽出モジュール
├── coverage_validator.py      # 新規: カバー率検証モジュール
├── prompt_loader.py           # 既存: プロンプト読み込みユーティリティ
└── dialogue_converter.py      # 既存: 対話生成（参照用）

tests/
├── test_keyword_extractor.py  # 新規
└── test_coverage_validator.py # 新規
```

**Structure Decision**: 既存のフラットな src/ 構造を維持。prompt_loader.py パターンを再利用。

## Complexity Tracking

違反なし。既存パターンに従った最小限の追加。
