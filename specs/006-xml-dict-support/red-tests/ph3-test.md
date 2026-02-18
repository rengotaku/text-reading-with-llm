# Phase 3 RED Tests: Markdownファイルの既存動作維持 + エッジケース

**Date**: 2026-02-18
**Status**: RED (FAIL確認済み)
**User Story**: US2 - Markdownファイルの既存動作を維持

## サマリー

| 項目 | 値 |
|------|-----|
| 作成テスト数 | 14 (Phase 3 新規: 11, うちFAIL: 3) |
| FAIL数 | 3 |
| テストファイル | tests/test_generate_reading_dict.py |

## FAILテスト一覧

| テストファイル | テストメソッド | 期待動作 |
|--------------|--------------|----------|
| tests/test_generate_reading_dict.py | TestInvalidXmlErrorExit::test_malformed_xml_exits_with_error | 不正XMLファイル指定時に `sys.exit(1)` で終了する |
| tests/test_generate_reading_dict.py | TestInvalidXmlErrorExit::test_malformed_xml_logs_error | 不正XMLファイルの場合エラーメッセージがログに出力される |
| tests/test_generate_reading_dict.py | TestInvalidXmlErrorExit::test_xml_parse_error_caught_gracefully | XMLパースエラー（ET.ParseError）がキャッチされ `sys.exit(1)` で終了する |

## PASSテスト一覧（Phase 3 新規、既に動作済み）

| テストクラス | テスト数 | 状態 | 理由 |
|-------------|---------|------|------|
| TestMdInputUsesSplitIntoPages | 2 | PASS | MD分岐は Phase 2 で実装済み |
| TestUnsupportedExtensionError | 3 | PASS | 未対応拡張子の `sys.exit(1)` は Phase 2 で実装済み |
| TestEmptyXmlGeneratesEmptyDict | 3 | PASS | 空リスト返却時は正常終了する既存ロジックで対応済み |
| TestChapterNumberNoneContentItem | 3 | PASS | `chapter_number=None` は `-1` としてソートされ groupby で処理済み |

## 実装ヒント

- `main()` の XML 分岐（`parse_book2_xml()` 呼び出し箇所）で `xml.etree.ElementTree.ParseError` を `try/except` でキャッチする
- キャッチ時に `logger.error()` でエラーメッセージを出力し、`sys.exit(1)` で終了する
- `except ET.ParseError as e:` のパターンを使用

## make test 出力 (抜粋)

```
FAILED tests/test_generate_reading_dict.py::TestInvalidXmlErrorExit::test_malformed_xml_exits_with_error - xml.etree.ElementTree.ParseError: mismatched tag: line 5, column 6
FAILED tests/test_generate_reading_dict.py::TestInvalidXmlErrorExit::test_malformed_xml_logs_error - xml.etree.ElementTree.ParseError: mismatched tag: line 5, column 6
FAILED tests/test_generate_reading_dict.py::TestInvalidXmlErrorExit::test_xml_parse_error_caught_gracefully - xml.etree.ElementTree.ParseError: invalid XML
3 failed, 20 passed in 0.09s
```
