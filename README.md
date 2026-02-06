# text-reading-with-llm

Markdown形式の書籍をVOICEVOX Coreで音声化するTTSパイプライン。

## セットアップ

```bash
# venv作成 + 依存関係 + VOICEVOXダウンロード
make setup
```

## 基本的な使い方

### 1. 音声生成（章分割あり）

```bash
# config.yamlのinputを使用
make run

# 入力ファイルを指定
make run INPUT=path/to/book.md
```

出力構造:
```
data/{content_hash}/
├── toc.json              # 目次情報
├── chapters/
│   ├── chapter_01.wav    # 章結合音声
│   ├── chapter_02.wav
│   ├── ...
│   ├── chapter_01/
│   │   ├── info.json     # 章メタ情報
│   │   └── pages/        # ページ別WAV
│   ├── chapter_02/
│   ...
```

### 2. 音声生成（章分割なし）

```bash
make run-simple
```

### 3. 既存データの章分割

すでにページ単位のWAVがある場合、後から章ごとに整理できる。

```bash
# TOC生成
make toc DATA_DIR=data/72a2534e9e81

# ページを章フォルダに整理 + 章音声を結合
make organize DATA_DIR=data/72a2534e9e81
```

## 設定

### config.yaml

```yaml
input: sample/book.md
output: data

voicevox:
  style_id: 13      # 青山龍星
  speed: 1.0
  pitch: 0.0
  volume: 1.0

max_chunk_chars: 500

chapters:
  enabled: true
  start_page: 15    # 前付け・目次をスキップ
```

### Makefile変数

| 変数 | デフォルト | 説明 |
|-----|-----------|------|
| `INPUT` | config.yaml | 入力Markdownファイル |
| `OUTPUT` | data | 出力ベースディレクトリ |
| `STYLE_ID` | 13 | VOICEVOXスタイルID |
| `SPEED` | 1.0 | 話速 |
| `TOC_START_PAGE` | 15 | TOC抽出の開始ページ |
| `DATA_DIR` | - | organize用データディレクトリ |

## コマンド一覧

```bash
make help          # ヘルプ表示
make setup         # 環境構築
make run           # TTS実行（章分割あり）
make run-simple    # TTS実行（章分割なし）
make toc           # TOC生成のみ
make organize      # 既存ページを章整理
make gen-dict      # LLM読み辞書生成
make clean         # 生成ファイル削除
make clean-all     # 全削除（venv含む）
```

## VOICEVOXスタイルID

| ID | キャラクター |
|----|------------|
| 2 | 四国めたん（ノーマル） |
| 3 | ずんだもん（ノーマル） |
| 8 | 春日部つむぎ（ノーマル） |
| 13 | 青山龍星（ノーマル） |

全スタイル一覧: https://voicevox.hiroshiba.jp/

## ディレクトリ構成

```
.
├── config.yaml          # 設定ファイル
├── Makefile
├── sample/
│   └── book.md          # サンプル入力
├── src/
│   ├── pipeline.py      # メインパイプライン
│   ├── toc_extractor.py # 目次抽出
│   ├── organize_chapters.py  # 章整理
│   ├── text_cleaner.py  # テキスト前処理
│   ├── voicevox_client.py    # VOICEVOX連携
│   └── ...
├── data/                # 出力（シンボリックリンク可）
└── voicevox_core/       # VOICEVOXランタイム
```
