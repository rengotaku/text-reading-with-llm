# Phase 3 RED Tests

## サマリー
- Phase: Phase 3 - User Story 2: 見出し効果音の挿入
- FAIL テスト数: 4
- PASS テスト数: 14 (既存機能のテスト)
- テストファイル:
  - tests/test_aquestalk_pipeline.py
  - tests/test_aquestalk_client.py

## 分析結果

Phase 2 で既に実装済みの機能:
- `load_heading_sound()` - 効果音読み込み + 16kHz リサンプリング
- `--heading-sound` CLI オプション
- `process_pages_with_heading_sound()` - 見出しマーカー分割 + 効果音挿入
- 効果音ファイルが見つからない場合の警告

Phase 3 で実装が必要な機能:
- `synthesize()` に `speed` パラメータを追加 (FR-011)
- 見出しセグメントを speed=80 で合成する処理 (FR-011: 見出しをゆっくり読む)

## FAIL テスト一覧

| テストファイル | テストメソッド | 期待動作 |
|---------------|---------------|---------|
| tests/test_aquestalk_client.py | test_synthesize_accepts_speed_parameter | synthesize() が speed パラメータを受け付ける |
| tests/test_aquestalk_client.py | test_synthesize_speed_80_for_heading_emphasis | speed=80 で見出しをゆっくり読み上げる |
| tests/test_aquestalk_client.py | test_synthesize_speed_overrides_config | speed パラメータが config.speed を上書きする |
| tests/test_aquestalk_pipeline.py | test_heading_synthesized_with_speed_80 | 見出しセグメントは speed=80 で合成される |

## PASS テスト一覧 (既存機能確認)

| テストファイル | テストクラス | テスト数 |
|---------------|-------------|---------|
| tests/test_aquestalk_pipeline.py | TestLoadHeadingSound | 4 |
| tests/test_aquestalk_pipeline.py | TestHeadingSoundInsertion | 3 |
| tests/test_aquestalk_pipeline.py | TestHeadingSoundFileNotFoundWarning | 4 |
| tests/test_aquestalk_client.py | TestHeadingSpeedAdjustmentClient | 2 (定数テスト) |

## 実装ヒント

### 1. AquesTalkSynthesizer.synthesize() に speed パラメータを追加

`src/aquestalk_client.py`:
```python
def synthesize(self, text: str, speed: int | None = None) -> bytes:
    """Synthesize text to audio.

    Args:
        text: Text to synthesize
        speed: Override speed (default: use config.speed)

    Returns:
        WAV audio data as bytes
    """
    actual_speed = speed if speed is not None else self.config.speed
    # ... 合成処理
```

### 2. process_pages_with_heading_sound() で見出しに speed=80 を適用

`src/aquestalk_pipeline.py`:
```python
# 見出しの速度定数
HEADING_SPEED = 80

# セグメント処理部分
if is_heading_segment:
    # 見出しはゆっくり読む (FR-011)
    wav_bytes = synthesizer.synthesize(segment, speed=HEADING_SPEED)
else:
    # 通常セグメントはユーザー指定速度
    wav_bytes = synthesizer.synthesize(segment, speed=args.speed)
```

## FAIL 出力例

```
FAILED tests/test_aquestalk_client.py::TestHeadingSpeedAdjustmentClient::test_synthesize_accepts_speed_parameter
    TypeError: AquesTalkSynthesizer.synthesize() got an unexpected keyword argument 'speed'

FAILED tests/test_aquestalk_client.py::TestHeadingSpeedAdjustmentClient::test_synthesize_speed_80_for_heading_emphasis
    TypeError: AquesTalkSynthesizer.synthesize() got an unexpected keyword argument 'speed'

FAILED tests/test_aquestalk_client.py::TestHeadingSpeedAdjustmentClient::test_synthesize_speed_overrides_config
    TypeError: AquesTalkSynthesizer.synthesize() got an unexpected keyword argument 'speed'

FAILED tests/test_aquestalk_pipeline.py::TestHeadingSpeedAdjustment::test_heading_synthesized_with_speed_80
    AssertionError: Heading should use speed=80 for emphasis, got 100
    assert 100 == 80
```

## make test 出力

```
============================= test session starts ==============================
platform linux -- Python 3.13.11, pytest-9.0.2, pluggy-1.6.0
collected 299 items

tests/test_aquestalk_client.py::TestHeadingSpeedAdjustmentClient::test_synthesize_accepts_speed_parameter FAILED
tests/test_aquestalk_client.py::TestHeadingSpeedAdjustmentClient::test_synthesize_speed_80_for_heading_emphasis FAILED
tests/test_aquestalk_client.py::TestHeadingSpeedAdjustmentClient::test_synthesize_speed_overrides_config FAILED
tests/test_aquestalk_pipeline.py::TestHeadingSpeedAdjustment::test_heading_synthesized_with_speed_80 FAILED
========================= 4 failed, 295 passed in 0.81s =========================
```

## 次ステップ

phase-executor が以下を実行:
1. RED tests を読み込み (T041)
2. synthesize() に speed パラメータを追加 (T042-T044 は既存機能のため不要)
3. 見出しセグメントに speed=80 を適用 (T045)
4. `make test` PASS を確認 (T046)
5. 検証 + phase output 生成 (T047-T048)
