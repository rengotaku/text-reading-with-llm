# Phase 5 RED Tests

## サマリー
- Phase: Phase 5 - 括弧付き用語の重複読み防止 (US5)
- FAIL テスト数: 24
- テストファイル: tests/test_parenthetical_cleaning.py

## FAIL テスト一覧

| テストファイル | テストクラス | テストメソッド | 期待動作 |
|---------------|-------------|---------------|---------|
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalFullWidth | test_clean_parenthetical_english_full_width_basic | 全角括弧内の英語を削除 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalFullWidth | test_clean_parenthetical_english_full_width_multi_word | 複数単語の英語を削除 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalFullWidth | test_clean_parenthetical_english_full_width_with_space | 括弧前後にスペースがある場合 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalHalfWidth | test_clean_parenthetical_english_half_width_basic | 半角括弧内の英語を削除 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalHalfWidth | test_clean_parenthetical_english_half_width_multi_word | 半角括弧内の複数単語英語を削除 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalHalfWidth | test_clean_parenthetical_english_half_width_with_hyphen | ハイフン付き英語を削除 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalPreserve | test_clean_parenthetical_preserve_japanese | 括弧内が日本語の場合は保持 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalPreserve | test_clean_parenthetical_preserve_hiragana | ひらがなのみの括弧内容は保持 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalPreserve | test_clean_parenthetical_preserve_katakana | カタカナのみの括弧内容は保持 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalPreserve | test_clean_parenthetical_preserve_mixed_japanese_english | 日本語と英語が混在する場合は保持 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalAlphabetTerm | test_clean_parenthetical_alphabet_term_basic | アルファベット用語後の括弧付き英語を削除 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalAlphabetTerm | test_clean_parenthetical_alphabet_term_lowercase | 小文字アルファベット用語の処理 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalAlphabetTerm | test_clean_parenthetical_alphabet_with_numbers | 数字を含むアルファベット用語 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalEdgeCases | test_clean_parenthetical_mixed_content | 英語括弧のみ削除、日本語括弧は保持 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalEdgeCases | test_clean_parenthetical_numbers_with_japanese | 数字+日本語の括弧内容は保持 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalEdgeCases | test_clean_parenthetical_multiple_english | 複数の英語括弧を削除 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalEdgeCases | test_clean_parenthetical_empty_parens | 空括弧は保持 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalEdgeCases | test_clean_parenthetical_empty_half_width_parens | 半角空括弧は保持 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalEdgeCases | test_clean_parenthetical_numbers_only | 数字のみの括弧内容は保持 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalEdgeCases | test_clean_parenthetical_punctuation_in_english | 英語内のピリオド・カンマを含む |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalIdempotent | test_clean_parenthetical_idempotent_no_parens | 括弧のないテキストは変化しない |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalIdempotent | test_clean_parenthetical_idempotent_already_processed | 処理済みテキストの再処理で変化しない |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalIdempotent | test_clean_parenthetical_empty_string | 空文字列の処理 |
| tests/test_parenthetical_cleaning.py | TestCleanParentheticalIdempotent | test_clean_parenthetical_whitespace_only | 空白のみのテキスト |

## 実装ヒント

### 必要な関数

`src/text_cleaner.py` に以下を実装:

```python
def _clean_parenthetical_english(text: str) -> str:
    """Remove English terms in parentheses for TTS.

    Removes parenthetical content when it contains ONLY:
    - English alphabets (A-Z, a-z)
    - Numbers (0-9)
    - Spaces
    - Hyphens
    - Periods/commas (e.g., "e.g.,")

    Preserves parenthetical content when it contains:
    - Japanese characters (hiragana, katakana, kanji)
    - Empty content
    """
```

### パターン定義

```python
# Parenthetical patterns (US5)
# Match (content) or （content） where content is English-only
PARENTHETICAL_ENGLISH_PATTERN = re.compile(
    r'[（(]'           # Opening paren (full or half width)
    r'([A-Za-z0-9\s\-.,]+)'  # English content only
    r'[）)]'           # Closing paren (full or half width)
)
```

### 判定ロジック

括弧内が「英語のみ」かどうかを判定:
- 日本語文字（ひらがな、カタカナ、漢字）を含む → 保持
- 英字、数字、スペース、ハイフン、ピリオド/カンマのみ → 削除
- 空 → 保持

### 注意点

- 全角括弧（）と半角括弧()の両方に対応
- 日本語が1文字でも含まれていれば保持
- 複数の括弧を順次処理
- 冪等性を保証（処理済みテキストを再処理しても変化しない）

## FAIL 出力例

```
============================= test session starts ==============================
platform linux -- Python 3.13.11, pytest-9.0.2, pluggy-1.6.0
collected 57 items / 1 error

==================================== ERRORS ====================================
____________ ERROR collecting tests/test_parenthetical_cleaning.py _____________
ImportError while importing test module '/data/projects/text-reading-with-llm/tests/test_parenthetical_cleaning.py'.
tests/test_parenthetical_cleaning.py:9: in <module>
    from src.text_cleaner import _clean_parenthetical_english
E   ImportError: cannot import name '_clean_parenthetical_english' from 'src.text_cleaner'
=========================== short test summary info ============================
ERROR tests/test_parenthetical_cleaning.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.09s ===============================
```

## テストケースの分類

### 必須テスト（タスク指定）
1. `TestCleanParentheticalFullWidth` - 全角括弧+英語削除
2. `TestCleanParentheticalHalfWidth` - 半角括弧+英語削除
3. `TestCleanParentheticalPreserve` - 日本語括弧保持
4. `TestCleanParentheticalAlphabetTerm` - アルファベット用語処理

### 追加エッジケース
5. `TestCleanParentheticalEdgeCases` - 混在、空括弧、数字のみ
6. `TestCleanParentheticalIdempotent` - 冪等性確認
