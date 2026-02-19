# Phase 2 RED Tests: XMLファイルから読み辞書を生成

**Date**: 2026-02-18
**Status**: RED (FAIL確認済み)
**User Story**: US1 - XMLファイルから読み辞書を生成

## サマリー

| 項目 | 値 |
|------|-----|
| 作成テスト数 | 9 |
| FAIL数 | 9 |
| テストファイル | tests/test_generate_reading_dict.py |

## FAILテスト一覧

| テストファイル | テストメソッド | 期待動作 |
|--------------|--------------|----------|
| tests/test_generate_reading_dict.py | test_xml_input_calls_parse_book2_xml | XML入力時にparse_book2_xmlが呼ばれ、split_into_pagesは呼ばれない |
| tests/test_generate_reading_dict.py | test_md_input_does_not_call_parse_book2_xml | MD入力時にparse_book2_xmlは呼ばれない |
| tests/test_generate_reading_dict.py | test_xml_groups_by_chapter_and_extracts_terms | チャプター単位でグループ化され各グループからextract_technical_termsが呼ばれる |
| tests/test_generate_reading_dict.py | test_xml_combined_text_per_chapter | 同一チャプターのテキストが結合されてextract_technical_termsに渡される |
| tests/test_generate_reading_dict.py | test_xml_all_terms_collected_across_chapters | 複数チャプターの用語が全て収集されgenerate_readings_batchに渡される |
| tests/test_generate_reading_dict.py | test_xml_dict_saved_via_save_dict | XML入力で辞書がsave_dictを通じてXMLパスと共に保存される |
| tests/test_generate_reading_dict.py | test_xml_get_dict_path_called_with_xml_input | get_dict_pathがXML入力パスで呼ばれる |
| tests/test_generate_reading_dict.py | test_xml_merge_combines_existing_and_new | --mergeで既存辞書と新規エントリが統合される |
| tests/test_generate_reading_dict.py | test_xml_merge_skips_existing_terms | --mergeで既存用語はLLMに再送信されない |

## 実装ヒント

- `main()`: `input_path.suffix` で `.xml` / `.md` を判定し分岐を追加する
- XML分岐: `from src.xml2_parser import parse_book2_xml` をインポートし、`parse_book2_xml(input_path)` を呼ぶ
- チャプターグループ化: `itertools.groupby` で `ContentItem.chapter_number` をキーにグループ化
- 各グループのテキストを結合して `extract_technical_terms()` に渡す
- 用語収集後は既存のMDフローと同じ: `generate_readings_batch()` → `save_dict()`
- `--merge` ロジックは既存コードをそのまま流用可能（拡張子分岐の前に実行済み）

## make test 出力 (抜粋)

```
FAILED tests/test_generate_reading_dict.py::TestXmlInputCallsParseBook2Xml::test_xml_input_calls_parse_book2_xml - AttributeError: <module 'src.generate_reading_dict'> does not have the attribute 'parse_book2_xml'
FAILED tests/test_generate_reading_dict.py::TestXmlInputCallsParseBook2Xml::test_md_input_does_not_call_parse_book2_xml - AttributeError
FAILED tests/test_generate_reading_dict.py::TestXmlChapterGroupingAndTermExtraction::test_xml_groups_by_chapter_and_extracts_terms - AttributeError
FAILED tests/test_generate_reading_dict.py::TestXmlChapterGroupingAndTermExtraction::test_xml_combined_text_per_chapter - AttributeError
FAILED tests/test_generate_reading_dict.py::TestXmlChapterGroupingAndTermExtraction::test_xml_all_terms_collected_across_chapters - AttributeError
FAILED tests/test_generate_reading_dict.py::TestXmlDictSavePath::test_xml_dict_saved_via_save_dict - AttributeError
FAILED tests/test_generate_reading_dict.py::TestXmlDictSavePath::test_xml_get_dict_path_called_with_xml_input - AttributeError
FAILED tests/test_generate_reading_dict.py::TestXmlMergeOption::test_xml_merge_combines_existing_and_new - AttributeError
FAILED tests/test_generate_reading_dict.py::TestXmlMergeOption::test_xml_merge_skips_existing_terms - AttributeError
9 failed in 0.36s
```
