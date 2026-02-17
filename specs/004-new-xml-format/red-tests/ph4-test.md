# Phase 4 RED Tests

## サマリー

- Phase: Phase 4 - User Story 3: 音声パイプライン統合
- FAIL テスト数: 33
- テストファイル: tests/test_xml2_pipeline.py

## FAIL テスト一覧

| テストクラス | テストメソッド | 期待動作 |
|-------------|---------------|---------|
| TestParseArgsDefaults | test_parse_args_input_required | --input 引数が必須 |
| TestParseArgsDefaults | test_parse_args_accepts_input_long | --input 引数を受け付ける |
| TestParseArgsDefaults | test_parse_args_accepts_input_short | -i 短縮形を受け付ける |
| TestParseArgsDefaults | test_output_default | --output のデフォルトは ./output |
| TestParseArgsDefaults | test_chapter_sound_default | --chapter-sound のデフォルトは assets/sounds/chapter.mp3 |
| TestParseArgsDefaults | test_section_sound_default | --section-sound のデフォルトは assets/sounds/section.mp3 |
| TestParseArgsDefaults | test_style_id_default | --style-id のデフォルトは 13 |
| TestParseArgsDefaults | test_speed_default | --speed のデフォルトは 1.0 |
| TestParseArgsDefaults | test_voicevox_dir_default | --voicevox-dir のデフォルトは ./voicevox_core |
| TestParseArgsDefaults | test_max_chunk_chars_default | --max-chunk-chars のデフォルトは 500 |
| TestParseArgsCustomSounds | test_chapter_sound_custom | --chapter-sound にカスタム値を設定 |
| TestParseArgsCustomSounds | test_section_sound_custom | --section-sound にカスタム値を設定 |
| TestParseArgsCustomSounds | test_both_sounds_custom | --chapter-sound と --section-sound を両方カスタム設定 |
| TestParseArgsCustomSounds | test_output_custom | --output にカスタム値を設定 |
| TestParseArgsCustomSounds | test_style_id_custom | --style-id にカスタム値を設定 |
| TestParseArgsCustomSounds | test_speed_custom | --speed にカスタム値を設定 |
| TestLoadSoundMonoConversion | test_load_sound_returns_numpy_array | load_sound は numpy 配列を返す |
| TestLoadSoundMonoConversion | test_load_sound_stereo_to_mono_conversion | ステレオ音声をモノラルに変換する |
| TestLoadSoundMonoConversion | test_load_sound_resampling | 異なるサンプルレートをリサンプリングする |
| TestLoadSoundMonoConversion | test_load_sound_already_correct_sample_rate | 既に正しいサンプルレートの場合はリサンプリングしない |
| TestLoadSoundMonoConversion | test_load_sound_normalization | 音量が正規化される |
| TestLoadSoundMonoConversion | test_load_sound_returns_float32 | float32 型で返却される |
| TestProcessContentWithMarkers | test_process_content_function_exists | process_content 関数が存在する |
| TestProcessContentWithMarkers | test_process_content_accepts_content_items | process_content は ContentItem リストを受け付ける |
| TestProcessContentWithMarkers | test_process_content_with_chapter_marker_includes_chapter_sound | CHAPTER_MARKER を含むテキストで chapter_sound が挿入される |
| TestProcessContentWithMarkers | test_process_content_with_section_marker_includes_section_sound | SECTION_MARKER を含むテキストで section_sound が挿入される |
| TestProcessContentWithMarkers | test_process_content_mixed_markers | CHAPTER_MARKER と SECTION_MARKER の両方を正しく処理 |
| TestProcessContentWithMarkers | test_process_content_no_markers | マーカーなしのテキストはそのまま処理される |
| TestMainFunction | test_main_function_exists | main 関数が存在する |
| TestMainFunction | test_main_file_not_found_raises_error | 存在しないファイルでエラー |
| TestMainFunction | test_main_invalid_xml_raises_error | 不正な XML でエラー |
| TestEdgeCases | test_parse_args_empty_chapter_sound_path | --chapter-sound に空パスを設定した場合 |
| TestEdgeCases | test_parse_args_relative_paths | 相対パスを受け付ける |

## 実装ヒント

### src/xml2_pipeline.py に実装するもの

1. **parse_args(args=None)**
   ```python
   def parse_args(args=None):
       parser = argparse.ArgumentParser(description="Generate TTS audio from book2.xml files")
       parser.add_argument("--input", "-i", required=True)
       parser.add_argument("--output", "-o", default="./output")
       parser.add_argument("--chapter-sound", default="assets/sounds/chapter.mp3")
       parser.add_argument("--section-sound", default="assets/sounds/section.mp3")
       parser.add_argument("--style-id", type=int, default=13)
       parser.add_argument("--speed", type=float, default=1.0)
       parser.add_argument("--voicevox-dir", default="./voicevox_core")
       parser.add_argument("--max-chunk-chars", type=int, default=500)
       return parser.parse_args(args)
   ```

2. **load_sound(sound_path: Path, target_sr: int = 24000) -> np.ndarray**
   - 既存の xml_pipeline.py::load_heading_sound() を参考に実装
   - ステレオ → モノラル変換
   - サンプルレート変換（リサンプリング）
   - 音量正規化
   - float32 型で返却

3. **process_content(content_items: list[ContentItem], ...) -> ...**
   - ContentItem リストを受け取る
   - CHAPTER_MARKER で分割して chapter_sound を挿入
   - SECTION_MARKER で分割して section_sound を挿入
   - マーカーなしテキストはそのまま処理

4. **main(args=None)**
   - エントリポイント
   - ファイル存在チェック（FileNotFoundError）
   - XML パースエラーハンドリング

### マーカー定数（xml2_parser.py から import）

```python
from src.xml2_parser import (
    CHAPTER_MARKER,  # "\uE001"
    SECTION_MARKER,  # "\uE002"
    ContentItem,
    parse_book2_xml,
)
```

## FAIL 出力例

```
tests/test_xml2_pipeline.py::TestParseArgsDefaults::test_parse_args_input_required FAILED
tests/test_xml2_pipeline.py::TestParseArgsDefaults::test_parse_args_accepts_input_long FAILED
...

E       ModuleNotFoundError: No module named 'src.xml2_pipeline'

tests/test_xml2_pipeline.py:45: ModuleNotFoundError
...

=========================== short test summary info ============================
FAILED tests/test_xml2_pipeline.py::TestParseArgsDefaults::test_parse_args_input_required
FAILED tests/test_xml2_pipeline.py::TestParseArgsDefaults::test_parse_args_accepts_input_long
FAILED tests/test_xml2_pipeline.py::TestParseArgsDefaults::test_parse_args_accepts_input_short
FAILED tests/test_xml2_pipeline.py::TestParseArgsDefaults::test_output_default
FAILED tests/test_xml2_pipeline.py::TestParseArgsDefaults::test_chapter_sound_default
FAILED tests/test_xml2_pipeline.py::TestParseArgsDefaults::test_section_sound_default
FAILED tests/test_xml2_pipeline.py::TestParseArgsDefaults::test_style_id_default
FAILED tests/test_xml2_pipeline.py::TestParseArgsDefaults::test_speed_default
FAILED tests/test_xml2_pipeline.py::TestParseArgsDefaults::test_voicevox_dir_default
FAILED tests/test_xml2_pipeline.py::TestParseArgsDefaults::test_max_chunk_chars_default
FAILED tests/test_xml2_pipeline.py::TestParseArgsCustomSounds::test_chapter_sound_custom
FAILED tests/test_xml2_pipeline.py::TestParseArgsCustomSounds::test_section_sound_custom
FAILED tests/test_xml2_pipeline.py::TestParseArgsCustomSounds::test_both_sounds_custom
FAILED tests/test_xml2_pipeline.py::TestParseArgsCustomSounds::test_output_custom
FAILED tests/test_xml2_pipeline.py::TestParseArgsCustomSounds::test_style_id_custom
FAILED tests/test_xml2_pipeline.py::TestParseArgsCustomSounds::test_speed_custom
FAILED tests/test_xml2_pipeline.py::TestLoadSoundMonoConversion::test_load_sound_returns_numpy_array
FAILED tests/test_xml2_pipeline.py::TestLoadSoundMonoConversion::test_load_sound_stereo_to_mono_conversion
FAILED tests/test_xml2_pipeline.py::TestLoadSoundMonoConversion::test_load_sound_resampling
FAILED tests/test_xml2_pipeline.py::TestLoadSoundMonoConversion::test_load_sound_already_correct_sample_rate
FAILED tests/test_xml2_pipeline.py::TestLoadSoundMonoConversion::test_load_sound_normalization
FAILED tests/test_xml2_pipeline.py::TestLoadSoundMonoConversion::test_load_sound_returns_float32
FAILED tests/test_xml2_pipeline.py::TestProcessContentWithMarkers::test_process_content_function_exists
FAILED tests/test_xml2_pipeline.py::TestProcessContentWithMarkers::test_process_content_accepts_content_items
FAILED tests/test_xml2_pipeline.py::TestProcessContentWithMarkers::test_process_content_with_chapter_marker_includes_chapter_sound
FAILED tests/test_xml2_pipeline.py::TestProcessContentWithMarkers::test_process_content_with_section_marker_includes_section_sound
FAILED tests/test_xml2_pipeline.py::TestProcessContentWithMarkers::test_process_content_mixed_markers
FAILED tests/test_xml2_pipeline.py::TestProcessContentWithMarkers::test_process_content_no_markers
FAILED tests/test_xml2_pipeline.py::TestMainFunction::test_main_function_exists
FAILED tests/test_xml2_pipeline.py::TestMainFunction::test_main_file_not_found_raises_error
FAILED tests/test_xml2_pipeline.py::TestMainFunction::test_main_invalid_xml_raises_error
FAILED tests/test_xml2_pipeline.py::TestEdgeCases::test_parse_args_empty_chapter_sound_path
FAILED tests/test_xml2_pipeline.py::TestEdgeCases::test_parse_args_relative_paths
======================== 33 failed, 371 passed in 0.85s ========================
```

## 次のステップ

phase-executor が「実装 (GREEN)」を実行:
- T047: RED テストを読む
- T048: parse_args() を実装
- T049: load_sound() を実装
- T050: process_content() を実装
- T051: main() を実装
- T052: make test PASS を確認
