# Implementation Plan: VOICEVOX モデルロード最適化

**Branch**: `012-vvm-load-optimization` | **Date**: 2026-02-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-vvm-load-optimization/spec.md`

## Summary

`make xml-tts` 実行時に、26個すべての VVM ファイルをロードする現状を改善し、指定された `--style-id` に対応する VVM ファイルのみをロードする。また、VVM ファイルと VOICEVOX Core のバージョン不一致警告を解消する。

**技術アプローチ**:
1. style_id → VVM ファイルの静的マッピングをコード内に定義
2. `load_all_models()` を `load_model_for_style_id()` に置き換え
3. VVM ファイルを Core 0.16.3 に合わせて再取得

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: voicevox_core 0.16.3, numpy, soundfile
**Storage**: N/A（VVM ファイルはローカルファイルシステム）
**Testing**: pytest
**Target Platform**: Linux x86_64
**Project Type**: Single CLI application
**Performance Goals**: モデルロード時間 80%以上短縮（26ファイル → 1ファイル）
**Constraints**: 既存の音声生成機能を損なわない
**Scale/Scope**: 単一ユーザー、ローカル実行

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Constitution file not found** - No gates to check. Proceeding with standard best practices.

**Post-design check**:
- ✅ 変更は既存の 2 ファイル（voicevox_client.py, xml2_pipeline.py）に限定
- ✅ 新規の設計パターンや複雑な抽象化は不要
- ✅ 静的マッピングはシンプルな dict で実装

## Project Structure

### Documentation (this feature)

```text
specs/012-vvm-load-optimization/
├── spec.md              # 機能仕様
├── plan.md              # このファイル
├── research.md          # style_id → VVM マッピング調査結果
├── data-model.md        # エンティティ定義
├── quickstart.md        # 実装手順ガイド
└── tasks.md             # タスクリスト（/speckit.tasks で生成）
```

### Source Code (repository root)

```text
src/
├── voicevox_client.py   # 変更: マッピング追加、load_model_for_style_id() 追加
└── xml2_pipeline.py     # 変更: load_all_models() → load_model_for_style_id()

tests/
├── test_xml2_pipeline.py  # 既存テスト確認
└── test_voicevox_client.py  # 新規: マッピングとロードのテスト（必要に応じて）

voicevox_core/
└── models/vvms/         # VVM ファイル再取得
    ├── 0.vvm
    ├── 1.vvm
    └── ...
```

**Structure Decision**: 既存の単一プロジェクト構造を維持。変更は `src/` 内の 2 ファイルに限定。

## Implementation Phases

### Phase 1: 静的マッピング実装 (P1 - FR-001, FR-002)

1. `src/voicevox_client.py` に `STYLE_ID_TO_VVM` dict を追加
2. `get_vvm_path_for_style_id()` メソッドを追加
3. `load_model_for_style_id()` メソッドを追加
4. 存在しない style_id に対するエラーハンドリング (FR-004)

**テスト**:
- style_id → VVM ファイル解決の単体テスト
- 存在しない style_id のエラーテスト

### Phase 2: パイプライン変更 (P1 - FR-001, FR-003)

1. `src/xml2_pipeline.py` の `load_all_models()` 呼び出しを置き換え
2. 既存の `make xml-tts` 動作確認

**テスト**:
- `make xml-tts` で単一モデルのみロードされることを確認
- ログ出力で VVM ファイル 1 つのみ表示を確認

### Phase 3: バージョン一致 (P2 - FR-005)

1. 既存の VVM ファイルを削除
2. `make setup-voicevox` で VVM を再取得
3. バージョン警告が出ないことを確認

**テスト**:
- `make xml-tts` 実行時に WARNING が 0 件
- 生成される音声品質が維持されていること

### Phase 4: 後方互換性検証 (P3 - FR-006)

1. 既存テストスイートの実行
2. 最適化前後の音声出力比較

**テスト**:
- `pytest` 全テストパス
- `make xml-tts` で同一入力に対する出力一致

## Risk Assessment

| リスク | 影響度 | 対策 |
|--------|--------|------|
| style_id マッピングの不完全 | 中 | 主要な style_id（デフォルト 13）を優先、必要に応じて拡張 |
| VVM 再取得後の動作変更 | 低 | 既存テストで検証 |
| 複数 style_id の同時使用 | 低 | FR-003 で対応済み、必要に応じて追加ロード |

## Complexity Tracking

> **No violations** - 実装はシンプルな dict ベースのマッピングと既存メソッドの拡張のみ

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | - | - |
