# Quickstart: 対話形式変換

## 前提条件

1. Python 3.10+ がインストールされている
2. Ollama がローカルで動作している
3. gpt-oss:20b モデルがダウンロード済み
4. VOICEVOX Core がセットアップ済み

```bash
# Ollama モデル確認
ollama list | grep gpt-oss

# VOICEVOX 確認
ls voicevox_core/models/vvms/
```

## 基本的な使い方

### 1. 対話形式に変換

```bash
# 単一コマンド
make dialogue-convert INPUT=data/book2.xml

# または直接実行
python -m src.dialogue_converter -i data/book2.xml -o output
```

**出力:**
- `output/dialogue_book.xml` - 対話形式XML

### 2. 音声を生成

```bash
# 読み辞書生成 → テキスト正規化 → TTS生成
make gen-dict INPUT=data/book2.xml
make clean-text INPUT=data/book2.xml
make dialogue-tts

# または一括実行
make dialogue INPUT=data/book2.xml
```

**出力:**
- `output/dialogue_audio/chapter_XX/section_X.X.wav`

## 特定セクションのみ処理

```bash
# チャプター1のセクション1.1のみ
python -m src.dialogue_converter \
  -i data/book2.xml \
  -o output \
  --chapter 1 \
  --section 1.1
```

## 話者の変更

```bash
# カスタム話者設定
python -m src.dialogue_pipeline \
  -i output/dialogue_book.xml \
  -o output \
  --narrator-style 13 \
  --speaker-a-style 67 \
  --speaker-b-style 2
```

### 利用可能なスタイルID（抜粋）

| style_id | キャラクター | 備考 |
|----------|-------------|------|
| 2 | 四国めたん（ノーマル） | デフォルト助手 |
| 13 | 青山龍星 | デフォルトナレーター |
| 67 | 麒ヶ島宗麟 | デフォルト博士 |

## トラブルシューティング

### LLM接続エラー

```bash
# Ollama が動作しているか確認
curl http://localhost:11434/api/tags

# モデルをプル
ollama pull gpt-oss:20b
```

### 長文で処理が遅い

- `--max-chars 2000` で分割閾値を下げる
- `--num-predict 1000` で生成トークン数を減らす

### 変換品質が低い

- Llama-3-ELYZA-JP:8B を試す: `--model Llama-3-ELYZA-JP:8B`
- セクション単位で確認: `--dry-run` で処理対象を確認

## 開発者向け

### テスト実行

```bash
make test

# カバレッジ付き
make coverage
```

### コードチェック

```bash
make lint
make format
```
