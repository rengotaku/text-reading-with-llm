# Phase 2 RED Tests

## サマリー
- Phase: Phase 2 - User Story 1: XML から AquesTalk 音声生成 (Priority: P1)
- FAIL テスト数: 2 ファイル (import エラーで収集不可)
- テストファイル:
  - tests/test_aquestalk_client.py
  - tests/test_aquestalk_pipeline.py

## FAIL テスト一覧

| テストファイル | テストクラス/メソッド | 期待動作 |
|---------------|----------------------|---------|
| tests/test_aquestalk_client.py | TestAquesTalkConfig | AquesTalkConfig dataclass のデフォルト値とカスタム値テスト |
| tests/test_aquestalk_client.py | TestSynthesizeBasic | synthesize() が bytes を返し、ひらがな/カタカナ/漢字を処理 |
| tests/test_aquestalk_client.py | TestConvertNumbersToNumTags | 数字を `<NUM VAL=N>` タグに変換 |
| tests/test_aquestalk_client.py | TestAddPunctuation | 見出し/段落末に句点自動追加、二重追加回避 |
| tests/test_aquestalk_client.py | TestSynthesizerInitialization | AquesTalkSynthesizer の作成と初期化 |
| tests/test_aquestalk_pipeline.py | TestParseArgsRequiredInput | --input 引数が必須 |
| tests/test_aquestalk_pipeline.py | TestParseArgsDefaults | デフォルト値（speed=100, voice=100, pitch=100） |
| tests/test_aquestalk_pipeline.py | TestParseArgsCustomValues | カスタム値の設定 |
| tests/test_aquestalk_pipeline.py | TestMainGeneratesAudio | main() が WAV ファイルを生成 |
| tests/test_aquestalk_pipeline.py | TestPageRangeFiltering | --start-page, --end-page でページフィルタリング |
| tests/test_aquestalk_pipeline.py | TestFileNotFoundError | 存在しないファイルでエラー |
| tests/test_aquestalk_pipeline.py | TestInvalidXmlError | 不正な XML でパースエラー |

## テスト内容詳細

### tests/test_aquestalk_client.py

**TestAquesTalkConfig** (4 tests):
- `test_config_has_default_speed`: speed のデフォルトは 100
- `test_config_has_default_voice`: voice のデフォルトは 100
- `test_config_has_default_pitch`: pitch のデフォルトは 100
- `test_config_accepts_custom_values`: カスタム値を設定できる

**TestSynthesizeBasic** (5 tests):
- `test_synthesize_returns_bytes`: synthesize() は bytes を返す
- `test_synthesize_returns_non_empty_audio`: 空でない音声データを返す
- `test_synthesize_accepts_hiragana`: ひらがなを受け付ける
- `test_synthesize_accepts_katakana`: カタカナを受け付ける
- `test_synthesize_accepts_mixed_text`: 漢字かな混じり文を受け付ける

**TestConvertNumbersToNumTags** (7 tests):
- `test_convert_single_number`: 単一の数字を NUM タグに変換
- `test_convert_multiple_numbers`: 複数の数字を NUM タグに変換
- `test_convert_large_number`: 大きな数字を NUM タグに変換
- `test_preserve_text_without_numbers`: 数字がないテキストはそのまま
- `test_empty_string`: 空文字列の処理
- `test_year_number`: 年号の数字を変換
- `test_decimal_not_converted`: 小数点を含む数値は変換しない

**TestAddPunctuation** (9 tests):
- `test_add_punctuation_to_heading_without_period`: 句点がない見出しに句点を追加
- `test_no_duplicate_punctuation_heading`: 二重追加しない（見出し）
- `test_add_punctuation_to_paragraph_without_period`: 句点がない段落に句点を追加
- `test_no_duplicate_punctuation_paragraph`: 二重追加しない（段落）
- `test_preserve_exclamation_mark`: 感嘆符で終わる場合は句点を追加しない
- `test_preserve_question_mark`: 疑問符で終わる場合は句点を追加しない
- `test_empty_string`: 空文字列の処理
- `test_whitespace_only`: 空白のみの場合
- `test_unicode_punctuation`: 全角の感嘆符・疑問符も認識

**TestSynthesizerInitialization** (4 tests):
- `test_synthesizer_creation`: AquesTalkSynthesizer を作成できる
- `test_synthesizer_with_config`: AquesTalkConfig を指定して作成できる
- `test_synthesizer_initialize_method_exists`: initialize() メソッドが存在する
- `test_synthesizer_synthesize_method_exists`: synthesize() メソッドが存在する

### tests/test_aquestalk_pipeline.py

**TestParseArgsRequiredInput** (3 tests):
- `test_parse_args_requires_input`: --input 引数がないとエラー
- `test_parse_args_accepts_input_long`: --input 引数を受け付ける
- `test_parse_args_accepts_input_short`: -i 短縮形を受け付ける

**TestParseArgsDefaults** (6 tests):
- `test_output_default`: --output のデフォルトは ./output
- `test_start_page_default`: --start-page のデフォルトは 1
- `test_end_page_default`: --end-page のデフォルトは None
- `test_speed_default`: --speed のデフォルトは 100
- `test_voice_default`: --voice のデフォルトは 100
- `test_pitch_default`: --pitch のデフォルトは 100

**TestParseArgsCustomValues** (7 tests):
- `test_output_custom`: --output にカスタム値を設定
- `test_output_short`: -o 短縮形を受け付ける
- `test_start_page_custom`: --start-page にカスタム値を設定
- `test_end_page_custom`: --end-page にカスタム値を設定
- `test_speed_custom`: --speed にカスタム値を設定
- `test_voice_custom`: --voice にカスタム値を設定
- `test_pitch_custom`: --pitch にカスタム値を設定

**TestMainGeneratesAudio** (3 tests):
- `test_main_creates_output_directory`: main() は出力ディレクトリを作成する
- `test_main_generates_page_wav_files`: main() はページごとの WAV ファイルを生成する
- `test_main_generates_book_wav`: main() は結合済み book.wav を生成する

**TestPageRangeFiltering** (3 tests):
- `test_start_page_filters_pages`: --start-page でページをフィルタリング
- `test_end_page_filters_pages`: --end-page でページをフィルタリング
- `test_page_range_combination`: --start-page と --end-page の組み合わせ

**TestFileNotFoundError** (2 tests):
- `test_file_not_found_raises_error`: 存在しないファイルでエラー
- `test_file_not_found_error_message`: エラーメッセージにファイルパスを含む

**TestInvalidXmlError** (3 tests):
- `test_invalid_xml_raises_parse_error`: 不正な XML でパースエラー
- `test_empty_file_raises_error`: 空ファイルでエラー
- `test_non_xml_content_raises_error`: XML でない内容でエラー

## 実装ヒント

### src/aquestalk_client.py

```python
from dataclasses import dataclass

@dataclass
class AquesTalkConfig:
    speed: int = 100   # 50-300
    voice: int = 100   # 0-200
    pitch: int = 100   # 50-200

class AquesTalkSynthesizer:
    def __init__(self, config: AquesTalkConfig | None = None):
        self.config = config or AquesTalkConfig()

    def initialize(self) -> None:
        # AquesTalk10 ライブラリの初期化
        pass

    def synthesize(self, text: str) -> bytes:
        # テキストを音声に変換
        pass

def convert_numbers_to_num_tags(text: str) -> str:
    # 数字を <NUM VAL=N> タグに変換
    import re
    return re.sub(r'\d+', lambda m: f'<NUM VAL={m.group()}>', text)

def add_punctuation(text: str, is_heading: bool) -> str:
    # 見出し/段落末に句点を自動追加（二重追加回避）
    pass
```

### src/aquestalk_pipeline.py

```python
import argparse
from src.aquestalk_client import AquesTalkSynthesizer, AquesTalkConfig

def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--output", "-o", default="./output")
    parser.add_argument("--start-page", type=int, default=1)
    parser.add_argument("--end-page", type=int, default=None)
    parser.add_argument("--speed", type=int, default=100)
    parser.add_argument("--voice", type=int, default=100)
    parser.add_argument("--pitch", type=int, default=100)
    return parser.parse_args(args)

def main(args=None):
    parsed = parse_args(args)
    # ファイル存在チェック
    # XML パース
    # ページ処理
    # WAV 出力
    pass
```

## FAIL 出力例

```
============================= test session starts ==============================
platform linux -- Python 3.13.11, pytest-9.0.2, pluggy-1.6.0
collecting ... collected 225 items / 2 errors

==================================== ERRORS ====================================
_______________ ERROR collecting tests/test_aquestalk_client.py ________________
ImportError while importing test module '/data/projects/text-reading-with-llm/tests/test_aquestalk_client.py'.
Traceback:
tests/test_aquestalk_client.py:23: in <module>
    from src.aquestalk_client import (
E   ModuleNotFoundError: No module named 'src.aquestalk_client'

______________ ERROR collecting tests/test_aquestalk_pipeline.py _______________
ImportError while importing test module '/data/projects/text-reading-with-llm/tests/test_aquestalk_pipeline.py'.
Traceback:
tests/test_aquestalk_pipeline.py:22: in <module>
    from src.aquestalk_pipeline import parse_args, main
E   ModuleNotFoundError: No module named 'src.aquestalk_pipeline'

=========================== short test summary info ============================
ERROR tests/test_aquestalk_client.py
ERROR tests/test_aquestalk_pipeline.py
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!
============================== 2 errors in 0.20s ===============================
make: *** [Makefile:63: test] Error 2
```

## 次ステップ

phase-executor が以下を実行:
1. `src/aquestalk_client.py` を作成（AquesTalkConfig, AquesTalkSynthesizer, convert_numbers_to_num_tags, add_punctuation）
2. `src/aquestalk_pipeline.py` を作成（parse_args, main）
3. `make test` で GREEN を確認
4. `specs/003-aquestalk-tts/tasks/ph2-output.md` を生成
