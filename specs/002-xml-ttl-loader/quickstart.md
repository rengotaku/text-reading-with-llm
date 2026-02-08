# Quickstart: XML から TTS へのローダー

## 概要

`xml_pipeline.py` は XML 形式の書籍データを読み込み、VOICEVOX で音声ファイルを生成するスクリプトです。

## 前提条件

- Python 3.10+
- VOICEVOX Core（セットアップ済み）
- 仮想環境の有効化

```bash
source .venv/bin/activate
```

## 基本的な使い方

```bash
# XML ファイルから音声を生成
python src/xml_pipeline.py --input sample/book.xml --output output/

# 特定のページ範囲を指定
python src/xml_pipeline.py --input sample/book.xml --start-page 1 --end-page 10

# 話速を調整
python src/xml_pipeline.py --input sample/book.xml --speed 1.2
```

## コマンドライン引数

| 引数 | 短縮形 | 説明 | デフォルト |
|------|--------|------|-----------|
| `--input` | `-i` | 入力 XML ファイル | 必須 |
| `--output` | `-o` | 出力ディレクトリ | `./output` |
| `--start-page` | | 開始ページ番号 | 1 |
| `--end-page` | | 終了ページ番号 | 最終ページまで |
| `--style-id` | | VOICEVOX スタイル ID | 13（青山龍星） |
| `--speed` | | 話速（1.0 = 通常） | 1.0 |
| `--voicevox-dir` | | VOICEVOX Core ディレクトリ | `./voicevox_core` |
| `--max-chunk-chars` | | TTS チャンクの最大文字数 | 500 |

## 出力構造

```
output/{content_hash}/
├── cleaned_text.txt    # 抽出されたテキスト（デバッグ用）
├── pages/
│   ├── page_0001.wav
│   ├── page_0002.wav
│   └── ...
└── book.wav            # 全ページ結合済み
```

## サンプル実行

```bash
# sample/book.xml を処理
python src/xml_pipeline.py -i sample/book.xml -o output/

# 生成された音声を確認
ls output/*/pages/
```

## トラブルシューティング

### "Invalid XML format" エラー

XML ファイルが正しい形式か確認してください。`xmllint` で検証できます。

```bash
xmllint --noout sample/book.xml
```

### "No <page> elements found" エラー

XML に `<page>` 要素が含まれていることを確認してください。

### VOICEVOX 関連エラー

VOICEVOX Core が正しくセットアップされているか確認してください。

```bash
ls voicevox_core/
# 以下が存在すること: onnxruntime/, dict/, models/
```
