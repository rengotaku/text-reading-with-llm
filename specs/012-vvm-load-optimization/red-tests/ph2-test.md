# Phase 2 RED Tests: 必要なモデルのみロード

**Date**: 2026-02-24
**Status**: RED (FAIL verified)
**User Story**: US1 - 必要なモデルのみロード

## Summary

| Item | Value |
|------|-------|
| 作成テスト数 | 36 |
| 失敗数 | 36 |
| テストファイル | tests/test_voicevox_client.py |

## 失敗テスト一覧

| テストファイル | テストメソッド | 期待動作 |
|---------------|---------------|----------|
| tests/test_voicevox_client.py | TestStyleIdToVvmMapping::test_mapping_exists | STYLE_ID_TO_VVM dict がモジュールに存在する |
| tests/test_voicevox_client.py | TestStyleIdToVvmMapping::test_mapping_not_empty | マッピングが空でない |
| tests/test_voicevox_client.py | TestStyleIdToVvmMapping::test_mapping_keys_are_integers | キーがすべて整数 |
| tests/test_voicevox_client.py | TestStyleIdToVvmMapping::test_mapping_values_are_strings | 値がすべて文字列 |
| tests/test_voicevox_client.py | TestStyleIdToVvmMapping::test_mapping_values_end_with_vvm | 値が .vvm で終わる |
| tests/test_voicevox_client.py | TestStyleIdToVvmMapping::test_default_style_id_in_mapping | style_id 13 が 13.vvm にマッピング |
| tests/test_voicevox_client.py | TestStyleIdToVvmMapping::test_style_id_0_maps_to_0_vvm | style_id 0 が 0.vvm にマッピング |
| tests/test_voicevox_client.py | TestStyleIdToVvmMapping::test_style_id_2_maps_to_1_vvm | style_id 2 が 1.vvm にマッピング |
| tests/test_voicevox_client.py | TestStyleIdToVvmMapping::test_multiple_style_ids_same_vvm | 複数 style_id が同一 VVM にマッピング |
| tests/test_voicevox_client.py | TestStyleIdToVvmMapping::test_mapping_keys_are_non_negative | キーが非負整数 |
| tests/test_voicevox_client.py | TestGetVvmPathForStyleId::test_returns_path_object | Path オブジェクトを返す |
| tests/test_voicevox_client.py | TestGetVvmPathForStyleId::test_default_style_id_returns_correct_path | style_id 13 で正しいパス |
| tests/test_voicevox_client.py | TestGetVvmPathForStyleId::test_style_id_0_returns_correct_path | style_id 0 で正しいパス |
| tests/test_voicevox_client.py | TestGetVvmPathForStyleId::test_style_id_2_returns_correct_path | style_id 2 で正しいパス |
| tests/test_voicevox_client.py | TestGetVvmPathForStyleId::test_path_uses_config_vvm_dir | config.vvm_dir を基準にパス生成 |
| tests/test_voicevox_client.py | TestGetVvmPathForStyleId::test_invalid_style_id_raises_value_error | 不正 style_id で ValueError |
| tests/test_voicevox_client.py | TestGetVvmPathForStyleId::test_negative_style_id_raises_value_error | 負の style_id で ValueError |
| tests/test_voicevox_client.py | TestGetVvmPathForStyleId::test_none_style_id_raises_type_error | None で TypeError |
| tests/test_voicevox_client.py | TestGetVvmPathForStyleId::test_string_style_id_raises_type_error | 文字列で TypeError |
| tests/test_voicevox_client.py | TestLoadModelForStyleId::test_loads_correct_vvm_for_style_id_13 | style_id 13 で 13.vvm のみロード |
| tests/test_voicevox_client.py | TestLoadModelForStyleId::test_loads_correct_vvm_for_style_id_0 | style_id 0 で 0.vvm のみロード |
| tests/test_voicevox_client.py | TestLoadModelForStyleId::test_loads_only_one_vvm | load_model が1回だけ呼ばれる |
| tests/test_voicevox_client.py | TestLoadModelForStyleId::test_does_not_load_all_models | load_all_models が呼ばれない |
| tests/test_voicevox_client.py | TestLoadModelForStyleId::test_calls_initialize_before_load | ロード前に initialize 呼び出し |
| tests/test_voicevox_client.py | TestLoadModelForStyleId::test_multiple_style_ids_load_different_vvms | 異なる style_id で異なる VVM ロード |
| tests/test_voicevox_client.py | TestLoadModelForStyleId::test_same_vvm_not_loaded_twice | 同一 VVM の重複ロード防止 |
| tests/test_voicevox_client.py | TestInvalidStyleIdError::test_nonexistent_style_id_raises_value_error | 存在しない style_id で ValueError |
| tests/test_voicevox_client.py | TestInvalidStyleIdError::test_negative_style_id_raises_value_error | 負の style_id で ValueError |
| tests/test_voicevox_client.py | TestInvalidStyleIdError::test_very_large_style_id_raises_value_error | 巨大な style_id で ValueError |
| tests/test_voicevox_client.py | TestInvalidStyleIdError::test_none_style_id_raises_error | None でエラー |
| tests/test_voicevox_client.py | TestInvalidStyleIdError::test_string_style_id_raises_error | 文字列でエラー |
| tests/test_voicevox_client.py | TestInvalidStyleIdError::test_float_style_id_raises_error | 浮動小数点でエラー |
| tests/test_voicevox_client.py | TestInvalidStyleIdError::test_error_message_includes_style_id | エラーメッセージに style_id 値を含む |
| tests/test_voicevox_client.py | TestInvalidStyleIdError::test_error_message_is_descriptive | 説明的なエラーメッセージ |
| tests/test_voicevox_client.py | TestInvalidStyleIdError::test_empty_string_style_id_raises_error | 空文字列でエラー |
| tests/test_voicevox_client.py | TestInvalidStyleIdError::test_get_vvm_path_also_raises_for_invalid | get_vvm_path でも不正値エラー |

## 実装ヒント

- `STYLE_ID_TO_VVM`: モジュールレベル dict。research.md のマッピング表を参照。キーは int (style_id)、値は str (VVM ファイル名)
- `get_vvm_path_for_style_id(style_id)`: STYLE_ID_TO_VVM で検索し、config.vvm_dir と結合して Path を返す。不正値は ValueError
- `load_model_for_style_id(style_id)`: get_vvm_path_for_style_id で VVM パスを取得し、既存の load_model() に委譲
- エッジケース: None, 文字列, 浮動小数点, 負数, 存在しない style_id すべてでエラーを返す

## make test 出力 (抜粋)

```
FAILED tests/test_voicevox_client.py::TestStyleIdToVvmMapping::test_mapping_exists - ImportError: cannot import name 'STYLE_ID_TO_VVM'
FAILED tests/test_voicevox_client.py::TestGetVvmPathForStyleId::test_returns_path_object - AttributeError: 'VoicevoxSynthesizer' object has no attribute 'get_vvm_path_for_style_id'
FAILED tests/test_voicevox_client.py::TestLoadModelForStyleId::test_loads_correct_vvm_for_style_id_13 - AttributeError: 'VoicevoxSynthesizer' object has no attribute 'load_model_for_style_id'
FAILED tests/test_voicevox_client.py::TestInvalidStyleIdError::test_nonexistent_style_id_raises_value_error - AttributeError: 'VoicevoxSynthesizer' object has no attribute 'load_model_for_style_id'
============================== 36 failed in 0.19s ==============================
```
