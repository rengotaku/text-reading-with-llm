# Quickstart: 読み辞書生成のXMLファイル対応

**Branch**: `006-xml-dict-support`

## 変更対象ファイル

| ファイル | 変更内容 |
|----------|----------|
| `src/generate_reading_dict.py` | `main()` にXML分岐ロジックを追加 |
| `tests/test_generate_reading_dict.py` | 新規：XML入力のテスト |
| `tests/fixtures/` | テスト用XMLフィクスチャ追加 |

## 実装の要点

1. `main()` 内で `input_path.suffix` を判定
2. `.xml` の場合: `parse_book2_xml()` → チャプターグループ化 → 用語抽出
3. `.md` の場合: 既存フロー（変更なし）
4. それ以外: エラーメッセージ + `sys.exit(1)`

## テスト実行

```bash
source .venv/bin/activate
python -m pytest tests/test_generate_reading_dict.py -v
```

## 手動検証

```bash
make gen-dict INPUT=sample/book2.xml
# → data/{hash}/readings.json が生成されることを確認
```
