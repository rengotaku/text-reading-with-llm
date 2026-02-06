# Phase 9 RED Tests

## サマリー
- Phase: Phase 9 - パイプライン統合
- FAIL テスト数: 5
- PASS テスト数: 16
- テストファイル: tests/test_integration.py

## FAIL テスト一覧

| テストファイル | テストメソッド | 期待動作 |
|---------------|---------------|---------|
| tests/test_integration.py | test_clean_page_text_all_features | 全変換（URL/ISBN/括弧/参照/コロン/鉤括弧）が適用される |
| tests/test_integration.py | test_clean_page_text_isbn_integration | ISBN が削除される |
| tests/test_integration.py | test_clean_page_text_url_before_reference | URL処理が参照正規化より先に行われる |
| tests/test_integration.py | test_clean_page_text_isbn_before_reference | ISBN処理が参照正規化より先に行われる |
| tests/test_integration.py | test_clean_page_text_idempotent_basic | 再処理しても結果が同一 |

## PASS テスト一覧

| テストクラス | テスト数 | 説明 |
|-------------|---------|------|
| TestCleanPageTextIntegration | 3 | URL/括弧/参照の個別統合テスト |
| TestCleanPageTextProcessingOrder | 1 | 括弧処理順序テスト |
| TestCleanPageTextIdempotent | 2 | 冪等性テスト（複雑/URL） |
| TestNormalizePunctuationIntegration | 5 | 句読点正規化統合テスト |
| TestIntegrationEdgeCases | 5 | エッジケーステスト |

## FAIL 原因分析

### 1. ISBN 未統合
`_clean_isbn()` 関数が `clean_page_text()` パイプラインに統合されていない。

**現状の出力:**
```
ISBNきゅうひゃくななじゅうはちよんはちまんななせんさんびゃくじゅういちはっぴゃくろくじゅうごはち
```

**期待される出力:**
ISBN 部分が完全に削除される

### 2. URL パターンの問題
URL 内に日本語が含まれる場合、完全に削除されない。

**入力:**
```
図解は[こちら](https://example.com/図2.1)を参照
```

**現状の出力:**
```
ズカイはこちらhttpsは、//example.com/ズにてんいちをサンショウ
```

**期待される出力:**
```
ズカイはこちらをサンショウ
```

### 3. 冪等性の問題
2回目の処理で「は」の後に読点が追加される。

**1回目の出力:**
```
...ろくじゅうごはち
```

**2回目の出力:**
```
...ろくじゅうごは、ち
```

これは ISBN 削除後、数字が読み仮名に変換され、その後「は」の後に読点挿入ルールが適用されるため。

## 実装ヒント

### 1. clean_page_text() への関数統合

`src/text_cleaner.py` の `clean_page_text()` に以下の関数を統合する:

```python
def clean_page_text(text: str) -> str:
    """Clean a single page's text for TTS consumption."""
    # 新規追加: URL処理を最初に実行
    text = _clean_urls(text)

    # 新規追加: ISBN処理
    text = _clean_isbn(text)

    # 新規追加: 括弧内英語除去
    text = _clean_parenthetical_english(text)

    # 新規追加: 図表参照正規化
    text = _normalize_references(text)

    # 既存の処理...
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    # ...
```

### 2. 処理順序

推奨される処理順序:
1. `_clean_urls()` - URL を先に削除（URL 内の図表参照を誤変換しないため）
2. `_clean_isbn()` - ISBN を削除
3. `_clean_parenthetical_english()` - 括弧内英語を除去
4. `_normalize_references()` - 図表参照を正規化
5. 既存の Markdown 処理
6. `normalize_punctuation()` - 句読点正規化
7. `normalize_numbers()` - 数字正規化
8. その他の処理

### 3. 冪等性の確保

冪等性を確保するために:
- 数字読み仮名変換後の「は」に読点が入らないよう、除外パターンを検討
- または、ISBN/URL 処理を normalize_punctuation より前に行う

## FAIL 出力例

```
FAILED tests/test_integration.py::TestCleanPageTextIntegration::test_clean_page_text_all_features
AssertionError: ISBN should be removed: got 'ショウサイはこちらhttpsは、//example.comをサンショウ。
ISBNきゅうひゃくななじゅうはちよんはちまんななせんさんびゃくじゅういちはっぴゃくろくじゅうごはち
...'

FAILED tests/test_integration.py::TestCleanPageTextIntegration::test_clean_page_text_isbn_integration
AssertionError: ISBN should be removed: got 'このホンはISBNきゅうひゃくななじゅうはちよんにひゃくきゅうじゅうなないちまんごせんななじゅうにさんでコウニュウできます'

FAILED tests/test_integration.py::TestCleanPageTextProcessingOrder::test_clean_page_text_url_before_reference
AssertionError: assert 'example.com' not in 'ズカイはこちらhttpsは、//example.com/ズにてんいちをサンショウ'

FAILED tests/test_integration.py::TestCleanPageTextProcessingOrder::test_clean_page_text_isbn_before_reference
AssertionError: assert 'ISBN' not in 'ISBNきゅうひゃくななじゅうはちよんはちまんななせんさんびゃくじゅういちはっぴゃくろくじゅうごはちのズにてんいちをサンショウ'

FAILED tests/test_integration.py::TestCleanPageTextIdempotent::test_clean_page_text_idempotent_basic
AssertionError: clean_page_text should be idempotent:
first='...ろくじゅうごはち...'
second='...ろくじゅうごは、ち...'
```

## テスト実装詳細

### TestCleanPageTextIntegration (5 tests)
- `test_clean_page_text_all_features`: 全機能統合テスト
- `test_clean_page_text_url_integration`: URL 処理統合
- `test_clean_page_text_isbn_integration`: ISBN 処理統合
- `test_clean_page_text_parenthetical_integration`: 括弧処理統合
- `test_clean_page_text_reference_integration`: 参照正規化統合

### TestCleanPageTextProcessingOrder (3 tests)
- `test_clean_page_text_url_before_reference`: URL 優先順序
- `test_clean_page_text_isbn_before_reference`: ISBN 優先順序
- `test_clean_page_text_parenthetical_after_url`: 括弧処理順序

### TestCleanPageTextIdempotent (3 tests)
- `test_clean_page_text_idempotent_basic`: 基本冪等性
- `test_clean_page_text_idempotent_complex`: 複雑入力冪等性
- `test_clean_page_text_idempotent_url_markdown`: URL 冪等性

### TestNormalizePunctuationIntegration (5 tests)
- `test_normalize_punctuation_all_rules`: 全ルール統合
- `test_normalize_punctuation_colon_conversion`: コロン変換
- `test_normalize_punctuation_bracket_conversion`: 鉤括弧変換
- `test_normalize_punctuation_exclusion_patterns`: 除外パターン
- `test_normalize_punctuation_combined_example`: 複合例

### TestIntegrationEdgeCases (5 tests)
- `test_empty_input`: 空入力
- `test_whitespace_only`: 空白のみ
- `test_no_special_patterns`: 特殊パターンなし
- `test_multiple_urls_and_references`: 複数 URL/参照
- `test_unicode_characters`: Unicode 文字

## 次ステップ

phase-executor が以下を実行:
1. `clean_page_text()` に `_clean_urls()`, `_clean_isbn()`, `_clean_parenthetical_english()`, `_normalize_references()` を統合
2. 処理順序を調整して冪等性を確保
3. `make test` で GREEN を確認
4. `tasks/ph9-output.md` を生成
