# Phase 4 Output

## 作業概要
- User Story 3 (Priority P3) の実装完了
- FAIL テスト 19 件を PASS させた（全て GREEN）
- voice, pitch パラメータを synthesize() に追加
- パラメータバリデーション機能を実装

## 修正ファイル一覧
- `src/aquestalk_client.py` - voice/pitch パラメータ追加 + バリデーション実装
  - `synthesize(text, speed=None, voice=None, pitch=None)` に変更
  - voice/pitch パラメータが指定された場合は config.voice/pitch を上書き
  - `_validate_parameters(speed, voice, pitch)` メソッドを追加
  - `initialize()` でバリデーションを実行（config パラメータの検証）
  - `synthesize()` でもバリデーションを実行（実行時パラメータの検証）

## テスト結果

```
============================= 321 passed in 0.72s ==============================
```

全 321 テスト PASS（既存テスト 302 件 + Phase 4 新規テスト 19 件）

## 実装の詳細

### 1. synthesize() への voice/pitch パラメータ追加 (T059)

`src/aquestalk_client.py`:
```python
def synthesize(
    self,
    text: str,
    speed: int | None = None,
    voice: int | None = None,
    pitch: int | None = None,
) -> bytes:
    """Synthesize text to audio.

    Args:
        text: Text to synthesize (can include AquesTalk tags like <NUM VAL=123>)
        speed: Override speed (50-300, default: use config.speed)
        voice: Override voice quality (0-200, default: use config.voice)
        pitch: Override pitch (50-200, default: use config.pitch)

    Returns:
        WAV audio data as bytes (16kHz, mono)

    Raises:
        ValueError: If any parameter is out of valid range
    """
    self.initialize()

    # Use provided values or fall back to config
    actual_speed = speed if speed is not None else self.config.speed
    actual_voice = voice if voice is not None else self.config.voice
    actual_pitch = pitch if pitch is not None else self.config.pitch

    # Validate parameters
    self._validate_parameters(actual_speed, actual_voice, actual_pitch)
    ...
```

- 全パラメータは Optional（None がデフォルト）
- None の場合は config から値を取得
- 指定された場合は config を上書き
- 実行時に必ずバリデーションを実行

### 2. パラメータバリデーションの実装 (T060)

`src/aquestalk_client.py`:
```python
def _validate_parameters(
    self,
    speed: int,
    voice: int,
    pitch: int
) -> None:
    """Validate AquesTalk10 parameters.

    Args:
        speed: Speech speed (50-300)
        voice: Voice quality (0-200)
        pitch: Pitch (50-200)

    Raises:
        ValueError: If any parameter is out of valid range
    """
    if not (50 <= speed <= 300):
        raise ValueError(f"speed must be 50-300, got {speed}")
    if not (0 <= voice <= 200):
        raise ValueError(f"voice must be 0-200, got {voice}")
    if not (50 <= pitch <= 200):
        raise ValueError(f"pitch must be 50-200, got {pitch}")
```

バリデーションは2箇所で実行:
1. `initialize()`: config パラメータの検証（起動時エラー検出）
2. `synthesize()`: 実行時パラメータの検証（呼び出し時エラー検出）

### 3. CLI オプションとパラメータ渡し (T061, T062)

これらは Phase 2 で既に実装済み:
- `parse_args()` に `--speed`, `--voice`, `--pitch` オプション
- `main()` で `AquesTalkConfig(speed=parsed.speed, voice=parsed.voice, pitch=parsed.pitch)` を作成
- synthesizer に config を渡して初期化

## 実装のハイライト

### AquesTalk10 全パラメータ対応

AquesTalk10 の全パラメータに対応完了:

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| speed | 50-300 | 100 | 読み上げ速度 |
| voice | 0-200 | 100 | 声質（0=若い, 200=老人） |
| pitch | 50-200 | 100 | ピッチ（高さ） |

### 2段階バリデーション

1. **起動時（initialize）**: config パラメータを検証
   - CLI オプションの誤りを早期に検出
   - synthesizer 初期化時に即座にエラー

2. **実行時（synthesize）**: 実行時パラメータを検証
   - 動的なパラメータ変更にも対応
   - 不正値で synthesize() を呼んだ場合も検出

### パラメータオーバーライド設計

```python
# config で全体のデフォルトを設定
config = AquesTalkConfig(speed=100, voice=100, pitch=100)
synthesizer = AquesTalkSynthesizer(config)

# 個別の synthesize() 呼び出しで上書き可能
synthesizer.synthesize("通常のテキスト")  # config.speed=100 を使用
synthesizer.synthesize("見出し", speed=80)  # speed=80 で上書き
synthesizer.synthesize("強調", voice=150, pitch=120)  # 複数パラメータ上書き
```

## 注意点

### 次 Phase (Phase 5) への引き継ぎ
- User Stories 1, 2, 3 すべてが完了
- Phase 5 では Polish（ドキュメント、型ヒント、クリーンアップ）のみ
- 全機能が動作し、全テストが PASS している状態

### 実装済みの機能
- User Story 1: XML から AquesTalk 音声生成（Phase 2）
- User Story 2: 見出し効果音の挿入 + 速度調整（Phase 3）
- User Story 3: 音声パラメータの調整（Phase 4）

### パラメータバリデーション
- 範囲外の値は即座に ValueError を raise
- エラーメッセージには期待値と実際の値を表示
- テストで全境界値（最小-1, 最小, 最大, 最大+1）を検証済み

## 実装のミス・課題
- なし（全テスト PASS、既存機能にリグレッションなし）
