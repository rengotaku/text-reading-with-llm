# Phase 7 RED Tests

## サマリー
- Phase: Phase 7 - User Story 7: コロン記号の自然な読み上げ変換
- FAIL テスト数: 17
- テストファイル: tests/test_punctuation_rules.py

## FAIL テスト一覧

| テストファイル | テストメソッド | 期待動作 |
|---------------|---------------|---------|
| tests/test_punctuation_rules.py | TestNormalizeColonsFullWidth::test_normalize_colons_full_width_basic | 全角コロンが「は、」に変換される |
| tests/test_punctuation_rules.py | TestNormalizeColonsFullWidth::test_normalize_colons_full_width_multiple | 複数の全角コロンが変換される |
| tests/test_punctuation_rules.py | TestNormalizeColonsFullWidth::test_normalize_colons_full_width_at_end | 文末の全角コロンが変換される |
| tests/test_punctuation_rules.py | TestNormalizeColonsHalfWidth::test_normalize_colons_half_width_basic | 半角コロンが「は、」に変換される |
| tests/test_punctuation_rules.py | TestNormalizeColonsHalfWidth::test_normalize_colons_half_width_with_space | 半角コロン+スペースが適切に処理される |
| tests/test_punctuation_rules.py | TestNormalizeColonsExclusions::test_normalize_colons_exclude_time_pattern | 時刻パターン(10:30)は変換しない |
| tests/test_punctuation_rules.py | TestNormalizeColonsExclusions::test_normalize_colons_exclude_time_with_seconds | 秒を含む時刻(10:30:45)は変換しない |
| tests/test_punctuation_rules.py | TestNormalizeColonsExclusions::test_normalize_colons_exclude_ratio_pattern | 比率パターン(1:3)は変換しない |
| tests/test_punctuation_rules.py | TestNormalizeColonsExclusions::test_normalize_colons_exclude_ratio_multiple | 複合比率(1:2:3)は変換しない |
| tests/test_punctuation_rules.py | TestNormalizeColonsMixedPatterns::test_normalize_colons_mixed_time_and_heading | 見出しコロン変換+時刻保持の混合 |
| tests/test_punctuation_rules.py | TestNormalizeColonsMixedPatterns::test_normalize_colons_mixed_ratio_and_heading | 見出しコロン変換+比率保持の混合 |
| tests/test_punctuation_rules.py | TestNormalizeColonsMixedPatterns::test_normalize_colons_full_and_half_width_mixed | 全角・半角コロン混在パターン |
| tests/test_punctuation_rules.py | TestNormalizeColonsEdgeCases::test_normalize_colons_empty_string | 空文字列の処理 |
| tests/test_punctuation_rules.py | TestNormalizeColonsEdgeCases::test_normalize_colons_no_colons | コロンを含まないテキスト |
| tests/test_punctuation_rules.py | TestNormalizeColonsEdgeCases::test_normalize_colons_consecutive | 連続コロン(::)の処理 |
| tests/test_punctuation_rules.py | TestNormalizeColonsEdgeCases::test_normalize_colons_at_line_start | 行頭のコロン |
| tests/test_punctuation_rules.py | TestNormalizeColonsEdgeCases::test_normalize_colons_url_colon_not_affected | URL内コロン(https:)の処理 |

## テストカテゴリ

### 1. TestNormalizeColonsFullWidth (3 tests)
全角コロン（：）の「は、」への変換をテスト

### 2. TestNormalizeColonsHalfWidth (2 tests)
半角コロン（:）の「は、」への変換をテスト

### 3. TestNormalizeColonsExclusions (4 tests)
変換対象外パターン（時刻・比率）のテスト

### 4. TestNormalizeColonsMixedPatterns (3 tests)
変換対象と除外パターンが混在するケースのテスト

### 5. TestNormalizeColonsEdgeCases (5 tests)
空文字列、コロンなし、連続コロン等のエッジケース

## 実装ヒント

### 関数シグネチャ
```python
def _normalize_colons(text: str) -> str:
    """Convert colons to 「は、」 for TTS reading.

    Args:
        text: Input text containing colons

    Returns:
        Text with colons converted to 「は、」
        Excludes time patterns (10:30) and ratios (1:3)
    """
```

### 実装アプローチ
1. 数字:数字パターン（時刻・比率）を一時的にプレースホルダーに置換
2. 残りのコロン（全角・半角）を「は、」に変換
3. プレースホルダーを元に戻す

または

1. negative lookahead/lookbehind で数字パターンを除外した正規表現を使用
2. 全角・半角コロンを一度に変換

### パターン定義例
```python
# 時刻・比率パターン（除外対象）
TIME_RATIO_PATTERN = re.compile(r'\d+:\d+')

# コロンパターン（変換対象）
COLON_PATTERN = re.compile(r'[:：]')
```

### 追加すべき定数
```python
# Colon patterns for conversion
FULL_WIDTH_COLON = "："
HALF_WIDTH_COLON = ":"
COLON_REPLACEMENT = "は、"
```

## FAIL 出力例
```
FAILED tests/test_punctuation_rules.py::TestNormalizeColonsFullWidth::test_normalize_colons_full_width_basic
ImportError: cannot import name '_normalize_colons' from 'src.punctuation_normalizer'
```

## 既存テスト状態
- US1-6 テスト: 102 tests PASS (リグレッションなし)
- US7 新規テスト: 17 tests FAIL (RED)

## 次ステップ
phase-executor が「実装 (GREEN)」→「検証」を実行:
1. `src/punctuation_normalizer.py` に `_normalize_colons()` 関数を実装
2. `make test` で 17 tests を PASS させる
3. リグレッションがないことを確認
