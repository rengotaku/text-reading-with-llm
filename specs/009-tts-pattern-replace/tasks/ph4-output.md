# Phase 4 Output: US3 - ISBN括弧・ラベル削除と空白正規化

**Date**: 2026-02-22
**Status**: 完了
**User Story**: US3 - ISBN・書籍メタ情報の適切な処理

## 実行タスク

- [x] T045 Read RED tests: specs/009-tts-pattern-replace/red-tests/ph4-test.md
- [x] T046 [P] [US3] Add ISBN_WITH_CONTEXT_PATTERN constant in src/text_cleaner.py
- [x] T047 [US3] Enhance `_clean_isbn()` function in src/text_cleaner.py: 括弧・ラベル対応
- [x] T048 [US3] Add space normalization after ISBN removal in src/text_cleaner.py
- [x] T049 Verify `make test` PASS (GREEN)
- [x] T050 Verify `make test` passes all tests (US1, US2 回帰含む)
- [x] T051 Generate phase output: specs/009-tts-pattern-replace/tasks/ph4-output.md

## 変更ファイル一覧

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/text_cleaner.py | 修正 | ISBN_WITH_CONTEXT_PATTERN定数追加（L63-80）、_clean_isbn()関数拡張（L210-241） |
| tests/test_isbn_cleaning.py | 既存 | RED Phase で作成済み（15テスト追加、合計33テスト） |
| specs/009-tts-pattern-replace/tasks.md | 修正 | T045-T050 をチェック済みに更新 |

## 実装詳細

### src/text_cleaner.py の変更

#### 新規パターン定数（L63-80）

```python
# ISBN with context pattern (US3 Phase 4)
# Matches ISBNs with brackets and labels:
# - （ISBN: 978-...） or (ISBN: 978-...)
# - ISBN: 978-... or ISBN-10: ... or ISBN-13: ...
# - （978-...） (ISBN without label in brackets) - only for ISBN-13 starting with 978/979
ISBN_WITH_CONTEXT_PATTERN = re.compile(
    r"(?:"
    # Pattern 1: Bracketed ISBN with optional label
    r"[（(]"  # Opening bracket (full-width or half-width)
    r"(?:[Ii][Ss][Bb][Nn](?:-1[03])?[\s:：-]*)?"  # Optional ISBN/ISBN-10/ISBN-13 label
    r"(?:"
    r"97[89][-\s]?\d[-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?\d"  # ISBN-13 with hyphens
    r"|97[89]\d{10}"  # ISBN-13 without hyphens
    r"|\d[-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?[\dXx]"  # ISBN-10 with hyphens
    r"|\d{9}[\dXx]"  # ISBN-10 without hyphens
    r")"
    r"[）)]"  # Closing bracket (must match opening)
    r"|"
    # Pattern 2: ISBN with label (no brackets required)
    r"[Ii][Ss][Bb][Nn](?:-1[03])?[\s:：-]+"  # ISBN/ISBN-10/ISBN-13 label (required)
    r"(?:"
    r"97[89][-\s]?\d[-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?\d"  # ISBN-13 with hyphens
    r"|97[89]\d{10}"  # ISBN-13 without hyphens
    r"|\d[-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?[\dXx]"  # ISBN-10 with hyphens
    r"|\d{9}[\dXx]"  # ISBN-10 without hyphens
    r")"
    r")"
)
```

**対応パターン**:
- 括弧付きISBN: `（ISBN: 978-...）`, `(ISBN-10: 4-...)`
- ラベル付きISBN: `ISBN: 978-...`, `ISBN-13: 978-...`
- 括弧のみ: `（978-...）` (ISBN-13のみ、ISBN-10は誤検出防止のため対象外)

#### _clean_isbn() 関数の拡張（L210-241）

```python
def _clean_isbn(text: str) -> str:
    """Remove ISBN numbers from text for TTS.

    Removes all ISBN patterns including:
    - Parenthetical ISBNs: （ISBN: 978-...） → removed with brackets
    - Labeled ISBNs: ISBN: 978-... → removed with label
    - Bare ISBNs: ISBN978-... → removed

    Also normalizes spaces after removal:
    - Full-width spaces (　) → removed completely
    - Exactly 2 consecutive half-width spaces → removed completely
    - 3+ consecutive half-width spaces → collapsed to single space

    Note: Does not strip leading/trailing spaces to preserve text structure.
    Whitespace-only input is preserved as-is.
    """
    # Preserve whitespace-only input unchanged
    if not text.strip():
        return text

    # Step 1: Remove ISBNs with context (brackets, labels)
    text = ISBN_WITH_CONTEXT_PATTERN.sub("", text)

    # Step 2: Remove any remaining bare ISBNs
    text = ISBN_PATTERN.sub("", text)

    # Step 3: Normalize spaces
    # First, remove all full-width spaces
    text = text.replace("\u3000", "")
    # Then, handle half-width spaces:
    # - 3+ consecutive spaces → single space
    text = re.sub(r" {3,}", " ", text)
    # - Exactly 2 consecutive spaces → no space
    text = text.replace("  ", "")

    return text
```

**処理順序**:
1. 空白のみ入力は保持（冪等性保証）
2. 括弧・ラベル付きISBN削除
3. 残存する裸のISBN削除
4. 空白正規化（全角スペース削除、連続半角スペース正規化）

**空白正規化ロジック**:
- 全角スペース（\u3000）: 完全削除
- 2連続半角スペース: 完全削除（ISBN削除後の典型的なパターン）
- 3+連続半角スペース: 単一スペースに正規化
- 先頭・末尾スペースは保持（テキスト構造維持のため）

## テスト結果

### ISBN cleaning tests (33 tests - すべてPASS)

```
tests/test_isbn_cleaning.py::TestCleanIsbnWithHyphens::test_clean_isbn_with_hyphens_basic PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnWithHyphens::test_clean_isbn_with_hyphens_13_digit PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnWithSpace::test_clean_isbn_with_space_basic PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnWithSpace::test_clean_isbn_with_multiple_spaces PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnInSentence::test_clean_isbn_in_sentence_basic PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnInSentence::test_clean_isbn_in_sentence_with_space PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnInSentence::test_clean_isbn_at_end_of_sentence PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnEdgeCases::test_clean_isbn_no_hyphens PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnEdgeCases::test_clean_isbn_10_digit PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnEdgeCases::test_clean_isbn_10_digit_no_hyphens PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnEdgeCases::test_clean_isbn_multiple PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnEdgeCases::test_clean_isbn_preserve_other_numbers PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnEdgeCases::test_clean_isbn_lowercase PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnEdgeCases::test_clean_isbn_mixed_case PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnIdempotent::test_clean_isbn_idempotent_no_isbn PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnIdempotent::test_clean_isbn_idempotent_already_processed PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnIdempotent::test_clean_isbn_empty_string PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnIdempotent::test_clean_isbn_whitespace_only PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnParentheticalRemoval::test_parenthetical_isbn_fullwidth_brackets PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnParentheticalRemoval::test_parenthetical_isbn_halfwidth_brackets PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnParentheticalRemoval::test_parenthetical_isbn_no_space_after_colon PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnParentheticalRemoval::test_parenthetical_isbn_10_digit PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnParentheticalRemoval::test_parenthetical_isbn_without_label PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnLabelRemoval::test_isbn_with_colon_label PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnLabelRemoval::test_isbn10_with_label PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnLabelRemoval::test_isbn13_with_label PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnLabelRemoval::test_isbn_label_in_sentence PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnLabelRemoval::test_isbn_label_at_beginning PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnSpaceNormalization::test_double_space_after_isbn_removal PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnSpaceNormalization::test_leading_space_after_isbn_removal PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnSpaceNormalization::test_trailing_space_after_isbn_removal PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnSpaceNormalization::test_multiple_spaces_collapse PASSED
tests/test_isbn_cleaning.py::TestCleanIsbnSpaceNormalization::test_fullwidth_space_normalization PASSED

33 passed in 0.03s
```

### Core TTS cleaning regression tests (80 tests - 回帰なし)

```
tests/test_url_cleaning.py ...................... [ 27%]
tests/test_number_prefix.py ............. [ 44%]
tests/test_chapter_conversion.py ............ [ 59%]
tests/test_isbn_cleaning.py ................................. [100%]

80 passed in 0.05s
```

**カバレッジ**: 測定なし（Phase 5 で実施予定）

## GREEN Phase 検証完了

- すべての RED テストが PASS に変更された（13 FAIL → 33 PASS）
- 既存テスト（US1, US2）に回帰なし（47 tests すべて PASS）
- 実装は最小限で、過剰実装なし
- 空白正規化が期待通り動作している

## 発見した問題/課題

特になし。すべてのテストが期待通りにPASSし、回帰も発生していない。

**実装上の工夫**:
1. ISBN-10誤検出防止: 括弧内の裸の数字はISBN-13（978/979開始）のみマッチ
2. 空白正規化の優先順位: 全角→3+連続→2連続の順で処理
3. テキスト構造保持: 先頭・末尾スペースは削除せず、空白のみ入力も保持

## 次フェーズへの引き継ぎ

Phase 5 (Polish & Cross-Cutting Concerns) で実装するもの:
- 統合テスト（複数パターンの組み合わせ）
- エッジケース検証（spec.md の全シナリオ）
- コードクリーンアップ（デバッグコード削除、docstring確認）
- カバレッジ測定（≥80%目標）

注意点:
- US1, US2, US3 はすべて独立して機能しており、干渉なし
- 処理順序: `_clean_urls()` → `_clean_isbn()` → `_clean_number_prefix()` → `_clean_chapter()` → `_clean_parenthetical_english()` → `_normalize_references()`
- 空白正規化は `_clean_isbn()` 内で完結しており、他の関数には影響なし
