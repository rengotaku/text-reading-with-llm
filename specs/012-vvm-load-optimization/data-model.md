# Data Model: VOICEVOX モデルロード最適化

**Date**: 2026-02-24
**Feature**: 012-vvm-load-optimization

## エンティティ

### StyleIdMapping

style_id から VVM ファイルへの静的マッピング

```python
@dataclass
class StyleIdMapping:
    """style_id と VVM ファイルのマッピング情報"""
    style_id: int           # グローバルユニークなスタイルID
    speaker_id: int         # 話者ID（VVM ファイル番号）
    speaker_name: str       # 話者名（例: "青山龍星"）
    style_name: str         # スタイル名（例: "ノーマル"）
    vvm_file: str           # VVM ファイル名（例: "13.vvm"）
```

### VoicevoxConfig（既存・拡張なし）

現行の設定クラスはそのまま使用

```python
@dataclass
class VoicevoxConfig:
    onnxruntime_dir: Path
    open_jtalk_dict_dir: Path
    vvm_dir: Path
    style_id: int           # 使用するスタイルID
    speed_scale: float
    pitch_scale: float
    volume_scale: float
```

### VoicevoxSynthesizer（既存・メソッド追加）

選択的ロード機能を追加

```python
class VoicevoxSynthesizer:
    # 既存メンバー
    _synthesizer: Synthesizer
    _loaded_models: set[Path]
    config: VoicevoxConfig

    # 新規追加
    def load_model_for_style_id(self, style_id: int) -> None:
        """指定された style_id に必要な VVM のみをロード"""
        pass

    def get_vvm_path_for_style_id(self, style_id: int) -> Path:
        """style_id から対応する VVM ファイルパスを取得"""
        pass
```

## 関係図

```
┌─────────────────┐
│ VoicevoxConfig  │
│ - style_id: 13  │
└────────┬────────┘
         │ uses
         ▼
┌─────────────────────────┐
│ STYLE_ID_TO_VVM_MAPPING │ (静的 dict)
│ {13: "13.vvm", ...}     │
└────────┬────────────────┘
         │ resolves to
         ▼
┌─────────────────────────┐
│ VoicevoxSynthesizer     │
│ - load_model_for_style_id()
│ - _loaded_models: {"13.vvm"}
└─────────────────────────┘
```

## 状態遷移

### VoicevoxSynthesizer のモデルロード状態

```
[Uninitialized]
       │
       │ initialize()
       ▼
[Initialized, No Models]
       │
       │ load_model_for_style_id(13)
       ▼
[Ready: 13.vvm loaded]
       │
       │ load_model_for_style_id(0)  (追加ロード)
       ▼
[Ready: 13.vvm, 0.vvm loaded]
```

## バリデーションルール

1. **style_id の存在確認**: マッピングに存在しない style_id はエラー
2. **VVM ファイルの存在確認**: 対応する VVM ファイルがない場合はエラー
3. **重複ロード防止**: 既にロード済みの VVM は再ロードしない
