# Phase 3 Output: チャプター単位の分割出力

**Date**: 2026-02-18
**Status**: 完了
**User Story**: US2 - チャプター単位の分割出力

## 実行タスク

- [x] T028 Read RED tests: specs/005-chapter-split-cleaning/red-tests/ph3-test.md
- [x] T029 [P] [US2] Add chapter_number field to ContentItem dataclass in src/xml2_parser.py
- [x] T030 [US2] Update parse_book2_xml() to track and assign chapter_number in src/xml2_parser.py
- [x] T031 [P] [US2] Implement sanitize_filename() helper in src/xml2_pipeline.py
- [x] T032 [US2] Implement process_chapters() function in src/xml2_pipeline.py
- [x] T033 [US2] Update main() to call process_chapters() in src/xml2_pipeline.py
- [x] T034 Verify `make test` PASS (GREEN)
- [x] T035 Verify `make test` passes all tests (including US1 regressions)

## 変更ファイル一覧

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/xml2_parser.py | 修正 | ContentItem に chapter_number フィールド追加、parse_book2_xml() で chapter 追跡ロジック追加 |
| src/xml2_pipeline.py | 修正 | sanitize_filename() 関数追加、process_chapters() 関数追加、main() を process_chapters() 呼び出しに変更 |

## 実装内容

### src/xml2_parser.py

**変更箇所 1**: ContentItem dataclass (L36-48)

`chapter_number: int | None = None` フィールドを追加:

```python
@dataclass
class ContentItem:
    """Content item extracted from XML.

    Attributes:
        item_type: Type of content ("paragraph", "heading", "list_item")
        text: Text content (may include markers)
        heading_info: Heading information (only for heading items)
        chapter_number: Chapter number (1, 2, 3, ...) or None for non-chapter content
    """
    item_type: str
    text: str
    heading_info: HeadingInfo | None = None
    chapter_number: int | None = None
```

**変更箇所 2**: parse_book2_xml() 関数 (L107-220)

chapter 追跡ロジックを追加:

- `current_chapter_number: int | None = None` 変数を追加
- chapter 要素処理時に `current_chapter_number` を更新
- 全 ContentItem 生成時に `chapter_number=current_chapter_number` を設定

主要変更点:

```python
content_items: list[ContentItem] = []
current_chapter_number: int | None = None

def process_element(elem) -> None:
    nonlocal current_chapter_number

    # Process chapter
    if elem.tag == "chapter":
        number = elem.get("number", "")
        if number:
            try:
                current_chapter_number = int(number)
            except ValueError:
                current_chapter_number = None
        # ... ContentItem 生成時に chapter_number を設定
        content_items.append(ContentItem(
            item_type="heading",
            text=marked_text,
            heading_info=heading_info,
            chapter_number=current_chapter_number
        ))
```

### src/xml2_pipeline.py

**変更箇所 1**: Import 追加 (L13)

```python
import re  # ファイル名サニタイズ用
```

**変更箇所 2**: sanitize_filename() 関数 (L122-150)

新規関数を実装:

```python
def sanitize_filename(number: int, title: str) -> str:
    """Sanitize chapter title for use in filename.

    Args:
        number: Chapter number (1, 2, 3, ...)
        title: Chapter title

    Returns:
        Sanitized filename in format "ch{NN}_{title}" where:
        - NN is zero-padded 2-digit chapter number
        - title contains only ASCII alphanumeric and underscores
        - spaces are converted to underscores
        - title is limited to 20 characters
        - empty titles become "untitled"
    """
    prefix = f"ch{number:02d}"
    sanitized_title = re.sub(r'[^a-zA-Z0-9_]', '', title.replace(' ', '_'))
    sanitized_title = sanitized_title[:20]
    if not sanitized_title:
        sanitized_title = "untitled"
    return f"{prefix}_{sanitized_title}"
```

**変更箇所 3**: process_chapters() 関数 (L181-351)

新規関数を実装:

- content_items を chapter_number でグループ化
- chapter がある場合: chapters/ に chapter 毎の WAV を出力、全 chapter を結合して book.wav を生成
- chapter がない場合: book.wav のみ生成（従来の process_content() と同等）

主要ロジック:

```python
# Group by chapter_number
chapters_dict: dict[int | None, list[ContentItem]] = {}
for item in content_items:
    chapter_num = item.chapter_number
    if chapter_num not in chapters_dict:
        chapters_dict[chapter_num] = []
    chapters_dict[chapter_num].append(item)

has_chapters = any(k is not None for k in chapters_dict.keys())

if has_chapters:
    chapters_dir = output_dir / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    for chapter_num in sorted([k for k in chapters_dict.keys() if k is not None]):
        # Generate chapter WAV
        # Save to chapters/ch{NN}_{title}.wav

    # Concatenate all chapters into book.wav
    concatenate_audio_files(chapter_wav_files, book_path)
else:
    # No chapters, generate book.wav only
```

**変更箇所 4**: main() 関数 (L468)

`process_content()` を `process_chapters()` に変更:

```python
# Process content and generate audio
process_chapters(
    content_items,
    synthesizer,
    output_dir,
    parsed,
    chapter_sound=chapter_sound,
    section_sound=section_sound,
)
```

## テスト結果

```
PYTHONPATH=/data/projects/text-reading-with-llm .venv/bin/python -m pytest tests/ -v
============================= 443 passed in 0.83s ==============================
```

### Phase 3 固有テスト (30件)

**xml2_parser.py 関連 (11テスト)**:
```
tests/test_xml2_parser.py::TestContentItemHasChapterNumber::test_content_item_has_chapter_number_attribute PASSED
tests/test_xml2_parser.py::TestContentItemHasChapterNumber::test_content_item_chapter_number_default_is_none PASSED
tests/test_xml2_parser.py::TestContentItemHasChapterNumber::test_content_item_chapter_number_accepts_int PASSED
tests/test_xml2_parser.py::TestContentItemHasChapterNumber::test_content_item_chapter_number_accepts_larger_int PASSED
tests/test_xml2_parser.py::TestContentItemHasChapterNumber::test_content_item_backward_compatible_without_chapter_number PASSED
tests/test_xml2_parser.py::TestParseBook2XmlAssignsChapterNumbers::test_chapter_1_items_have_chapter_number_1 PASSED
tests/test_xml2_parser.py::TestParseBook2XmlAssignsChapterNumbers::test_chapter_2_items_have_chapter_number_2 PASSED
tests/test_xml2_parser.py::TestParseBook2XmlAssignsChapterNumbers::test_chapter_3_items_have_chapter_number_3 PASSED
tests/test_xml2_parser.py::TestParseBook2XmlAssignsChapterNumbers::test_section_inherits_parent_chapter_number PASSED
tests/test_xml2_parser.py::TestParseBook2XmlAssignsChapterNumbers::test_no_chapter_xml_has_none_chapter_number PASSED
tests/test_xml2_parser.py::TestParseBook2XmlAssignsChapterNumbers::test_chapter_heading_itself_has_chapter_number PASSED
```

**xml2_pipeline.py 関連 (19テスト)**:
```
tests/test_xml2_pipeline.py::TestSanitizeFilename::test_sanitize_filename_function_exists PASSED
tests/test_xml2_pipeline.py::TestSanitizeFilename::test_sanitize_filename_english_title PASSED
tests/test_xml2_pipeline.py::TestSanitizeFilename::test_sanitize_filename_japanese_title PASSED
tests/test_xml2_pipeline.py::TestSanitizeFilename::test_sanitize_filename_mixed_title PASSED
tests/test_xml2_pipeline.py::TestSanitizeFilename::test_sanitize_filename_empty_title PASSED
tests/test_xml2_pipeline.py::TestSanitizeFilename::test_sanitize_filename_special_characters PASSED
tests/test_xml2_pipeline.py::TestSanitizeFilename::test_sanitize_filename_number_zero_padded PASSED
tests/test_xml2_pipeline.py::TestSanitizeFilename::test_sanitize_filename_large_chapter_number PASSED
tests/test_xml2_pipeline.py::TestSanitizeFilename::test_sanitize_filename_max_length PASSED
tests/test_xml2_pipeline.py::TestSanitizeFilename::test_sanitize_filename_spaces_to_underscores PASSED
tests/test_xml2_pipeline.py::TestProcessChaptersCreatesChapterFiles::test_process_chapters_function_exists PASSED
tests/test_xml2_pipeline.py::TestProcessChaptersCreatesChapterFiles::test_process_chapters_creates_chapters_directory PASSED
tests/test_xml2_pipeline.py::TestProcessChaptersCreatesChapterFiles::test_process_chapters_creates_chapter_wav_files PASSED
tests/test_xml2_pipeline.py::TestProcessChaptersCreatesChapterFiles::test_process_chapters_filename_format PASSED
tests/test_xml2_pipeline.py::TestProcessChaptersCreatesChapterFiles::test_process_chapters_three_chapters PASSED
tests/test_xml2_pipeline.py::TestProcessChaptersCreatesBookWav::test_process_chapters_creates_book_wav PASSED
tests/test_xml2_pipeline.py::TestProcessChaptersCreatesBookWav::test_process_chapters_book_wav_and_chapter_files_coexist PASSED
tests/test_xml2_pipeline.py::TestProcessContentWithoutChaptersCreatesBookWav::test_no_chapters_creates_only_book_wav PASSED
tests/test_xml2_pipeline.py::TestProcessContentWithoutChaptersCreatesBookWav::test_mixed_none_and_numbered_chapters PASSED
```

**全テスト**: 443 passed (既存 413 + 新規 30)
**リグレッション**: なし（既存 413 テストすべて PASS）

## 発見した問題/課題

### 1. process_content() 関数の重複

**問題**: process_chapters() 実装により、process_content() 関数が実質的に未使用となった。

**解決**: 既存の process_content() 関数は後方互換性のために残した。Phase 5 (Polish) でドキュメント整理時に対応を検討。

### 2. chapter_number が None のアイテムの扱い

**確認事項**:
- ✅ chapter_number=None のアイテムのみの場合は book.wav のみ生成（テスト: test_no_chapters_creates_only_book_wav）
- ✅ chapter_number=None と数値が混在する場合、数値の chapter のみを chapters/ に出力（テスト: test_mixed_none_and_numbered_chapters）

**設計判断**: mixed ケースでは None アイテムは book.wav には含まれるが、個別の chapter ファイルには含まれない。これは仕様通り。

### 3. chapter タイトル取得ロジック

**実装**: chapter 内の最初の level=1 heading の title を使用。

```python
chapter_title = "untitled"
for item in items:
    if item.item_type == "heading" and item.heading_info and item.heading_info.level == 1:
        chapter_title = item.heading_info.title
        break
```

**妥当性**: book2.xml では chapter 要素が level=1 heading として処理されるため、確実にタイトルを取得できる。

## 次フェーズへの引き継ぎ

### Phase 4 (US3: cleaned_text.txt の品質向上)

**前提条件**:
- ✅ clean_page_text() が process_chapters() で動作することを確認済み（Phase 2 の機能を継承）
- ✅ chapter_number が ContentItem に設定されていることを確認済み

**実装するもの**:
1. main() の cleaned_text.txt 出力部分（L273-281）を修正
2. item.text に clean_page_text() を適用してから出力
3. chapter 区切りマーカー（`=== Chapter N: Title ===`）を挿入

**注意点**:
- clean_page_text() 適用は process_chapters() 内で既に行われているが、cleaned_text.txt 出力時にも適用が必要
- マーカー（CHAPTER_MARKER, SECTION_MARKER）は表示用に変換（`[章]`, `[節]`）
- chapter がある場合は chapter 番号とタイトルを含めた区切りを挿入

**Phase 4 で流用可能な実装パターン**:
- process_chapters() の chapter グループ化ロジック（L207-212）
- chapter タイトル取得ロジック（L234-238）
- clean_page_text() 呼び出しパターン（L257）

### Phase 5 (Polish: ドキュメント・型ヒント・クリーンアップ)

**実装するもの**:
- sanitize_filename() の docstring は既に完備
- process_chapters() の docstring は既に完備
- 型ヒントは既に完備
- process_content() 関数の扱いを検討（deprecation notice または削除）

## 実装の品質確認

### 後方互換性
- ✅ ContentItem.chapter_number はオプショナル（デフォルト None）
- ✅ 既存テスト 413 件すべて PASS（リグレッションなし）
- ✅ chapter がない XML でも動作（book.wav のみ生成）

### エッジケース対応
- ✅ 空タイトル → "untitled"
- ✅ 日本語タイトル → ASCII のみ抽出（空なら "untitled"）
- ✅ 特殊文字 → 除去
- ✅ 長いタイトル → 20文字に制限
- ✅ スペース → アンダースコアに変換
- ✅ 2桁以上の章番号 → ゼロ埋めなし（`ch100_`）

### 実装の完全性
- ✅ TDD フロー完遂（RED → GREEN → 検証）
- ✅ 全テスト PASS（443/443）
- ✅ 実装とテストの対応関係明確
- ✅ ドキュメント完備（docstrings, 型ヒント）

## Checkpoint 確認

**US1 AND US2 が両方独立して動作すること**:
- ✅ US1 (clean_page_text 適用): Phase 2 で実装済み、Phase 3 でも維持
- ✅ US2 (chapter 分割出力): Phase 3 で実装、全テスト PASS
- ✅ US1 + US2 統合: process_chapters() 内で clean_page_text() を呼び出し、両機能が協調動作
