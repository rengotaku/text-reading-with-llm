# Quickstart: doc-clean-tts-replace

**Branch**: `001-doc-clean-tts-replace`

## 環境セットアップ

```bash
# venv 有効化
source .venv/bin/activate

# 依存関係確認
pip install -r requirements.txt
```

## 開発対象ファイル

| ファイル | 変更内容 |
|---------|---------|
| `src/text_cleaner.py` | URL処理、ISBN処理、括弧処理、参照正規化を追加 |
| `src/punctuation_normalizer.py` | コロン変換、鉤括弧変換、除外パターンを追加 |
| `tests/test_url_cleaning.py` | URL処理のテスト (NEW) |
| `tests/test_punctuation_rules.py` | 句読点ルールのテスト (NEW) |

## 実装順序

1. **text_cleaner.py に新規関数を追加**
   - `_clean_urls()` - FR-001,002,003
   - `_clean_isbn()` - FR-007
   - `_clean_parenthetical_english()` - FR-010
   - `_normalize_references()` - FR-004,005,006

2. **punctuation_normalizer.py を修正**
   - `_normalize_colons()` 追加 - FR-012
   - `_normalize_brackets()` 追加 - FR-013
   - `_normalize_line()` 修正 - FR-011

3. **clean_page_text() のパイプラインに統合**

## テスト実行

```bash
# 全テスト
make test

# 特定テスト
PYTHONPATH=$(pwd) python -m pytest tests/test_url_cleaning.py -v

# 手動テスト
PYTHONPATH=$(pwd) python -c "
from src.text_cleaner import clean_page_text
print(clean_page_text('[SRE NEXT](https://example.com)'))
"
```

## サンプルデータ

テスト用サンプル: `sample/book.md`

```bash
# サンプルで動作確認
make run INPUT=sample/book.md
```

## よく使うコマンド

```bash
# テスト実行
make test

# TTS生成
make run

# クリーンアップ
make clean
```

## 注意事項

- 処理順序が重要（URL処理 → コロン変換の順）
- 正規表現のプリコンパイルでパフォーマンス維持
- 冪等性テストを忘れずに
