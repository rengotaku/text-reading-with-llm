# Implementation Plan: 書籍内容の対話形式変換

**Branch**: `041-book-dialogue-conversion` | **Date**: 2026-03-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/041-book-dialogue-conversion/spec.md`

## Summary

書籍のセクション内容を1人のナレーター形式から、博士と助手の2人対話形式に変換する機能を実装する。LLMを使用してテキストを対話形式に変換し、VOICEVOXの複数話者機能で音声を生成する。既存のxml_pipeline.pyと並行して動作するdialogue_pipeline.pyを新規作成する。

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: ollama (LLM), voicevox_core (TTS), requests, pyyaml, soundfile, numpy
**Storage**: ファイルシステム（XML入力、WAV出力、JSON辞書）
**Testing**: pytest, pytest-cov (カバレッジ70%以上)
**Target Platform**: Linux (x86_64)
**Project Type**: Single project (CLI tool)
**Performance Goals**: 3,500文字以内のセクションを5分以内に変換
**Constraints**: 4,000文字超は見出し単位で分割、num_predict: 1500〜2000
**Scale/Scope**: 書籍1冊（数十〜数百セクション）を順次処理

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution file not found - skipping gate check. Proceeding with standard project conventions:
- [x] 既存のコードスタイル（ruff, mypy）に従う
- [x] 既存のモジュール構造を維持
- [x] テストカバレッジ70%以上

## Project Structure

### Documentation (this feature)

```text
specs/041-book-dialogue-conversion/
├── plan.md              # This file
├── research.md          # Phase 0: LLMプロンプト設計、分割戦略
├── data-model.md        # Phase 1: 対話XMLスキーマ
├── quickstart.md        # Phase 1: クイックスタートガイド
├── contracts/           # Phase 1: CLI引数仕様
└── tasks.md             # Phase 2: /speckit.tasks で生成
```

### Source Code (repository root)

```text
src/
├── xml_pipeline.py          # 既存: 1話者TTS
├── dialogue_converter.py    # 新規: LLM対話変換
├── dialogue_pipeline.py     # 新規: 複数話者TTS
├── voicevox_client.py       # 既存: VOICEVOX呼び出し（変更なし）
├── text_cleaner.py          # 既存: テキスト正規化（変更なし）
├── xml_parser.py            # 既存: XML解析（変更なし）
└── llm_reading_generator.py # 既存: LLM辞書生成（参考）

tests/
├── test_dialogue_converter.py  # 新規: 対話変換テスト
├── test_dialogue_pipeline.py   # 新規: パイプラインテスト
└── ...                         # 既存テスト
```

**Structure Decision**: 既存のフラットなsrc/構造を維持し、新規モジュールを追加。既存モジュールは変更せず、dialogue_*で始まる新規モジュールで機能を実装。

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 2段階LLM処理 | 構造分析と対話生成を分離することで品質向上 | 1段階だと長文でコンテキストが失われる |
| 3話者構成 | 導入/結論はナレーター、対話は博士/助手で役割分担 | 2話者だと導入/結論の読み上げが不自然 |

## Phase Summary

### Phase 0: Research (このplan実行時に完了)

- [x] LLMプロンプト設計（gpt-oss:20b検証済み）
- [x] 長文分割戦略（4,000文字で見出し単位分割）
- [x] VOICEVOX話者割り当て（青山龍星:13, 麒ヶ島宗麟:67, 四国めたん:2）

### Phase 1: Design (このplan実行時に完了)

- [x] 対話XMLスキーマ定義
- [x] CLI引数仕様
- [x] クイックスタートガイド

### Phase 2: Implementation (tasks.mdで詳細化)

User Storyに基づく実装順序:
1. P1: 基本対話変換（dialogue_converter.py）
2. P2: 長文分割処理
3. P3: 複数話者TTS（dialogue_pipeline.py）
