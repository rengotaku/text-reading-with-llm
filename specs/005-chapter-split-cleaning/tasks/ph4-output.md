# Phase 4 Output: cleaned_text.txt の品質向上

**Date**: 2026-02-18
**Status**: 完了
**User Story**: US3 - cleaned_text.txt の品質向上

## 実行タスク

- [x] T043 Read RED tests: specs/005-chapter-split-cleaning/red-tests/ph4-test.md
- [x] T044 [US3] Update main() to write cleaned text to cleaned_text.txt in src/xml2_pipeline.py
- [x] T045 Verify `make test` PASS (GREEN)
- [x] T046 Verify `make test` passes all tests (including US1, US2 regressions)

## 変更ファイル一覧

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/xml2_pipeline.py | 修正 | main() 関数の cleaned_text.txt 出力部分（L468-478）を変更し、clean_page_text() 適用 + 章区切りフォーマット変更 |

## 実装内容

### src/xml2_pipeline.py

**変更箇所**: main() 関数の cleaned_text.txt 出力部分 (L468-499)

**変更前**:
```python
# Save cleaned text
cleaned_text_path = output_dir / "cleaned_text.txt"
with open(cleaned_text_path, "w", encoding="utf-8") as f:
    for item in content_items:
        f.write(f"=== {item.item_type} ===\n")
        # Remove markers for display
        display_text = item.text.replace(CHAPTER_MARKER, "\n[章] ")
        display_text = display_text.replace(SECTION_MARKER, "\n[節] ")
        f.write(display_text)
        f.write("\n\n")
logger.info("Saved cleaned text: %s", cleaned_text_path)
```

**変更後**:
```python
# Save cleaned text
cleaned_text_path = output_dir / "cleaned_text.txt"
with open(cleaned_text_path, "w", encoding="utf-8") as f:
    current_chapter = None

    for item in content_items:
        # Insert chapter separator when chapter changes
        if item.chapter_number is not None and item.chapter_number != current_chapter:
            current_chapter = item.chapter_number

            # Find chapter title from heading info
            chapter_title = "Untitled"
            if item.item_type == "heading" and item.heading_info and item.heading_info.level == 1:
                chapter_title = item.heading_info.title

            f.write(f"=== Chapter {current_chapter}: {chapter_title} ===\n\n")

        # Remove markers before cleaning
        text = item.text
        if text.startswith(CHAPTER_MARKER):
            text = text[len(CHAPTER_MARKER):]
        elif text.startswith(SECTION_MARKER):
            text = text[len(SECTION_MARKER):]

        # Apply clean_page_text to remove URLs, parenthetical English, convert numbers, etc.
        cleaned = clean_page_text(text)

        # Skip empty content
        if cleaned.strip():
            f.write(cleaned)
            f.write("\n\n")

logger.info("Saved cleaned text: %s", cleaned_text_path)
```

**主要な変更点**:
1. **章区切り追加**: chapter_number が変わるタイミングで `=== Chapter N: Title ===` を挿入
2. **clean_page_text() 適用**: マーカー除去後、各 item.text に clean_page_text() を適用
3. **マーカー除去**: CHAPTER_MARKER / SECTION_MARKER を clean_page_text() 適用前に除去
4. **フォーマット変更**: `=== {item_type} ===` ラベルを廃止し、章区切りのみを出力
5. **空コンテンツスキップ**: クリーニング後に空になったテキストは出力しない

## テスト結果

```
PYTHONPATH=/data/projects/text-reading-with-llm .venv/bin/python -m pytest tests/ -q
........................................................................ [ 15%]
........................................................................ [ 31%]
........................................................................ [ 47%]
........................................................................ [ 63%]
........................................................................ [ 79%]
........................................................................ [ 95%]
...................                                                      [100%]
451 passed in 1.27s
```

### Phase 4 固有テスト (8件)

**xml2_pipeline.py 関連 (8テスト)**:
```
tests/test_xml2_pipeline.py::TestCleanedTextFileContainsCleanedContent::test_cleaned_text_does_not_contain_url PASSED
tests/test_xml2_pipeline.py::TestCleanedTextFileContainsCleanedContent::test_cleaned_text_does_not_contain_parenthetical_english PASSED
tests/test_xml2_pipeline.py::TestCleanedTextFileContainsCleanedContent::test_cleaned_text_numbers_converted_to_kana PASSED
tests/test_xml2_pipeline.py::TestCleanedTextFileContainsCleanedContent::test_cleaned_text_isbn_removed PASSED
tests/test_xml2_pipeline.py::TestCleanedTextFileHasChapterMarkers::test_cleaned_text_has_chapter_separator_format PASSED
tests/test_xml2_pipeline.py::TestCleanedTextFileHasChapterMarkers::test_cleaned_text_chapter_separator_contains_title PASSED
tests/test_xml2_pipeline.py::TestCleanedTextFileHasChapterMarkers::test_cleaned_text_paragraph_text_is_cleaned PASSED
tests/test_xml2_pipeline.py::TestCleanedTextFileHasChapterMarkers::test_cleaned_text_no_item_type_labels PASSED
```

**全テスト**: 451 passed (既存 443 + 新規 8)
**リグレッション**: なし（既存 443 テストすべて PASS）

## 発見した問題/課題

### 1. clean_page_text() の二重適用

**確認事項**:
- process_chapters() 内で clean_page_text() が既に適用されている（US1の実装）
- cleaned_text.txt 出力時に再度 clean_page_text() を適用している
- これは意図通りの動作（音声生成とテキスト出力は独立した処理）

**理由**:
- 音声生成: process_chapters() で clean_page_text() を適用してから TTS 生成
- テキスト出力: content_items は元のテキストを保持しているため、再度適用が必要

### 2. chapter タイトル取得ロジック

**実装**:
chapter_number が変わるタイミングで、その ContentItem が level=1 heading なら title を取得:

```python
chapter_title = "Untitled"
if item.item_type == "heading" and item.heading_info and item.heading_info.level == 1:
    chapter_title = item.heading_info.title
```

**妥当性**: book2.xml では chapter 要素が最初に level=1 heading として処理されるため、確実にタイトルを取得できる。

### 3. マーカー処理の一貫性

**確認事項**:
- process_chapters() でのマーカー処理: マーカー除去後に効果音挿入、その後 clean_page_text() 適用
- cleaned_text.txt でのマーカー処理: マーカー除去後に clean_page_text() 適用

**一貫性**: 両方とも同じパターン（マーカー除去 → クリーニング）で実装されており、一貫性が保たれている。

## 次フェーズへの引き継ぎ

### Phase 5 (Polish: ドキュメント・型ヒント・クリーンアップ)

**前提条件**:
- ✅ US1, US2, US3 すべての実装完了
- ✅ 全テスト PASS (451/451)
- ✅ リグレッションなし

**実装するもの**:
1. docstrings の確認・追加（必要であれば）
2. 型ヒントの確認・追加（必要であれば）
3. quickstart.md の手動検証

**注意点**:
- Phase 4 で新規関数は追加していない（既存の main() 関数のみ修正）
- 既存の docstrings と型ヒントは変更不要
- quickstart.md での動作確認が主要タスク

**Phase 5 で流用可能な実装パターン**:
- cleaned_text.txt の章区切り処理パターン（L471-480）
- clean_page_text() 適用パターン（L490）

## 実装の品質確認

### TDD フロー完遂
- ✅ RED → GREEN → 検証の流れを完遂
- ✅ 全 8 テスト FAIL (RED) → PASS (GREEN)
- ✅ リグレッションなし（既存 443 テストすべて PASS）

### 要件充足
- ✅ FR-005: cleaned_text.txt に clean_page_text() 適用済みテキストを出力
- ✅ URL、括弧内英語、ISBN が除去されている
- ✅ 数値がカナに変換されている
- ✅ 章区切りが `=== Chapter N: Title ===` 形式で出力される
- ✅ `=== {item_type} ===` ラベルが廃止されている

### 実装の完全性
- ✅ マーカー除去が clean_page_text() 適用前に行われている
- ✅ 空コンテンツのスキップ処理
- ✅ 章タイトルのフォールバック処理（"Untitled"）
- ✅ 既存機能への影響なし（process_chapters() との独立性確保）

## Checkpoint 確認

**全 US (1, 2, 3) が動作し、E2E テスト可能であること**:
- ✅ US1 (clean_page_text 適用): Phase 2 で実装済み、Phase 4 でも維持
- ✅ US2 (chapter 分割出力): Phase 3 で実装済み、Phase 4 でも維持
- ✅ US3 (cleaned_text.txt 品質向上): Phase 4 で実装、全テスト PASS
- ✅ 全 User Story が独立して動作・テスト可能
- ✅ E2E テスト: make xml-tts INPUT=sample/book2.xml PARSER=xml2 で実行可能
