# Phase 3 Output

## 作業概要
- User Story 2 (Priority P2) の実装完了
- FAIL テスト 4 件を PASS させた（全て GREEN）
- 見出しセグメントに speed=80 を適用し、ゆっくり読む強調機能を実装

## 修正ファイル一覧
- `src/aquestalk_client.py` - synthesize() に speed パラメータ追加
  - `synthesize(text, speed=None)` に変更
  - speed パラメータが指定された場合は config.speed を上書き
- `src/aquestalk_pipeline.py` - 見出しセグメントの速度調整実装
  - `HEADING_SPEED = 80` 定数を追加
  - `process_pages_with_heading_sound()` で見出しセグメントに speed=80 を適用
- `tests/test_aquestalk_pipeline.py` - Phase 2 の mock 修正
  - 既存テストの mock_synthesize() に speed パラメータを追加（3箇所）

## テスト結果

```
============================= test session starts ==============================
platform linux -- Python 3.13.11, pytest-9.0.2, pluggy-1.6.0
collected 299 items

============================== 299 tests PASSED ================================
```

全 299 テスト PASS（既存テスト 295 件 + 新規テスト 4 件）

## 実装の詳細

### 1. synthesize() への speed パラメータ追加 (T041-T042)

`src/aquestalk_client.py`:
```python
def synthesize(self, text: str, speed: int | None = None) -> bytes:
    """Synthesize text to audio.

    Args:
        text: Text to synthesize (can include AquesTalk tags like <NUM VAL=123>)
        speed: Override speed (default: use config.speed)

    Returns:
        WAV audio data as bytes (16kHz, mono)
    """
    self.initialize()

    # Use provided speed or fall back to config
    actual_speed = speed if speed is not None else self.config.speed
```

- speed パラメータは Optional（None がデフォルト）
- None の場合は config.speed を使用
- 指定された場合は config.speed を上書き

### 2. 見出し速度調整の実装 (T045)

`src/aquestalk_pipeline.py`:
```python
# Heading emphasis: slow down heading speech for emphasis
HEADING_SPEED = 80

# process_pages_with_heading_sound() 内
if segment.strip():
    # Use slower speed for headings (FR-011: 見出しをゆっくり読む)
    if is_heading_segment:
        wav_bytes = synthesizer.synthesize(segment, speed=HEADING_SPEED)
    else:
        wav_bytes = synthesizer.synthesize(segment)
```

- `HEADING_SPEED = 80` 定数を定義（FR-011 対応）
- 見出しセグメント（is_heading_segment == True）の場合のみ speed=80 を適用
- 通常セグメントは config.speed（ユーザー指定速度）を使用

### 3. Phase 2 テストの修正

Phase 2 で実装済みの効果音挿入テストの mock が speed パラメータを受け付けなかったため、以下の3つのテストを修正:
- `test_heading_sound_inserted_before_heading`
- `test_no_heading_sound_when_not_specified`
- `test_heading_sound_not_inserted_before_first_segment`

すべての mock_synthesize() に `speed=None` パラメータを追加。

## 実装のハイライト

### 見出し強調の実現方法

AquesTalk には直接的な「強調」や「音量」の制御機能がないため、速度を遅くすることで強調感を出す。

- デフォルト速度: 100
- 見出し速度: 80（20%遅い）
- 効果音 + 速度低下の組み合わせで「ここは見出し」という印象を与える

### 実装パターンの一貫性

VOICEVOX 版（`src/xml_pipeline.py`）と同様に：
- `HEADING_MARKER` でセグメント分割
- 見出しセグメント（i > 0）に特別な処理を適用
- 効果音挿入と速度調整を組み合わせた見出し強調

## 注意点

### 次 Phase (Phase 4) への引き継ぎ
- User Story 1 (基本音声生成) と User Story 2 (見出し効果音 + 速度調整) が完了
- Phase 4 では速度以外のパラメータ（voice, pitch）の調整機能を追加
- --speed, --voice, --pitch オプションは既に実装済み（Phase 2）
- Phase 4 では AquesTalk の全パラメータがユーザーから調整可能になることを検証

### 実装済みの機能
- load_heading_sound(): 効果音読み込み + 16kHz リサンプリング（Phase 2）
- process_pages_with_heading_sound(): 効果音挿入 + 見出し速度調整（Phase 2 + Phase 3）
- --heading-sound CLI オプション（Phase 2）
- synthesize() speed パラメータ（Phase 3）

## 実装のミス・課題
- なし（全テスト PASS、既存機能にリグレッションなし）
