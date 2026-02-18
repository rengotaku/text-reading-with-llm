# Quickstart: チャプター分割とクリーニング

**Date**: 2026-02-18
**Branch**: `005-chapter-split-cleaning`

## 概要

xml2_pipeline を使用して book2.xml を処理し、chapter 単位で分割された音声ファイルを生成する。

## 前提条件

- Python 3.10+
- VOICEVOX Core がセットアップ済み
- 効果音ファイル: `assets/sounds/chapter.mp3`, `assets/sounds/section.mp3`

## 基本的な使い方

### 1. book2.xml を処理

```bash
make xml-tts INPUT=sample/book2.xml PARSER=xml2
```

### 2. 出力構造

```
output/{content_hash}/
├── chapters/
│   ├── ch01_企画で失敗.wav
│   ├── ch02_仕様で失敗.wav
│   └── ...
├── book.wav
└── cleaned_text.txt
```

### 3. 出力の確認

```bash
# 生成されたファイル一覧
ls -la output/*/chapters/

# cleaned_text.txt の確認（クリーニング済みテキスト）
head -50 output/*/cleaned_text.txt
```

## CLI オプション

```bash
python -m src.xml2_pipeline \
    --input sample/book2.xml \
    --output ./output \
    --chapter-sound assets/sounds/chapter.mp3 \
    --section-sound assets/sounds/section.mp3 \
    --style-id 13 \
    --speed 1.0
```

| オプション | デフォルト | 説明 |
|------------|------------|------|
| `--input`, `-i` | 必須 | 入力 XML ファイル |
| `--output`, `-o` | `./output` | 出力ディレクトリ |
| `--chapter-sound` | `assets/sounds/chapter.mp3` | 章効果音 |
| `--section-sound` | `assets/sounds/section.mp3` | 節効果音 |
| `--style-id` | `13` | VOICEVOX スタイル ID |
| `--speed` | `1.0` | 読み上げ速度 |

## テスト実行

```bash
# 全テスト実行
make test

# xml2 関連テストのみ
PYTHONPATH=. pytest tests/test_xml2_parser.py tests/test_xml2_pipeline.py -v
```

## トラブルシューティング

### Q: 音声にURLが読み上げられる

**A**: `clean_page_text()` が適用されていない可能性があります。
- `cleaned_text.txt` を確認し、URL が除去されているか確認
- xml2_pipeline.py の `process_content()` 内で `clean_page_text()` が呼ばれているか確認

### Q: chapters/ ディレクトリが生成されない

**A**: book2.xml に `<chapter>` 要素がない可能性があります。
- `<chapter>` 要素がない場合は `book.wav` のみ出力されます
- XML 構造を確認してください

### Q: ファイル名が文字化けする

**A**: ファイル名サニタイズが正しく動作していない可能性があります。
- `sanitize_filename()` 関数の動作を確認
- 日本語文字は除去され、半角英数字のみが残ります
