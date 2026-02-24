# Quickstart: VOICEVOX モデルロード最適化

**Feature**: 012-vvm-load-optimization

## 変更概要

1. `load_all_models()` → `load_model_for_style_id()` に置き換え
2. style_id → VVM 静的マッピングを追加
3. VVM ファイルを再取得してバージョン警告を解消

## 実装手順

### Step 1: 静的マッピング追加

```python
# src/voicevox_client.py に追加

# style_id → VVM ファイル名のマッピング（VOICEVOX 0.16.x）
STYLE_ID_TO_VVM: dict[int, str] = {
    0: "0.vvm",    # 四国めたん - あまあま
    1: "0.vvm",    # 四国めたん - ノーマル
    2: "1.vvm",    # ずんだもん - ノーマル
    3: "1.vvm",    # ずんだもん - あまあま
    # ... 省略（全 style_id を網羅）
    13: "13.vvm",  # 青山龍星 - ノーマル
}
```

### Step 2: 選択的ロードメソッド追加

```python
# VoicevoxSynthesizer に追加

def load_model_for_style_id(self, style_id: int) -> None:
    """指定された style_id に必要な VVM のみをロード."""
    if style_id not in STYLE_ID_TO_VVM:
        raise ValueError(f"Unknown style_id: {style_id}")

    vvm_file = STYLE_ID_TO_VVM[style_id]
    vvm_path = self.config.vvm_dir / vvm_file

    if not vvm_path.exists():
        raise FileNotFoundError(f"VVM file not found: {vvm_path}")

    self.load_model(vvm_path)
```

### Step 3: パイプライン変更

```python
# src/xml2_pipeline.py を変更

# Before:
synthesizer.load_all_models()

# After:
synthesizer.load_model_for_style_id(parsed.style_id)
```

### Step 4: VVM ファイル再取得

```bash
# Makefile のバージョンを確認
# VOICEVOX_VERSION := 0.16.3

# VVM ファイルを再ダウンロード
rm -rf voicevox_core/models/vvms/
make setup-voicevox
```

## テスト実行

```bash
# 単一 style_id でのテスト
make xml-tts STYLE_ID=13

# ログ確認: 13.vvm のみロードされることを確認
# [INFO] Loading voice model: voicevox_core/models/vvms/13.vvm
# (他のモデルはロードされない)

# バージョン警告がないことを確認
# [WARNING] `...`: different `version` が出力されないこと
```

## 期待される結果

- 起動時間: 80%以上短縮（26ファイル → 1ファイル）
- メモリ使用量: 大幅削減
- バージョン警告: 0件
