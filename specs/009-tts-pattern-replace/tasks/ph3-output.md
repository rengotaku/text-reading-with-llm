# Phase 3 Output: US2 - 番号表記の自然な読み上げ

**Date**: 2026-02-22
**Status**: 完了
**User Story**: US2 - 番号表記の自然な読み上げ

## 実行タスク

- [x] T029 Read RED tests: specs/009-tts-pattern-replace/red-tests/ph3-test.md
- [x] T030 [P] [US2] Add NUMBER_PREFIX_PATTERN constant in src/text_cleaner.py
- [x] T031 [P] [US2] Add CHAPTER_PATTERN constant in src/text_cleaner.py
- [x] T032 [US2] Add `_clean_number_prefix()` function in src/text_cleaner.py
- [x] T033 [US2] Add `_clean_chapter()` function in src/text_cleaner.py
- [x] T034 [US2] Integrate new functions into `clean_page_text()` in src/text_cleaner.py
- [x] T035 Verify `make test` PASS (GREEN)
- [x] T036 Verify `make test` passes all tests (US1 回帰含む)
- [x] T037 Generate phase output: specs/009-tts-pattern-replace/tasks/ph3-output.md

## 変更ファイル一覧

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/text_cleaner.py | 修正 | 新規パターン定数追加（L42-48）、新規関数追加（L164-182）、clean_page_text()統合（L218-219） |
| tests/test_number_prefix.py | 既存 | RED Phase で作成済み（13テスト） |
| tests/test_chapter_conversion.py | 既存 | RED Phase で作成済み（12テスト） |
| specs/009-tts-pattern-replace/tasks.md | 修正 | T029-T037 をチェック済みに更新 |

## 実装詳細

### src/text_cleaner.py の変更

#### 新規パターン定数（L42-48）

```python
# Number prefix pattern (US2)
# No.X pattern (case insensitive)
NUMBER_PREFIX_PATTERN = re.compile(r"No\.(\d+)", re.IGNORECASE)

# Chapter pattern (US2)
# Chapter X pattern (case insensitive)
CHAPTER_PATTERN = re.compile(r"Chapter\s+(\d+)", re.IGNORECASE)
```

#### 新規関数（L164-182）

```python
def _clean_number_prefix(text: str) -> str:
    """Replace No.X pattern with ナンバーX for TTS.

    Converts:
    - No.21 → ナンバー21
    - no.5 → ナンバー5 (case insensitive)
    - NO.100 → ナンバー100
    """
    return NUMBER_PREFIX_PATTERN.sub(r"ナンバー\1", text)


def _clean_chapter(text: str) -> str:
    """Replace Chapter X pattern with 第X章 for TTS.

    Converts:
    - Chapter 5 → 第5章
    - chapter 12 → 第12章 (case insensitive)
    - CHAPTER 1 → 第1章

    Note: 第X章 will be further converted to だいXしょう by normalize_numbers()
    """
    return CHAPTER_PATTERN.sub(r"第\1章", text)
```

#### clean_page_text() への統合（L218-219）

```python
# NEW: Text cleaning for TTS (before markdown cleanup)
# Process in specific order to avoid interference
text = _clean_urls(text)  # US1: Remove URLs
text = _clean_isbn(text)  # US4: Remove ISBN
text = _clean_number_prefix(text)  # US2: No.X → ナンバーX
text = _clean_chapter(text)  # US2: Chapter X → 第X章
text = _clean_parenthetical_english(text)  # US5: Remove (English)
text = _normalize_references(text)  # US2/3: 図X.Y → ずXのY
```

**処理順序の根拠**:
- US1（URL）の後に実行: URLと番号パターンは干渉しない
- US4（ISBN）の後に実行: ISBNパターンと番号パターンは干渉しない
- normalize_numbers() の前に実行: `第X章` を `だいXしょう` に変換するため

## テスト結果

### Number prefix tests (13 tests)

```
tests/test_number_prefix.py::TestCleanNumberPrefixBasic::test_clean_number_prefix_basic PASSED
tests/test_number_prefix.py::TestCleanNumberPrefixBasic::test_clean_number_prefix_attached_to_word PASSED
tests/test_number_prefix.py::TestCleanNumberPrefixBasic::test_clean_number_prefix_large_number PASSED
tests/test_number_prefix.py::TestCleanNumberPrefixBasic::test_clean_number_prefix_single_digit PASSED
tests/test_number_prefix.py::TestCleanNumberPrefixCaseInsensitive::test_clean_number_prefix_lowercase PASSED
tests/test_number_prefix.py::TestCleanNumberPrefixCaseInsensitive::test_clean_number_prefix_uppercase PASSED
tests/test_number_prefix.py::TestCleanNumberPrefixCaseInsensitive::test_clean_number_prefix_mixed_case PASSED
tests/test_number_prefix.py::TestCleanNumberPrefixNoNumber::test_clean_number_prefix_no_number_after_dot PASSED
tests/test_number_prefix.py::TestCleanNumberPrefixNoNumber::test_clean_number_prefix_no_followed_by_text PASSED
tests/test_number_prefix.py::TestCleanNumberPrefixMultiple::test_clean_number_prefix_multiple PASSED
tests/test_number_prefix.py::TestCleanNumberPrefixEdgeCases::test_clean_number_prefix_empty_string PASSED
tests/test_number_prefix.py::TestCleanNumberPrefixEdgeCases::test_clean_number_prefix_no_match PASSED
tests/test_number_prefix.py::TestCleanNumberPrefixEdgeCases::test_clean_number_prefix_idempotent PASSED

13 passed in 0.03s
```

### Chapter conversion tests (12 tests)

```
tests/test_chapter_conversion.py::TestCleanChapterBasic::test_clean_chapter_basic PASSED
tests/test_chapter_conversion.py::TestCleanChapterBasic::test_clean_chapter_double_digit PASSED
tests/test_chapter_conversion.py::TestCleanChapterBasic::test_clean_chapter_single_digit PASSED
tests/test_chapter_conversion.py::TestCleanChapterBasic::test_clean_chapter_large_number PASSED
tests/test_chapter_conversion.py::TestCleanChapterCaseInsensitive::test_clean_chapter_lowercase PASSED
tests/test_chapter_conversion.py::TestCleanChapterCaseInsensitive::test_clean_chapter_uppercase PASSED
tests/test_chapter_conversion.py::TestCleanChapterCaseInsensitive::test_clean_chapter_mixed_case PASSED
tests/test_chapter_conversion.py::TestCleanChapterMultiple::test_clean_chapter_multiple PASSED
tests/test_chapter_conversion.py::TestCleanChapterEdgeCases::test_clean_chapter_empty_string PASSED
tests/test_chapter_conversion.py::TestCleanChapterEdgeCases::test_clean_chapter_no_match PASSED
tests/test_chapter_conversion.py::TestCleanChapterEdgeCases::test_clean_chapter_without_number PASSED
tests/test_chapter_conversion.py::TestCleanChapterEdgeCases::test_clean_chapter_idempotent PASSED

12 passed in 0.03s
```

### Core TTS cleaning regression tests (65 tests - 回帰なし)

```
tests/test_number_prefix.py ............. [ 20%]
tests/test_chapter_conversion.py ............ [ 38%]
tests/test_url_cleaning.py ...................... [ 72%]
tests/test_isbn_cleaning.py .................. [100%]

65 passed in 0.05s
```

**カバレッジ**: 測定なし（Phase 5 で実施予定）

## GREEN Phase 検証完了

- すべての RED テストが PASS に変更された（24 FAIL → 25 PASS）
- 既存テストに回帰なし（US1 の 22 tests すべて PASS）
- 実装は最小限で、過剰実装なし
- 処理順序が正しく統合されている

## 発見した問題/課題

特になし。すべてのテストが期待通りにPASSし、回帰も発生していない。

## 次フェーズへの引き継ぎ

Phase 4 (US3: ISBN・書籍メタ情報の適切な処理) で実装するもの:
- ISBN削除後の括弧・ラベル削除（`（ISBN: 978-...）` → 括弧ごと削除）
- ISBN削除後の空白正規化
- 新規パターン定数: `ISBN_WITH_CONTEXT_PATTERN`（括弧・ラベル対応）
- `_clean_isbn()` 関数の拡張
- 空白正規化処理追加

注意点:
- US2 の番号パターン処理は完全に独立しており、US3 と干渉しない
- 処理順序: `_clean_urls()` → `_clean_isbn()` → `_clean_number_prefix()` → `_clean_chapter()` → 以降は US3 で拡張予定
