# Quickstart: 新XMLフォーマット対応

**Branch**: `004-new-xml-format` | **Date**: 2026-02-17

## Prerequisites

```bash
# venv 有効化
source .venv/bin/activate

# 依存パッケージ確認
pip install -r requirements.txt

# VOICEVOX Core 設定
ls voicevox_core/
```

## Usage

### 基本使用法

```bash
python -m src.xml2_pipeline --input sample/book2.xml --output ./output
```

### 効果音指定

```bash
python -m src.xml2_pipeline \
    --input sample/book2.xml \
    --chapter-sound assets/sounds/chapter.mp3 \
    --section-sound assets/sounds/section.mp3 \
    --output ./output
```

### ページ範囲指定

```bash
python -m src.xml2_pipeline \
    --input sample/book2.xml \
    --start-page 1 \
    --end-page 10 \
    --output ./output
```

## CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--input`, `-i` | (required) | 入力 book2.xml ファイル |
| `--output`, `-o` | `./output` | 出力ディレクトリ |
| `--chapter-sound` | `assets/sounds/chapter.mp3` | chapter 用効果音 |
| `--section-sound` | `assets/sounds/section.mp3` | section 用効果音 |
| `--style-id` | `13` | VOICEVOX スタイル ID |
| `--speed` | `1.0` | 読み上げ速度 |
| `--start-page` | `1` | 開始位置（コンテンツ番号） |
| `--end-page` | (last) | 終了位置 |

## Testing

```bash
# パーサーテスト
make test TEST_PATH=tests/test_xml2_parser.py

# パイプラインテスト
make test TEST_PATH=tests/test_xml2_pipeline.py

# 全テスト
make test
```

## Output Structure

```
output/{content_hash}/
├── cleaned_text.txt     # クリーニング済みテキスト
├── segments/
│   ├── segment_0001.wav # セグメント別音声
│   ├── segment_0002.wav
│   └── ...
└── book.wav             # 結合音声
```
