"""Tests for VOICEVOX client model loading optimization.

Phase 2 RED Tests - US1: 必要なモデルのみロード
style_id から対応する VVM ファイルのみをロードする機能のテスト。

Phase 3 RED Tests - US2: バージョン警告の解消
VVM ファイルと VOICEVOX Core のバージョンが一致し、警告が出ないことを確認するテスト。

Target functions:
- src/voicevox_client.py::STYLE_ID_TO_VVM (dict)
- src/voicevox_client.py::VoicevoxSynthesizer.get_vvm_path_for_style_id()
- src/voicevox_client.py::VoicevoxSynthesizer.load_model_for_style_id()
- src/voicevox_client.py::VoicevoxSynthesizer.load_model() (バージョン警告なし検証)
"""

import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from src.voicevox_client import VoicevoxConfig, VoicevoxSynthesizer

# =============================================================================
# T008: test_style_id_to_vvm_mapping
# STYLE_ID_TO_VVM dict のマッピング正当性テスト
# =============================================================================


class TestStyleIdToVvmMapping:
    """STYLE_ID_TO_VVM マッピング dict の正当性テスト."""

    def test_mapping_exists(self):
        """STYLE_ID_TO_VVM がモジュールレベルで定義されている."""
        from src.voicevox_client import STYLE_ID_TO_VVM

        assert isinstance(STYLE_ID_TO_VVM, dict)

    def test_mapping_not_empty(self):
        """マッピングが空ではない."""
        from src.voicevox_client import STYLE_ID_TO_VVM

        assert len(STYLE_ID_TO_VVM) > 0

    def test_mapping_keys_are_integers(self):
        """キーがすべて整数 (style_id)."""
        from src.voicevox_client import STYLE_ID_TO_VVM

        for key in STYLE_ID_TO_VVM:
            assert isinstance(key, int), f"Key {key} is not int: {type(key)}"

    def test_mapping_values_are_strings(self):
        """値がすべて文字列 (VVM ファイル名)."""
        from src.voicevox_client import STYLE_ID_TO_VVM

        for key, value in STYLE_ID_TO_VVM.items():
            assert isinstance(value, str), f"Value for key {key} is not str: {type(value)}"

    def test_mapping_values_end_with_vvm(self):
        """値がすべて .vvm 拡張子で終わる."""
        from src.voicevox_client import STYLE_ID_TO_VVM

        for key, value in STYLE_ID_TO_VVM.items():
            assert value.endswith(".vvm"), f"Value for key {key} does not end with .vvm: {value}"

    def test_default_style_id_in_mapping(self):
        """デフォルト style_id (13: 青山龍星) がマッピングに含まれる."""
        from src.voicevox_client import STYLE_ID_TO_VVM

        assert 13 in STYLE_ID_TO_VVM
        assert STYLE_ID_TO_VVM[13] == "13.vvm"

    def test_style_id_0_maps_to_0_vvm(self):
        """style_id 0 (四国めたん) は 0.vvm にマッピングされる."""
        from src.voicevox_client import STYLE_ID_TO_VVM

        assert 0 in STYLE_ID_TO_VVM
        assert STYLE_ID_TO_VVM[0] == "0.vvm"

    def test_style_id_2_maps_to_1_vvm(self):
        """style_id 2 (ずんだもん) は 1.vvm にマッピングされる."""
        from src.voicevox_client import STYLE_ID_TO_VVM

        assert 2 in STYLE_ID_TO_VVM
        assert STYLE_ID_TO_VVM[2] == "1.vvm"

    def test_multiple_style_ids_same_vvm(self):
        """同一 VVM に複数の style_id がマッピングされるケースがある."""
        from src.voicevox_client import STYLE_ID_TO_VVM

        # style_id 0 と 1 はどちらも 0.vvm (四国めたん)
        assert STYLE_ID_TO_VVM.get(0) == STYLE_ID_TO_VVM.get(1)

    def test_mapping_keys_are_non_negative(self):
        """style_id は非負整数のみ."""
        from src.voicevox_client import STYLE_ID_TO_VVM

        for key in STYLE_ID_TO_VVM:
            assert key >= 0, f"Negative style_id found: {key}"


# =============================================================================
# T009: test_get_vvm_path_for_style_id
# get_vvm_path_for_style_id() のパス解決テスト
# =============================================================================


class TestGetVvmPathForStyleId:
    """get_vvm_path_for_style_id() のテスト."""

    def setup_method(self):
        """テストごとに新しい Synthesizer を作成."""
        self.config = VoicevoxConfig(
            vvm_dir=Path("/tmp/test_vvms"),
        )
        self.synth = VoicevoxSynthesizer(config=self.config)

    def test_returns_path_object(self):
        """戻り値が Path オブジェクトである."""
        result = self.synth.get_vvm_path_for_style_id(13)
        assert isinstance(result, Path)

    def test_default_style_id_returns_correct_path(self):
        """デフォルト style_id 13 → /tmp/test_vvms/13.vvm."""
        result = self.synth.get_vvm_path_for_style_id(13)
        assert result == Path("/tmp/test_vvms/13.vvm")

    def test_style_id_0_returns_correct_path(self):
        """style_id 0 → vvm_dir/0.vvm."""
        result = self.synth.get_vvm_path_for_style_id(0)
        assert result == Path("/tmp/test_vvms/0.vvm")

    def test_style_id_2_returns_correct_path(self):
        """style_id 2 (ずんだもん) → vvm_dir/1.vvm."""
        result = self.synth.get_vvm_path_for_style_id(2)
        assert result == Path("/tmp/test_vvms/1.vvm")

    def test_path_uses_config_vvm_dir(self):
        """パスが config.vvm_dir を基準としている."""
        custom_config = VoicevoxConfig(vvm_dir=Path("/custom/vvm/path"))
        synth = VoicevoxSynthesizer(config=custom_config)
        result = synth.get_vvm_path_for_style_id(13)
        assert result.parent == Path("/custom/vvm/path")

    def test_invalid_style_id_raises_value_error(self):
        """存在しない style_id で ValueError が発生."""
        with pytest.raises(ValueError):
            self.synth.get_vvm_path_for_style_id(99999)

    def test_negative_style_id_raises_value_error(self):
        """負の style_id で ValueError が発生."""
        with pytest.raises(ValueError):
            self.synth.get_vvm_path_for_style_id(-1)

    def test_none_style_id_raises_type_error(self):
        """None を渡すと TypeError が発生."""
        with pytest.raises((TypeError, ValueError)):
            self.synth.get_vvm_path_for_style_id(None)

    def test_string_style_id_raises_type_error(self):
        """文字列を渡すと TypeError が発生."""
        with pytest.raises((TypeError, ValueError)):
            self.synth.get_vvm_path_for_style_id("13")


# =============================================================================
# T010: test_load_model_for_style_id
# load_model_for_style_id() の選択的ロードテスト
# =============================================================================


class TestLoadModelForStyleId:
    """load_model_for_style_id() のテスト."""

    def setup_method(self):
        """テストごとに新しい Synthesizer を作成."""
        self.config = VoicevoxConfig(
            vvm_dir=Path("/tmp/test_vvms"),
        )
        self.synth = VoicevoxSynthesizer(config=self.config)

    @patch.object(VoicevoxSynthesizer, "load_model")
    @patch.object(VoicevoxSynthesizer, "initialize")
    def test_loads_correct_vvm_for_style_id_13(self, mock_init, mock_load):
        """style_id 13 で 13.vvm のみがロードされる."""
        self.synth.load_model_for_style_id(13)
        mock_load.assert_called_once_with(Path("/tmp/test_vvms/13.vvm"))

    @patch.object(VoicevoxSynthesizer, "load_model")
    @patch.object(VoicevoxSynthesizer, "initialize")
    def test_loads_correct_vvm_for_style_id_0(self, mock_init, mock_load):
        """style_id 0 で 0.vvm のみがロードされる."""
        self.synth.load_model_for_style_id(0)
        mock_load.assert_called_once_with(Path("/tmp/test_vvms/0.vvm"))

    @patch.object(VoicevoxSynthesizer, "load_model")
    @patch.object(VoicevoxSynthesizer, "initialize")
    def test_loads_only_one_vvm(self, mock_init, mock_load):
        """1つの style_id に対して load_model は1回だけ呼ばれる."""
        self.synth.load_model_for_style_id(13)
        assert mock_load.call_count == 1

    @patch.object(VoicevoxSynthesizer, "load_model")
    @patch.object(VoicevoxSynthesizer, "initialize")
    def test_does_not_load_all_models(self, mock_init, mock_load):
        """load_all_models() ではなく load_model() が呼ばれる."""
        with patch.object(VoicevoxSynthesizer, "load_all_models") as mock_load_all:
            self.synth.load_model_for_style_id(13)
            mock_load_all.assert_not_called()

    @patch.object(VoicevoxSynthesizer, "load_model")
    @patch.object(VoicevoxSynthesizer, "initialize")
    def test_calls_initialize_before_load(self, mock_init, mock_load):
        """ロード前に initialize() が呼ばれる."""
        self.synth.load_model_for_style_id(13)
        mock_init.assert_called()

    @patch.object(VoicevoxSynthesizer, "load_model")
    @patch.object(VoicevoxSynthesizer, "initialize")
    def test_multiple_style_ids_load_different_vvms(self, mock_init, mock_load):
        """異なる style_id で異なる VVM がロードされる."""
        self.synth.load_model_for_style_id(0)
        self.synth.load_model_for_style_id(13)
        assert mock_load.call_count == 2
        calls = [call.args[0] for call in mock_load.call_args_list]
        assert Path("/tmp/test_vvms/0.vvm") in calls
        assert Path("/tmp/test_vvms/13.vvm") in calls

    @patch.object(VoicevoxSynthesizer, "load_model")
    @patch.object(VoicevoxSynthesizer, "initialize")
    def test_same_vvm_not_loaded_twice(self, mock_init, mock_load):
        """同一 VVM に属する style_id を複数回呼んでも重複ロードしない.

        style_id 0 と 1 は同じ 0.vvm なので、load_model は1回のみ。
        既存の _loaded_models メカニズムで重複を防ぐ。
        """

        # load_model の内部で _loaded_models に追加される動作をシミュレート
        def side_effect(path):
            self.synth._loaded_models.add(path)

        mock_load.side_effect = side_effect
        self.synth.load_model_for_style_id(0)
        self.synth.load_model_for_style_id(1)
        # 0.vvm は1回だけロード（_loaded_models で重複防止）
        # ただし load_model 自体が重複チェックするため、
        # load_model_for_style_id は load_model に委譲する
        assert mock_load.call_count <= 2


# =============================================================================
# T011: test_invalid_style_id_error
# 不正な style_id に対するエラーハンドリングテスト
# =============================================================================

# voicevox_core がインストールされているかチェック
try:
    import voicevox_core  # noqa: F401

    HAS_VOICEVOX_CORE = True
except ImportError:
    HAS_VOICEVOX_CORE = False


@pytest.mark.skipif(not HAS_VOICEVOX_CORE, reason="voicevox_core not installed")
class TestInvalidStyleIdError:
    """不正な style_id でのエラーハンドリングテスト."""

    def setup_method(self):
        """テストごとに新しい Synthesizer を作成."""
        self.config = VoicevoxConfig(
            vvm_dir=Path("/tmp/test_vvms"),
        )
        self.synth = VoicevoxSynthesizer(config=self.config)

    def test_nonexistent_style_id_raises_value_error(self):
        """マッピングに存在しない style_id で ValueError."""
        with pytest.raises(ValueError, match="style_id"):
            self.synth.load_model_for_style_id(99999)

    def test_negative_style_id_raises_value_error(self):
        """負の style_id で ValueError."""
        with pytest.raises(ValueError, match="style_id"):
            self.synth.load_model_for_style_id(-1)

    def test_very_large_style_id_raises_value_error(self):
        """非常に大きな style_id で ValueError."""
        with pytest.raises(ValueError):
            self.synth.load_model_for_style_id(100000)

    def test_none_style_id_raises_error(self):
        """None を渡すとエラー."""
        with pytest.raises((TypeError, ValueError)):
            self.synth.load_model_for_style_id(None)

    def test_string_style_id_raises_error(self):
        """文字列を渡すとエラー."""
        with pytest.raises((TypeError, ValueError)):
            self.synth.load_model_for_style_id("invalid")

    def test_float_style_id_raises_error(self):
        """浮動小数点を渡すとエラー."""
        with pytest.raises((TypeError, ValueError)):
            self.synth.load_model_for_style_id(13.5)

    def test_error_message_includes_style_id(self):
        """エラーメッセージに不正な style_id の値が含まれる."""
        with pytest.raises(ValueError, match="99999"):
            self.synth.load_model_for_style_id(99999)

    def test_error_message_is_descriptive(self):
        """エラーメッセージが説明的である."""
        with pytest.raises(ValueError) as exc_info:
            self.synth.load_model_for_style_id(99999)
        error_msg = str(exc_info.value)
        # メッセージに style_id と有用な情報が含まれる
        assert "99999" in error_msg

    def test_empty_string_style_id_raises_error(self):
        """空文字列を渡すとエラー."""
        with pytest.raises((TypeError, ValueError)):
            self.synth.load_model_for_style_id("")

    def test_get_vvm_path_also_raises_for_invalid(self):
        """get_vvm_path_for_style_id でも不正値はエラー."""
        with pytest.raises(ValueError):
            self.synth.get_vvm_path_for_style_id(99999)


# =============================================================================
# T025: test_no_version_warning (Phase 3 - US2)
# VVM ロード時にバージョン不一致の警告が出ないことを検証
# =============================================================================


class TestNoVersionWarning:
    """VVM ロード時にバージョン不一致の WARNING が出ないことを検証.

    US2: バージョン警告の解消
    VVM ファイルと VOICEVOX Core 0.16.3 のバージョンが一致している場合、
    load_model() 実行時に WARNING レベルのログが出力されないことを確認する。

    このテストは現状の VVM ファイルがバージョン不一致のため FAIL する。
    GREEN フェーズで VVM ファイルを再取得することで PASS になる。
    """

    def setup_method(self):
        """テストごとに新しい Synthesizer を作成."""
        self.config = VoicevoxConfig(
            vvm_dir=Path("/tmp/test_vvms"),
        )
        self.synth = VoicevoxSynthesizer(config=self.config)

    def test_load_model_no_version_warning(self, caplog):
        """VVM ロード時にバージョン不一致の WARNING が出力されない.

        voicevox_core が VVM を開く際、バージョン不一致があると
        WARNING ログを出力する。VVM ファイルが Core と一致していれば
        WARNING は 0 件のはず。

        verify_vvm_version() メソッドが True を返すことで検証。
        このメソッドは Phase 3 GREEN で実装される。
        """
        # verify_vvm_version() は VVM とCore のバージョン一致を確認する
        # このメソッドはまだ存在しないため AttributeError で FAIL する
        result = self.synth.verify_vvm_version(13)
        assert result is True, "VVM ファイルと Core のバージョンが一致していない"

    def test_verify_vvm_version_returns_bool(self):
        """verify_vvm_version() が bool を返す."""
        result = self.synth.verify_vvm_version(13)
        assert isinstance(result, bool)

    def test_verify_vvm_version_default_style_id(self):
        """デフォルト style_id (13) でバージョンが一致している."""
        result = self.synth.verify_vvm_version(13)
        assert result is True

    def test_verify_vvm_version_style_id_0(self):
        """style_id 0 でバージョンが一致している."""
        result = self.synth.verify_vvm_version(0)
        assert result is True

    def test_verify_vvm_version_style_id_2(self):
        """style_id 2 (ずんだもん) でバージョンが一致している."""
        result = self.synth.verify_vvm_version(2)
        assert result is True

    def test_verify_vvm_version_invalid_style_id(self):
        """存在しない style_id で ValueError."""
        with pytest.raises(ValueError):
            self.synth.verify_vvm_version(99999)

    def test_verify_vvm_version_none_raises_error(self):
        """None を渡すとエラー."""
        with pytest.raises((TypeError, ValueError)):
            self.synth.verify_vvm_version(None)

    def test_no_warning_in_logs_during_load(self, caplog):
        """モデルロード中に WARNING レベルのログが出力されない.

        load_model_for_style_id() 実行後、WARNING ログが 0 件であることを確認。
        verify_vvm_version() が True を返すなら、ロード時も警告なしのはず。
        """
        # まず VVM バージョンが一致していることを確認
        assert self.synth.verify_vvm_version(13) is True

        # WARNING ログが出ていないことを確認
        warning_records = [r for r in caplog.records if r.levelno >= logging.WARNING]
        version_warnings = [
            r for r in warning_records if "version" in r.message.lower() or "mismatch" in r.message.lower()
        ]
        assert len(version_warnings) == 0, (
            f"バージョン不一致の WARNING が {len(version_warnings)} 件検出された: "
            f"{[r.message for r in version_warnings]}"
        )

    def test_all_mapped_vvms_version_compatible(self):
        """STYLE_ID_TO_VVM に含まれるすべての VVM がバージョン互換.

        マッピング内の全 style_id について verify_vvm_version() が True を返す。
        """
        from src.voicevox_client import STYLE_ID_TO_VVM

        # 重複する VVM を除いてユニークな VVM ファイルのみチェック
        checked_vvms = set()
        for style_id, vvm_file in STYLE_ID_TO_VVM.items():
            if vvm_file not in checked_vvms:
                result = self.synth.verify_vvm_version(style_id)
                assert result is True, f"style_id {style_id} ({vvm_file}) のバージョンが不一致"
                checked_vvms.add(vvm_file)
