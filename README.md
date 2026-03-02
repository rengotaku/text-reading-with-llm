# text-reading-with-llm

![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/rengotaku/python-coverage-comment-action-data/raw/endpoint.json)

Markdown形式の書籍をVOICEVOX Coreで音声化するTTSパイプライン。

## セットアップ

```bash
# venv作成 + 依存関係 + VOICEVOXダウンロード
make setup
```

## 基本的な使い方

### 1. XML パイプライン（段階的実行）

#### 1.1 全パイプライン一括実行

```bash
# 辞書生成 → テキストクリーニング → TTS を順次実行
make run INPUT=path/to/book.xml
```

#### 1.2 段階的実行（推奨）

各ステップを個別に実行することで、中間結果の確認やデバッグが容易になります。

```bash
# Step 1: 読み辞書生成（固有名詞・専門用語の読み方を LLM で生成）
make gen-dict INPUT=path/to/book.xml

# Step 2: テキストクリーニング（URL除去、数字変換等）
# → data/{hash}/cleaned_text.txt が生成される
make clean-text INPUT=path/to/book.xml

# Step 3: TTS 音声生成（cleaned_text.txt から音声生成）
make xml-tts INPUT=path/to/book.xml
```

#### 1.3 TTS パラメータ調整時の時短テクニック

テキストクリーニングは1回実行すれば、TTS パラメータ（速度、スタイル等）の調整時に再実行不要です。

```bash
# 初回: 全パイプライン実行
make run INPUT=sample.xml

# 2回目以降: TTS のみ再実行（テキストクリーニングをスキップ）
make xml-tts INPUT=sample.xml SPEED=1.5
make xml-tts INPUT=sample.xml STYLE_ID=3  # ずんだもん
```

**処理時間**: テキストクリーニングのスキップにより処理時間が約50%短縮されます。

### 2. Markdown パイプライン（章分割あり）

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

### 3. 音声生成（章分割なし）

```bash
make run-simple
```

### 4. 既存データの章分割

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

# パイプライン実行（XML処理）
make run           # 全パイプライン実行（辞書生成 → テキストクリーニング → TTS）
make gen-dict      # 読み辞書生成のみ
make clean-text    # テキストクリーニングのみ（XML → cleaned_text.txt）
make xml-tts       # TTS生成のみ（INPUT指定または既存cleaned_text.txt使用）

# その他のパイプライン
make run-simple    # TTS実行（章分割なし）
make toc           # TOC生成のみ
make organize      # 既存ページを章整理

# 開発・メンテナンス
make test          # テスト実行
make lint          # リンター実行
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
