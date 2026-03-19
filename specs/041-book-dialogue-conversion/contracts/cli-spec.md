# CLI Specification: 対話形式変換

## dialogue_converter.py

セクションテキストをLLMで対話形式に変換するCLI。

### Usage

```bash
python -m src.dialogue_converter -i <input_xml> -o <output_dir> [options]
```

### Arguments

| Argument | Short | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| --input | -i | Yes | - | 入力XMLファイルパス |
| --output | -o | No | ./output | 出力ディレクトリ |
| --model | -m | No | gpt-oss:20b | Ollamaモデル名 |
| --max-chars | - | No | 3500 | 分割なし処理の最大文字数 |
| --split-threshold | - | No | 4000 | 分割処理の閾値文字数 |
| --num-predict | - | No | 1500 | LLM生成トークン数上限 |
| --chapter | -c | No | None | 処理対象チャプター番号（指定しない場合は全て） |
| --section | -s | No | None | 処理対象セクション番号（指定しない場合は全て） |
| --dry-run | - | No | False | 変換せずに処理対象を表示 |

### Output

```text
<output_dir>/
├── dialogue_book.xml      # 対話形式変換後のXML
├── conversion_log.json    # 変換ログ（処理時間、文字数等）
└── sections/
    ├── 1.1.xml            # セクション単位のXML（デバッグ用）
    ├── 1.2.xml
    └── ...
```

### Exit Codes

| Code | Description |
|------|-------------|
| 0 | 成功 |
| 1 | 入力ファイルエラー |
| 2 | LLM接続エラー |
| 3 | 変換エラー |

---

## dialogue_pipeline.py

対話形式XMLから複数話者音声を生成するCLI。

### Usage

```bash
python -m src.dialogue_pipeline -i <dialogue_xml> -o <output_dir> [options]
```

### Arguments

| Argument | Short | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| --input | -i | Yes | - | 対話形式XMLファイルパス |
| --output | -o | No | ./output | 出力ディレクトリ |
| --narrator-style | - | No | 13 | ナレーターのVOICEVOXスタイルID |
| --speaker-a-style | - | No | 67 | 博士（A）のスタイルID |
| --speaker-b-style | - | No | 2 | 助手（B）のスタイルID |
| --speed | - | No | 1.0 | 読み上げ速度 |
| --voicevox-dir | - | No | ./voicevox_core | VOICEVOXディレクトリ |
| --chapter-sound | - | No | assets/sounds/chapter.mp3 | チャプター区切り音 |
| --section-sound | - | No | assets/sounds/section.mp3 | セクション区切り音 |
| --acceleration-mode | - | No | AUTO | VOICEVOX加速モード |

### Output

```text
<output_dir>/
├── dialogue_audio/
│   ├── chapter_01/
│   │   ├── section_1.1.wav
│   │   ├── section_1.2.wav
│   │   └── ...
│   └── chapter_02/
│       └── ...
└── full_audio.wav         # 全体結合音声（オプション）
```

### Exit Codes

| Code | Description |
|------|-------------|
| 0 | 成功 |
| 1 | 入力ファイルエラー |
| 2 | VOICEVOX初期化エラー |
| 3 | 音声生成エラー |

---

## Makefile ターゲット

### dialogue-convert

```makefile
dialogue-convert:  ## Convert XML to dialogue format (INPUT=file)
	PYTHONPATH=$(CURDIR) $(PYTHON) -m src.dialogue_converter \
		-i "$(INPUT)" -o "$(OUTPUT)" --model "$(LLM_MODEL)"
```

### dialogue-tts

```makefile
dialogue-tts:  ## Generate multi-speaker TTS from dialogue XML
	PYTHONPATH=$(CURDIR) $(PYTHON) -m src.dialogue_pipeline \
		-i "$(OUTPUT)/dialogue_book.xml" -o "$(OUTPUT)"
```

### dialogue

```makefile
dialogue: dialogue-convert gen-dict clean-text dialogue-tts  ## Full dialogue pipeline
```
