# Phase 1 Output: Setup

**Date**: 2026-02-24
**Status**: Completed

## Executed Tasks

- [x] T001 Read current implementation in src/voicevox_client.py
- [x] T002 [P] Read current implementation in src/xml2_pipeline.py
- [x] T003 [P] Read existing tests in tests/test_xml2_pipeline.py
- [x] T004 [P] Read VOICEVOX Core version in Makefile
- [x] T005 Identify current load_all_models() call location and usage pattern
- [x] T006 Generate phase output: specs/012-vvm-load-optimization/tasks/ph1-output.md

## Existing Code Analysis

### src/voicevox_client.py

**Structure**:
- `VoicevoxConfig` (dataclass, line 37-47): 設定クラス。`vvm_dir`, `style_id` 等を保持
- `VoicevoxSynthesizer` (class, line 50-192): メインの合成クラス
  - `_loaded_models: set[Path]`: ロード済みモデルを追跡（重複ロード防止）
  - `load_model(vvm_path)` (line 99): 単一 VVM をロード
  - `load_all_models()` (line 125): **変更対象** - vvm_dir の全 .vvm をロード
  - `synthesize()` (line 131): モデル未ロード時に `load_all_models()` を呼ぶ

**Required Updates**:
1. `STYLE_ID_TO_VVM` dict を追加: style_id → VVM ファイル名のマッピング
2. `get_vvm_path_for_style_id()` を追加: style_id から VVM パスを解決
3. `load_model_for_style_id()` を追加: 指定 style_id に必要な VVM のみロード

### src/xml2_pipeline.py

**Structure**:
- `main()` (line 94): エントリーポイント
- Line 226: `synthesizer.load_all_models()` ← **変更箇所**

**Required Updates**:
1. Line 226: `load_all_models()` → `load_model_for_style_id(parsed.style_id)` に置き換え

### Makefile

**VOICEVOX Configuration** (line 6-9):
```makefile
VOICEVOX_DIR := voicevox_core
VOICEVOX_VERSION := 0.16.3
VOICEVOX_WHEEL := voicevox_core-$(VOICEVOX_VERSION)-cp310-abi3-manylinux_2_34_x86_64.whl
VOICEVOX_DOWNLOADER := download-linux-x64
```

**Key Targets**:
- `make setup-voicevox`: VVM ファイルを Core 0.16.3 に合わせて再取得

## Existing Test Analysis

- `tests/test_xml2_pipeline.py`:
  - parse_args のデフォルト値テスト
  - カスタムオプションテスト
  - VoicevoxSynthesizer は **mock で代替** されている
- **Does not exist**: `tests/test_voicevox_client.py` → Create new

**Required Fixtures**:
- None (既存の mock パターンを踏襲)

## Newly Created Files

### tests/test_voicevox_client.py (Phase 2 で作成)

- `test_style_id_to_vvm_mapping`: マッピング dict のテスト
- `test_get_vvm_path_for_style_id`: パス解決のテスト
- `test_load_model_for_style_id`: 選択的ロードのテスト
- `test_invalid_style_id_error`: 不正 style_id のエラーテスト

## Technical Decisions

1. **静的マッピング採用**: VOICEVOX Core の `get_metas()` による動的取得ではなく、コード内の dict で静的定義。理由: シンプルさ、起動時オーバーヘッド削減
2. **テストファイル分離**: voicevox_client のテストを新規ファイルに分離。理由: テスト責務の明確化

## Handoff to Next Phase

Items to implement in Phase 2 (US1: 必要なモデルのみロード):

**新規実装**:
- `STYLE_ID_TO_VVM` dict: style_id → VVM ファイル名マッピング（research.md 参照）
- `get_vvm_path_for_style_id(style_id: int) -> Path`: style_id から VVM パスを解決
- `load_model_for_style_id(style_id: int) -> None`: 指定 VVM のみロード

**変更箇所**:
- `src/xml2_pipeline.py` line 226: `load_all_models()` → `load_model_for_style_id()`

**再利用可能な既存コード**:
- `VoicevoxSynthesizer.load_model(vvm_path)`: 単一 VVM ロードロジック
- `_loaded_models` set: 重複ロード防止機構

**Caveats**:
- マッピングは VOICEVOX 0.16.x 向け。将来のバージョンで style_id と VVM の対応が変わる可能性あり
- research.md のマッピング情報を参考に実装
