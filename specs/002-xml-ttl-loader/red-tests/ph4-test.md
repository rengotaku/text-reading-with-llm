# Phase 4 RED Tests

## サマリー
- Phase: Phase 4 - パイプライン統合
- FAIL テスト数: 17
- テストファイル: tests/test_xml_pipeline.py

## FAIL テスト一覧

| テストファイル | テストクラス | テストメソッド | 期待動作 |
|---------------|-------------|---------------|---------|
| tests/test_xml_pipeline.py | TestParseArgsRequiredInput | test_parse_args_requires_input | --input 引数がないとエラー (exit code 2) |
| tests/test_xml_pipeline.py | TestParseArgsRequiredInput | test_parse_args_accepts_input_long | --input 引数を受け付ける |
| tests/test_xml_pipeline.py | TestParseArgsRequiredInput | test_parse_args_accepts_input_short | -i 短縮形を受け付ける |
| tests/test_xml_pipeline.py | TestParseArgsDefaults | test_output_default | --output のデフォルトは ./output |
| tests/test_xml_pipeline.py | TestParseArgsDefaults | test_start_page_default | --start-page のデフォルトは 1 |
| tests/test_xml_pipeline.py | TestParseArgsDefaults | test_end_page_default | --end-page のデフォルトは None |
| tests/test_xml_pipeline.py | TestParseArgsDefaults | test_style_id_default | --style-id のデフォルトは 13 |
| tests/test_xml_pipeline.py | TestParseArgsDefaults | test_speed_default | --speed のデフォルトは 1.0 |
| tests/test_xml_pipeline.py | TestParseArgsDefaults | test_voicevox_dir_default | --voicevox-dir のデフォルトは ./voicevox_core_cuda |
| tests/test_xml_pipeline.py | TestParseArgsCustomValues | test_output_custom | --output にカスタム値を設定 |
| tests/test_xml_pipeline.py | TestParseArgsCustomValues | test_output_short | -o 短縮形を受け付ける |
| tests/test_xml_pipeline.py | TestParseArgsCustomValues | test_start_page_custom | --start-page にカスタム値を設定 |
| tests/test_xml_pipeline.py | TestParseArgsCustomValues | test_end_page_custom | --end-page にカスタム値を設定 |
| tests/test_xml_pipeline.py | TestParseArgsCustomValues | test_style_id_custom | --style-id にカスタム値を設定 |
| tests/test_xml_pipeline.py | TestParseArgsCustomValues | test_speed_custom | --speed にカスタム値を設定 |
| tests/test_xml_pipeline.py | TestParseArgsCustomValues | test_voicevox_dir_custom | --voicevox-dir にカスタム値を設定 |
| tests/test_xml_pipeline.py | TestFileNotFoundError | test_file_not_found_raises_error | 存在しないファイルで FileNotFoundError |
| tests/test_xml_pipeline.py | TestFileNotFoundError | test_file_not_found_error_message | エラーメッセージにファイルパスを含む |
| tests/test_xml_pipeline.py | TestInvalidXmlError | test_invalid_xml_raises_parse_error | 不正な XML で ParseError |
| tests/test_xml_pipeline.py | TestInvalidXmlError | test_empty_file_raises_error | 空ファイルでエラー |
| tests/test_xml_pipeline.py | TestInvalidXmlError | test_non_xml_content_raises_error | XML でない内容でエラー |

## 実装ヒント

### parse_args() 関数

`src/xml_pipeline.py` に以下の引数パーサーを実装:

```python
import argparse

def parse_args(args=None):
    """Parse command line arguments.

    Args:
        args: List of arguments (for testing). If None, uses sys.argv.

    Returns:
        argparse.Namespace with parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate TTS audio from XML book files"
    )

    # Required
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input XML file path"
    )

    # Optional with defaults
    parser.add_argument(
        "--output", "-o",
        default="./output",
        help="Output directory (default: ./output)"
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="Start page number (default: 1)"
    )
    parser.add_argument(
        "--end-page",
        type=int,
        default=None,
        help="End page number (default: last page)"
    )
    parser.add_argument(
        "--style-id",
        type=int,
        default=13,
        help="VOICEVOX style ID (default: 13)"
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speech speed (default: 1.0)"
    )
    parser.add_argument(
        "--voicevox-dir",
        default="./voicevox_core_cuda",
        help="VOICEVOX Core directory (default: ./voicevox_core_cuda)"
    )

    return parser.parse_args(args)
```

### main() 関数

```python
def main(args=None):
    """Main entry point.

    Args:
        args: List of arguments (for testing). If None, uses sys.argv.
    """
    parsed = parse_args(args)

    # Check file existence
    input_path = Path(parsed.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {parsed.input}")

    # Parse XML (will raise ParseError for invalid XML)
    from src.xml_parser import parse_book_xml
    pages = parse_book_xml(input_path)

    # ... rest of pipeline integration
```

### argparse 属性名の注意

- `--start-page` は `args.start_page` (ハイフンがアンダースコアに変換)
- `--end-page` は `args.end_page`
- `--style-id` は `args.style_id`
- `--voicevox-dir` は `args.voicevox_dir`

## FAIL 出力例

```
ERRORS
_________________ ERROR collecting tests/test_xml_pipeline.py __________________
ImportError while importing test module '/data/projects/text-reading-with-llm/tests/test_xml_pipeline.py'.
tests/test_xml_pipeline.py:17: in <module>
    from src.xml_pipeline import parse_args, main
E   ModuleNotFoundError: No module named 'src.xml_pipeline'

=========================== short test summary info ============================
ERROR tests/test_xml_pipeline.py
!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.10s ===============================
```

## 次のステップ

1. `src/xml_pipeline.py` を作成
2. `parse_args()` 関数を実装
3. `main()` 関数を実装
4. ファイル存在チェックを追加
5. XML パースエラーハンドリングを追加
6. `make test` で GREEN 確認
