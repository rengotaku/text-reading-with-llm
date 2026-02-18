# Phase 3 RED Tests: チャプター単位の分割出力

**Date**: 2026-02-18
**Status**: RED (FAIL確認済み)
**User Story**: US2 - チャプター単位の分割出力

## サマリー

| 項目 | 値 |
|------|-----|
| 作成テスト数 | 30 |
| FAIL数 | 30 |
| 既存テスト | 413 passed (リグレッションなし) |
| テストファイル | tests/test_xml2_parser.py, tests/test_xml2_pipeline.py |

## FAILテスト一覧

### tests/test_xml2_parser.py (11テスト)

| テストクラス | テストメソッド | 期待動作 |
|-------------|--------------|----------|
| TestContentItemHasChapterNumber | test_content_item_has_chapter_number_attribute | ContentItem に chapter_number 属性が存在する |
| TestContentItemHasChapterNumber | test_content_item_chapter_number_default_is_none | chapter_number のデフォルト値は None |
| TestContentItemHasChapterNumber | test_content_item_chapter_number_accepts_int | chapter_number に整数を設定できる |
| TestContentItemHasChapterNumber | test_content_item_chapter_number_accepts_larger_int | chapter_number に大きな整数を設定できる |
| TestContentItemHasChapterNumber | test_content_item_backward_compatible_without_chapter_number | 既存コードとの後方互換性を維持 |
| TestParseBook2XmlAssignsChapterNumbers | test_chapter_1_items_have_chapter_number_1 | chapter 1 内のコンテンツの chapter_number が 1 |
| TestParseBook2XmlAssignsChapterNumbers | test_chapter_2_items_have_chapter_number_2 | chapter 2 内のコンテンツの chapter_number が 2 |
| TestParseBook2XmlAssignsChapterNumbers | test_chapter_3_items_have_chapter_number_3 | chapter 3 内のコンテンツの chapter_number が 3 |
| TestParseBook2XmlAssignsChapterNumbers | test_section_inherits_parent_chapter_number | section 内のコンテンツは親 chapter の chapter_number を引き継ぐ |
| TestParseBook2XmlAssignsChapterNumbers | test_no_chapter_xml_has_none_chapter_number | chapter 要素がない XML では chapter_number は None |
| TestParseBook2XmlAssignsChapterNumbers | test_chapter_heading_itself_has_chapter_number | chapter の見出し自体にも chapter_number が設定される |

### tests/test_xml2_pipeline.py (19テスト)

| テストクラス | テストメソッド | 期待動作 |
|-------------|--------------|----------|
| TestSanitizeFilename | test_sanitize_filename_function_exists | sanitize_filename 関数が存在する |
| TestSanitizeFilename | test_sanitize_filename_english_title | 英語タイトル → "ch01_Introduction" |
| TestSanitizeFilename | test_sanitize_filename_japanese_title | 日本語タイトル → "ch02_untitled" |
| TestSanitizeFilename | test_sanitize_filename_mixed_title | 混合タイトル → "ch03_Python" |
| TestSanitizeFilename | test_sanitize_filename_empty_title | 空タイトル → "ch01_untitled" |
| TestSanitizeFilename | test_sanitize_filename_special_characters | 特殊文字は除去される |
| TestSanitizeFilename | test_sanitize_filename_number_zero_padded | 章番号はゼロ埋め2桁 |
| TestSanitizeFilename | test_sanitize_filename_large_chapter_number | 2桁以上の章番号に対応 |
| TestSanitizeFilename | test_sanitize_filename_max_length | タイトル部分は最大20文字 |
| TestSanitizeFilename | test_sanitize_filename_spaces_to_underscores | スペースはアンダースコアに変換 |
| TestProcessChaptersCreatesChapterFiles | test_process_chapters_function_exists | process_chapters 関数が存在する |
| TestProcessChaptersCreatesChapterFiles | test_process_chapters_creates_chapters_directory | chapters/ ディレクトリを作成する |
| TestProcessChaptersCreatesChapterFiles | test_process_chapters_creates_chapter_wav_files | chapter ごとの WAV ファイルを作成する |
| TestProcessChaptersCreatesChapterFiles | test_process_chapters_filename_format | ファイル名が ch{NN}_{title}.wav 形式 |
| TestProcessChaptersCreatesChapterFiles | test_process_chapters_three_chapters | 3 chapter → 3 WAV ファイル |
| TestProcessChaptersCreatesBookWav | test_process_chapters_creates_book_wav | 全 chapter を結合した book.wav を生成 |
| TestProcessChaptersCreatesBookWav | test_process_chapters_book_wav_and_chapter_files_coexist | book.wav と chapters/ が両方存在する |
| TestProcessContentWithoutChaptersCreatesBookWav | test_no_chapters_creates_only_book_wav | chapter なしでも book.wav のみ生成 |
| TestProcessContentWithoutChaptersCreatesBookWav | test_mixed_none_and_numbered_chapters | None + 数値の混在ケース |

## 実装ヒント

### src/xml2_parser.py

- `ContentItem` dataclass に `chapter_number: int | None = None` フィールドを追加
- `parse_book2_xml()` 内の `process_element()` で chapter 要素を処理する際に `current_chapter_number` を追跡
- chapter 内の子要素（paragraph, section, heading, list）に `chapter_number` を設定
- chapter 外のコンテンツは `chapter_number=None` のまま

### src/xml2_pipeline.py

- `sanitize_filename(number: int, title: str) -> str` 関数を新規作成
  - 形式: `ch{NN}_{sanitized_title}`
  - 半角英数字とアンダースコアのみ許可（`re.sub(r'[^a-zA-Z0-9_]', '', ...)`)
  - 空の場合は "untitled"
  - タイトル部分最大20文字
  - スペースはアンダースコアに変換

- `process_chapters()` 関数を新規作成
  - content_items を chapter_number でグループ化
  - 各 chapter の音声を生成して `chapters/ch{NN}_{title}.wav` に保存
  - 全 chapter を結合して `book.wav` に保存
  - chapter_number が全て None の場合は book.wav のみ生成

- エッジケース: chapter_number=None のアイテムと数値のアイテムが混在するケースへの対応

## make test 出力 (抜粋)

```
FAILED tests/test_xml2_parser.py::TestContentItemHasChapterNumber::test_content_item_has_chapter_number_attribute - AttributeError
FAILED tests/test_xml2_parser.py::TestContentItemHasChapterNumber::test_content_item_chapter_number_default_is_none - AttributeError
FAILED tests/test_xml2_parser.py::TestContentItemHasChapterNumber::test_content_item_chapter_number_accepts_int - TypeError
FAILED tests/test_xml2_parser.py::TestParseBook2XmlAssignsChapterNumbers::test_chapter_1_items_have_chapter_number_1 - AssertionError
FAILED tests/test_xml2_parser.py::TestParseBook2XmlAssignsChapterNumbers::test_no_chapter_xml_has_none_chapter_number - AttributeError
FAILED tests/test_xml2_pipeline.py::TestSanitizeFilename::test_sanitize_filename_function_exists - ImportError
FAILED tests/test_xml2_pipeline.py::TestProcessChaptersCreatesChapterFiles::test_process_chapters_function_exists - ImportError
FAILED tests/test_xml2_pipeline.py::TestProcessChaptersCreatesBookWav::test_process_chapters_creates_book_wav - ImportError
FAILED tests/test_xml2_pipeline.py::TestProcessContentWithoutChaptersCreatesBookWav::test_no_chapters_creates_only_book_wav - ImportError
...
30 failed, 413 passed in 1.17s
```
