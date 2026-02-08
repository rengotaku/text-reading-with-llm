# Phase 6 RED Tests

## サマリー
- Phase: Phase 6 - User Story 6: 不適切な読点挿入の修正
- FAIL テスト数: 6
- テストファイル: tests/test_punctuation_rules.py

## FAIL テスト一覧

| テストファイル | テストクラス | テストメソッド | 期待動作 |
|---------------|-------------|---------------|---------|
| tests/test_punctuation_rules.py | TestNormalizeLineDehaArimasen | test_normalize_line_deha_arimasen_basic | 「これは問題ではありません」→ 「では、ありません」にならない |
| tests/test_punctuation_rules.py | TestNormalizeLineDehaArimasen | test_normalize_line_deha_arimasen_longer | 長いフレーズ後の「ではありません」でも読点なし |
| tests/test_punctuation_rules.py | TestNormalizeLineDehaPatterns | test_normalize_line_deha_nai_in_sentence | 文中の「ではない」でも読点なし |
| tests/test_punctuation_rules.py | TestNormalizeLineMixedPatterns | test_normalize_line_mixed_ha_patterns | 「この本は問題ではありません」→「では、ありません」にならない |
| tests/test_punctuation_rules.py | TestNormalizeLineMixedPatterns | test_normalize_line_mixed_ha_patterns_longer | 長い文での混合パターン |
| tests/test_punctuation_rules.py | TestNormalizeLineMixedPatterns | test_normalize_line_multiple_exclusions | 複数の除外パターンが連続する場合 |

## テストクラス構成

### TestNormalizeLineDehaArimasen (2 tests)
- 「ではありません」パターンで「は」の後に読点が入らないことを検証

### TestNormalizeLineDehaPatterns (4 tests)
- 「ではない」「ではなかった」「ではなくて」パターンの検証

### TestNormalizeLineNihaPatterns (3 tests)
- 「にはならない」「には至らない」パターンの検証

### TestNormalizeLineTohaPatterns (2 tests)
- 「とは言えない」「とは限らない」パターンの検証

### TestNormalizeLineMixedPatterns (4 tests)
- 通常の「は」と除外パターンの混合ケースの検証

### TestNormalizeLineEdgeCases (4 tests)
- エッジケース（文頭、空文字列、など）の検証

### TestNormalizeLineArimasuPatterns (2 tests)
- 「ではありますが」「ではある」パターンの検証

## 実装ヒント

### 対象ファイル
`src/punctuation_normalizer.py`

### 除外パターンリスト (EXCLUSION_SUFFIXES)
以下のパターンが「は」の後に続く場合、読点を挿入しない:

```python
EXCLUSION_SUFFIXES = [
    # では系
    "ありません",
    "ありませんでした",
    "ありますが",
    "ある",
    "ない",
    "なかった",
    "なくて",
    "ないか",
    # には系
    "ならない",
    "ならなかった",
    "至らない",
    # とは系
    "言えない",
    "限らない",
]
```

### 修正方法
Rule 4 の正規表現を修正し、negative lookahead を使用:

```python
# 現在のRule 4 (問題あり)
line = re.sub(
    rf"([^、。！？]{{{ha_prefix_len},}})(は)([^、。！？\s])",
    r"\1\2、\3",
    line
)

# 修正案: negative lookahead で除外パターンをスキップ
exclusion_pattern = "|".join(re.escape(s) for s in EXCLUSION_SUFFIXES)
line = re.sub(
    rf"([^、。！？]{{{ha_prefix_len},}})(は)(?!({exclusion_pattern}))([^、。！？\s])",
    r"\1\2、\4",
    line
)
```

### 注意点
- 「では」「には」「とは」は助詞+助詞の組み合わせで、文法的に一体
- 後続の動詞/形容詞と密接に結びついているため、読点を挿入すると不自然
- 通常の「は」（主題マーカー）の後は引き続き読点挿入 OK

## FAIL 出力例

```
FAILED tests/test_punctuation_rules.py::TestNormalizeLineDehaArimasen::test_normalize_line_deha_arimasen_basic
AssertionError: 「ではありません」の「は」の後に読点を入れてはいけない: got 'これは問題では、ありません', expected 'これは問題ではありません'

FAILED tests/test_punctuation_rules.py::TestNormalizeLineDehaArimasen::test_normalize_line_deha_arimasen_longer
AssertionError: 「ではありません」の途中に読点を入れてはいけない: got 'この技術の導入は終わりでは、ありません'

FAILED tests/test_punctuation_rules.py::TestNormalizeLineDehaPatterns::test_normalize_line_deha_nai_in_sentence
AssertionError: 「ではない」の途中に読点を入れてはいけない: got 'これは単純な問題では、ないと思います'

FAILED tests/test_punctuation_rules.py::TestNormalizeLineMixedPatterns::test_normalize_line_mixed_ha_patterns
AssertionError: 「ではありません」の途中に読点を入れてはいけない: got 'この本は問題では、ありません'

FAILED tests/test_punctuation_rules.py::TestNormalizeLineMixedPatterns::test_normalize_line_mixed_ha_patterns_longer
AssertionError: 「ではありません」の途中に読点を入れてはいけない: got 'この技術は重要ですが問題では、ありません'

FAILED tests/test_punctuation_rules.py::TestNormalizeLineMixedPatterns::test_normalize_line_multiple_exclusions
AssertionError: 「では」の後に読点を入れてはいけない: got 'この方法では問題では、ありません'
```

## テスト実行結果

```
============================= test session starts ==============================
platform linux -- Python 3.13.11, pytest-9.0.2
collected 102 items

tests/test_punctuation_rules.py 6 FAILED, 15 PASSED
========================= 6 failed, 96 passed in 0.09s =========================
```

## 次ステップ

phase-executor が以下を実行:
1. RED tests を読み込む: `specs/001-doc-clean-tts-replace/red-tests/ph6-test.md`
2. `EXCLUSION_SUFFIXES` 定数を追加: `src/punctuation_normalizer.py`
3. `_normalize_line()` の Rule 4 を修正: negative lookahead 追加
4. `make test` で GREEN 確認
5. リグレッションテスト確認
6. Phase 出力生成: `specs/001-doc-clean-tts-replace/tasks/ph6-output.md`
