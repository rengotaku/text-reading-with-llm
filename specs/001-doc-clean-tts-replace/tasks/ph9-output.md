# Phase 9 Output

## 作業概要
- Phase 9 - パイプライン統合の実装完了
- FAIL テスト 5 件を PASS させた
- 全 8 User Stories の機能を clean_page_text() パイプラインに統合

## 修正ファイル一覧
- `src/text_cleaner.py` - clean_page_text() 関数にテキストクリーニング処理を統合

## 実装内容

### clean_page_text() の変更

clean_page_text() の冒頭に、以下の順序で新規関数を統合:

```python
def clean_page_text(text: str) -> str:
    """Clean a single page's text for TTS consumption."""
    # NEW: Text cleaning for TTS (before markdown cleanup)
    # Process in specific order to avoid interference
    text = _clean_urls(text)                    # US1: Remove URLs
    text = _clean_isbn(text)                    # US4: Remove ISBN
    text = _clean_parenthetical_english(text)   # US5: Remove (English)
    text = _normalize_references(text)          # US2/3: 図X.Y → ずXのY

    # (既存の Markdown クリーニング処理...)
    # ...

    # (既存の TTS 正規化処理...)
    text = normalize_punctuation(text)  # コロン・鉤括弧・読点ルールが適用される
    text = normalize_numbers(text)
    # ...
```

### 処理順序の重要性

1. **URL 処理を最初に実行** - URL 内の図表参照を誤変換しないため
2. **ISBN 処理** - 数字読み仮名変換前に削除
3. **括弧処理** - 英語表記を除去
4. **参照正規化** - 図表参照を読み仮名に変換
5. **Markdown クリーニング** - 既存処理
6. **句読点正規化** - コロン・鉤括弧変換、読点挿入ルール（除外パターン適用済み）

この順序により冪等性が確保され、2回処理しても結果が同一になる。

## テスト結果

### GREEN 確認
```
============================= 156 passed in 0.08s ==============================
```

全 156 テストが PASS:
- Phase 9 統合テスト: 21 tests (5 件が FAIL → PASS に変化)
- Phase 2-8 ユニットテスト: 135 tests (リグレッションなし)

### PASS した統合テスト

| テストファイル | テストメソッド | 説明 |
|---------------|---------------|------|
| test_integration.py | test_clean_page_text_all_features | 全変換（URL/ISBN/括弧/参照/コロン/鉤括弧）が適用される |
| test_integration.py | test_clean_page_text_isbn_integration | ISBN が削除される |
| test_integration.py | test_clean_page_text_url_before_reference | URL処理が参照正規化より先に行われる |
| test_integration.py | test_clean_page_text_isbn_before_reference | ISBN処理が参照正規化より先に行われる |
| test_integration.py | test_clean_page_text_idempotent_basic | 再処理しても結果が同一（冪等性） |

## 注意点

### 次 Phase (Phase 10) で必要な情報
- Phase 10: Polish & Cross-Cutting Concerns
  - パフォーマンス検証（regex パターンのコンパイル最適化）
  - quickstart.md シナリオ検証
  - 処理時間増加 ≤10% の確認

### 統合パイプラインの特性

1. **冪等性が確保されている**
   - clean_page_text() を複数回呼び出しても同じ結果
   - URL/ISBN 削除後の数字は読み仮名に変換済みのため、「は」の後に読点が入らない

2. **処理順序が固定されている**
   - URL → ISBN → 括弧 → 参照 → Markdown → 句読点
   - この順序を変更すると冪等性が崩れる可能性がある

3. **リグレッションがない**
   - 既存の normalize_punctuation() の動作に変更なし
   - 既存の Markdown クリーニング処理に影響なし

## 実装のミス・課題

なし - 全テストが PASS し、冪等性も確保されている。
