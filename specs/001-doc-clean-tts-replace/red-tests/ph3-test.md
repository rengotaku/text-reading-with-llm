# Phase 3 RED Tests

## サマリー
- Phase: Phase 3 - User Story 2/3 - 図表・注釈参照の読み上げ
- FAIL テスト数: 22 methods (1 import error blocking collection)
- テストファイル: tests/test_reference_normalization.py

## FAIL テスト一覧

| テストファイル | テストクラス | テストメソッド | 期待動作 |
|---------------|-------------|---------------|---------|
| tests/test_reference_normalization.py | TestNormalizeFigureReference | test_normalize_figure_reference_basic | `図2.1を参照` -> `ず2の1を参照` |
| tests/test_reference_normalization.py | TestNormalizeFigureReference | test_normalize_figure_reference_full_width_dot | `図3．2に示す` -> `ず3の2に示す` |
| tests/test_reference_normalization.py | TestNormalizeFigureReference | test_normalize_figure_single_digit | `図1を参照` -> `ず1を参照` |
| tests/test_reference_normalization.py | TestNormalizeFigureReference | test_normalize_figure_reference_multi_digit | `図12.34を参照` -> `ず12の34を参照` |
| tests/test_reference_normalization.py | TestNormalizeTableReference | test_normalize_table_reference_basic | `表1.2に示す` -> `ひょう1の2に示す` |
| tests/test_reference_normalization.py | TestNormalizeTableReference | test_normalize_table_reference_full_width_dot | `表4．5を見てください` -> `ひょう4の5を見てください` |
| tests/test_reference_normalization.py | TestNormalizeTableReference | test_normalize_table_single_digit | `表2を参照` -> `ひょう2を参照` |
| tests/test_reference_normalization.py | TestNormalizeNoteReference | test_normalize_note_reference_basic | `注1.6を参照` -> `ちゅう1の6を参照` |
| tests/test_reference_normalization.py | TestNormalizeNoteReference | test_normalize_note_reference_full_width_dot | `注2．3を確認` -> `ちゅう2の3を確認` |
| tests/test_reference_normalization.py | TestNormalizeNoteReference | test_normalize_note_single_digit | `注5を参照` -> `ちゅう5を参照` |
| tests/test_reference_normalization.py | TestNormalizeReferencesMixed | test_normalize_references_mixed_all_types | `図2.1と表3.4と注5.6` -> `ず2の1とひょう3の4とちゅう5の6` |
| tests/test_reference_normalization.py | TestNormalizeReferencesMixed | test_normalize_references_in_sentence | 文中複数参照の処理 |
| tests/test_reference_normalization.py | TestNormalizeReferencesMixed | test_normalize_references_multiple_same_type | `図1.1と図1.2を比較` -> `ず1の1とず1の2を比較` |
| tests/test_reference_normalization.py | TestNormalizeReferencesIdempotent | test_normalize_references_idempotent_no_refs | 参照なしテキストは変化しない |
| tests/test_reference_normalization.py | TestNormalizeReferencesIdempotent | test_normalize_references_idempotent_already_processed | 冪等性の確認 |
| tests/test_reference_normalization.py | TestNormalizeReferencesEdgeCases | test_normalize_references_empty_string | 空文字列処理 |
| tests/test_reference_normalization.py | TestNormalizeReferencesEdgeCases | test_normalize_references_whitespace_only | 空白のみ処理 |
| tests/test_reference_normalization.py | TestNormalizeReferencesEdgeCases | test_normalize_references_heading_format | `注1.1 概要` -> `ちゅう1の1 概要` |
| tests/test_reference_normalization.py | TestNormalizeReferencesEdgeCases | test_normalize_references_consecutive | 連続参照処理 |
| tests/test_reference_normalization.py | TestNormalizeReferencesEdgeCases | test_normalize_references_with_parentheses | 括弧内参照処理 |
| tests/test_reference_normalization.py | TestNormalizeReferencesEdgeCases | test_normalize_references_real_world_example | 実使用例 |

## 実装ヒント

### 関数シグネチャ
```python
def _normalize_references(text: str) -> str:
    """参照（図X.Y, 表X.Y, 注X.Y）を自然な読み仮名に変換する"""
```

### 必要な正規表現パターン

```python
# 図参照: 図X.Y または 図X
FIGURE_REF_PATTERN = re.compile(r'図(\d+)([\.．](\d+))?')

# 表参照: 表X.Y または 表X
TABLE_REF_PATTERN = re.compile(r'表(\d+)([\.．](\d+))?')

# 注参照: 注X.Y または 注X
NOTE_REF_PATTERN = re.compile(r'注(\d+)([\.．](\d+))?')
```

### 変換ロジック

1. 図X.Y -> ずXのY (ドットを「の」に変換)
2. 図X -> ずX (単一数字)
3. 表X.Y -> ひょうXのY
4. 注X.Y -> ちゅうXのY

### 実装ファイル
- `src/text_cleaner.py` に `_normalize_references(text: str) -> str` を実装
- パターン定数は関数の前にモジュールレベルで定義

## FAIL 出力例

```
============================= test session starts ==============================
platform linux -- Python 3.13.11, pytest-9.0.2, pluggy-1.6.0
rootdir: /data/projects/text-reading-with-llm
collecting ... collected 18 items / 1 error

==================================== ERRORS ====================================
____________ ERROR collecting tests/test_reference_normalization.py ____________
ImportError while importing test module '/data/projects/text-reading-with-llm/tests/test_reference_normalization.py'.
tests/test_reference_normalization.py:10: in <module>
    from src.text_cleaner import _normalize_references
E   ImportError: cannot import name '_normalize_references' from 'src.text_cleaner' (/data/projects/text-reading-with-llm/src/text_cleaner.py)
=========================== short test summary info ============================
ERROR tests/test_reference_normalization.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.08s ===============================
```

## User Story 対応

| User Story | FR | テストカバレッジ |
|------------|-----|-----------------|
| US2: 図表参照の適切な読み上げ | FR-004, FR-005 | TestNormalizeFigureReference, TestNormalizeTableReference |
| US3: 脚注・注釈番号の処理 | FR-006 | TestNormalizeNoteReference |

## 次ステップ

phase-executor が以下を実行:
1. T027: RED テスト読み込み
2. T028-T030: `_normalize_references()` 実装
3. T031: `make test` PASS (GREEN) 確認
4. T032-T033: 検証と Phase 出力生成
