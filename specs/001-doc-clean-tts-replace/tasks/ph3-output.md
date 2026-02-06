# Phase 3 Output

## 作業概要
- Phase 3 - User Story 2/3 - 図表・注釈参照の読み上げ の実装完了
- FAIL テスト 21 件を PASS させた
- `_normalize_references()` 関数を実装し、図表・注釈参照を読み仮名に変換

## 修正ファイル一覧
- `src/text_cleaner.py` - 参照正規化関数と定数パターンを追加

## 実装詳細

### 追加した定数
```python
# Reference patterns for TTS normalization (US2/US3)
REFERENCE_PATTERNS = [
    (re.compile(r'図(\d+)[.．](\d+)'), r'ず\1の\2'),  # 図X.Y
    (re.compile(r'図(\d+)'), r'ず\1'),               # 図X
    (re.compile(r'表(\d+)[.．](\d+)'), r'ひょう\1の\2'),  # 表X.Y
    (re.compile(r'表(\d+)'), r'ひょう\1'),           # 表X
    (re.compile(r'注(\d+)[.．](\d+)'), r'ちゅう\1の\2'),  # 注X.Y
    (re.compile(r'注(\d+)'), r'ちゅう\1'),           # 注X
]
```

### 追加した関数
```python
def _normalize_references(text: str) -> str:
    """Normalize figure/table/note references for TTS.

    Converts:
    - 図X.Y → ずXのY
    - 表X.Y → ひょうXのY
    - 注X.Y → ちゅうXのY
    """
    for pattern, replacement in REFERENCE_PATTERNS:
        text = pattern.sub(replacement, text)
    return text
```

## テスト結果

```
39 passed in 0.03s
```

全テストが PASS:
- 21 tests: 参照正規化 (US2/US3) - 新規
- 18 tests: URL処理 (US1) - 既存（リグレッションなし）

## 変換例

| 入力 | 出力 |
|-----|------|
| `図2.1を参照` | `ず2の1を参照` |
| `表3．4に示す` | `ひょう3の4に示す` |
| `注5を参照` | `ちゅう5を参照` |
| `図1.1と表2.2と注3.3` | `ず1の1とひょう2の2とちゅう3の3` |

## 注意点
- 半角・全角ドット両対応: `図2.1` と `図2．1` 両方処理
- 単一数字対応: `図1` → `ず1`（ドットなし）
- 複数桁対応: `図12.34` → `ず12の34`
- 冪等性確認済み: 複数回実行しても結果不変

## 次 Phase への引き継ぎ
- Phase 4: User Story 4 - ISBN・書籍情報の簡略化
- 次回実装: `_clean_isbn()` 関数
- 既存機能: URL処理 + 参照正規化が統合され動作中

## 実装のミス・課題
- なし（全テスト PASS、リグレッションなし）
