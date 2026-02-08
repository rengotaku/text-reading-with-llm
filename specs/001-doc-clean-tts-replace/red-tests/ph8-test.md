# Phase 8 RED Tests

## サマリー
- Phase: Phase 8 - User Story 8 - 鉤括弧の読点変換 (Priority: P2)
- FAIL テスト数: 16
- テストファイル: tests/test_punctuation_rules.py

## FAIL テスト一覧

| テストファイル | テストメソッド | 期待動作 |
|---------------|---------------|---------|
| tests/test_punctuation_rules.py | TestNormalizeBracketsBasic::test_normalize_brackets_basic | 「テスト」という言葉 → 、テスト、という言葉 |
| tests/test_punctuation_rules.py | TestNormalizeBracketsBasic::test_normalize_brackets_single_char | 「A」を選択 → 、A、を選択 |
| tests/test_punctuation_rules.py | TestNormalizeBracketsWithText::test_normalize_brackets_with_text | これは「重要な」ポイントです → これは、重要な、ポイントです |
| tests/test_punctuation_rules.py | TestNormalizeBracketsWithText::test_normalize_brackets_conference_name | テックカンファレンス「SRE NEXT」を立ち上げ → テックカンファレンス、SRE NEXT、を立ち上げ |
| tests/test_punctuation_rules.py | TestNormalizeBracketsWithText::test_normalize_brackets_book_description | 本書は「入門書」です → 本書は、入門書、です |
| tests/test_punctuation_rules.py | TestNormalizeBracketsConsecutive::test_normalize_brackets_consecutive | 「A」と「B」がある → 、A、と、B、がある |
| tests/test_punctuation_rules.py | TestNormalizeBracketsConsecutive::test_normalize_brackets_triple_consecutive | 「X」「Y」「Z」を選ぶ → 、X、、Y、、Z、を選ぶ |
| tests/test_punctuation_rules.py | TestNormalizeBracketsEdgeCases::test_normalize_brackets_at_start | 「注意」してください → 、注意、してください |
| tests/test_punctuation_rules.py | TestNormalizeBracketsEdgeCases::test_normalize_brackets_at_end | これは「テスト」 → これは、テスト、 |
| tests/test_punctuation_rules.py | TestNormalizeBracketsEdgeCases::test_normalize_brackets_reference | 「はじめに」を参照 → 、はじめに、を参照 |
| tests/test_punctuation_rules.py | TestNormalizeBracketsEdgeCases::test_normalize_brackets_empty | これは「」です → これは、、です |
| tests/test_punctuation_rules.py | TestNormalizeBracketsEdgeCases::test_normalize_brackets_nested | 「『内側』の外側」 → 、、内側、の外側、 |
| tests/test_punctuation_rules.py | TestNormalizeBracketsEdgeCases::test_normalize_brackets_empty_string | 空文字列 → 空文字列 |
| tests/test_punctuation_rules.py | TestNormalizeBracketsEdgeCases::test_normalize_brackets_no_brackets | 鉤括弧なしテキスト → 変化なし |
| tests/test_punctuation_rules.py | TestNormalizeBracketsIntegration::test_normalize_punctuation_includes_brackets | normalize_punctuation が鉤括弧変換を含む |
| tests/test_punctuation_rules.py | TestNormalizeBracketsIntegration::test_normalize_punctuation_brackets_and_colons | コロンと鉤括弧の両方が変換される |

## 実装ヒント

### 新規関数
- `src/punctuation_normalizer.py` に `_normalize_brackets(text: str) -> str` を実装

### 実装内容
1. 開き鉤括弧「→ 読点、
2. 閉じ鉤括弧」→ 読点、
3. 二重鉤括弧『』も同様に変換

### 正規表現パターン案
```python
OPEN_BRACKET_PATTERN = re.compile(r'[「『]')
CLOSE_BRACKET_PATTERN = re.compile(r'[」』]')
```

### normalize_punctuation への統合
```python
def normalize_punctuation(text: str) -> str:
    lines = text.split("\n")
    result_lines = []
    for line in lines:
        if not line.strip():
            result_lines.append(line)
            continue
        line = _normalize_colons(line)
        line = _normalize_brackets(line)  # 追加
        result_lines.append(_normalize_line(line))
    return "\n".join(result_lines)
```

## FAIL 出力例

```
FAILED tests/test_punctuation_rules.py::TestNormalizeBracketsBasic::test_normalize_brackets_basic
    E       ImportError: cannot import name '_normalize_brackets' from 'src.punctuation_normalizer'

FAILED tests/test_punctuation_rules.py::TestNormalizeBracketsIntegration::test_normalize_punctuation_includes_brackets
    E       AssertionError: normalize_punctuationが鉤括弧変換を含むべき: got '本書は「入門書」です', expected substring '、入門書、'
    E       assert '、入門書、' in '本書は「入門書」です'
```

## テスト結果サマリー

```
======================== 16 failed, 119 passed in 0.13s ========================
```

- 既存テスト (US1-7): 119 passed (リグレッションなし)
- 新規テスト (US8): 16 failed (RED 確認済み)
