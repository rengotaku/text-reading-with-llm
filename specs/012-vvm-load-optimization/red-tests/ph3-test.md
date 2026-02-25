# Phase 3 RED Tests: バージョン警告の解消

**Date**: 2026-02-24
**Status**: RED (FAIL verified)
**User Story**: US2 - バージョン警告の解消

## Summary

| Item | Value |
|------|-------|
| 作成テスト数 | 9 |
| 失敗数 | 9 |
| テストファイル | tests/test_voicevox_client.py |

## 失敗テスト一覧

| テストファイル | テストメソッド | 期待動作 |
|---------------|---------------|----------|
| tests/test_voicevox_client.py | TestNoVersionWarning::test_load_model_no_version_warning | verify_vvm_version(13) が True を返す（バージョン一致） |
| tests/test_voicevox_client.py | TestNoVersionWarning::test_verify_vvm_version_returns_bool | verify_vvm_version() が bool を返す |
| tests/test_voicevox_client.py | TestNoVersionWarning::test_verify_vvm_version_default_style_id | デフォルト style_id 13 でバージョン一致 |
| tests/test_voicevox_client.py | TestNoVersionWarning::test_verify_vvm_version_style_id_0 | style_id 0 でバージョン一致 |
| tests/test_voicevox_client.py | TestNoVersionWarning::test_verify_vvm_version_style_id_2 | style_id 2 (ずんだもん) でバージョン一致 |
| tests/test_voicevox_client.py | TestNoVersionWarning::test_verify_vvm_version_invalid_style_id | 存在しない style_id で ValueError |
| tests/test_voicevox_client.py | TestNoVersionWarning::test_verify_vvm_version_none_raises_error | None で TypeError/ValueError |
| tests/test_voicevox_client.py | TestNoVersionWarning::test_no_warning_in_logs_during_load | モデルロード中に WARNING ログが 0 件 |
| tests/test_voicevox_client.py | TestNoVersionWarning::test_all_mapped_vvms_version_compatible | 全マッピング VVM がバージョン互換 |

## 実装ヒント

- `verify_vvm_version(style_id: int) -> bool`: VVM ファイルと Core のバージョン一致を確認するメソッド。style_id から VVM パスを解決し、VVM メタデータのバージョンが Core 0.16.3 と一致するかチェック
- エッジケース: 不正な style_id (None, 存在しない ID) は ValueError/TypeError で拒否
- VVM 再取得: `make setup-voicevox` で Core 0.16.3 に合う VVM をダウンロードし直すことでバージョン一致を達成
- WARNING ログ検証: caplog フィクスチャで WARNING レベルのバージョン関連ログが 0 件であることを確認

## make test 出力 (抜粋)

```
FAILED tests/test_voicevox_client.py::TestNoVersionWarning::test_load_model_no_version_warning - AttributeError: 'VoicevoxSynthesizer' object has no attribute 'verify_vvm_version'
FAILED tests/test_voicevox_client.py::TestNoVersionWarning::test_verify_vvm_version_returns_bool - AttributeError: 'VoicevoxSynthesizer' object has no attribute 'verify_vvm_version'
FAILED tests/test_voicevox_client.py::TestNoVersionWarning::test_verify_vvm_version_default_style_id - AttributeError: 'VoicevoxSynthesizer' object has no attribute 'verify_vvm_version'
FAILED tests/test_voicevox_client.py::TestNoVersionWarning::test_verify_vvm_version_style_id_0 - AttributeError: 'VoicevoxSynthesizer' object has no attribute 'verify_vvm_version'
FAILED tests/test_voicevox_client.py::TestNoVersionWarning::test_verify_vvm_version_style_id_2 - AttributeError: 'VoicevoxSynthesizer' object has no attribute 'verify_vvm_version'
FAILED tests/test_voicevox_client.py::TestNoVersionWarning::test_verify_vvm_version_invalid_style_id - AttributeError: 'VoicevoxSynthesizer' object has no attribute 'verify_vvm_version'
FAILED tests/test_voicevox_client.py::TestNoVersionWarning::test_verify_vvm_version_none_raises_error - AttributeError: 'VoicevoxSynthesizer' object has no attribute 'verify_vvm_version'
FAILED tests/test_voicevox_client.py::TestNoVersionWarning::test_no_warning_in_logs_during_load - AttributeError: 'VoicevoxSynthesizer' object has no attribute 'verify_vvm_version'
FAILED tests/test_voicevox_client.py::TestNoVersionWarning::test_all_mapped_vvms_version_compatible - AttributeError: 'VoicevoxSynthesizer' object has no attribute 'verify_vvm_version'
============================== 9 failed in 0.11s ==============================
```
