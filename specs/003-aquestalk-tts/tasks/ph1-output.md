# Phase 1 Output: Setup

## 作業概要

既存コードを分析し、AquesTalk10 パイプライン実装のための設計準備を完了した。

## 既存コード分析結果

### 1. VoicevoxSynthesizer パターン (src/voicevox_client.py)

**クラス構造**:
```python
@dataclass
class VoicevoxConfig:
    onnxruntime_dir: Path
    open_jtalk_dict_dir: Path
    vvm_dir: Path
    style_id: int = 13
    speed_scale: float = 1.0
    pitch_scale: float = 0.0
    volume_scale: float = 1.0

class VoicevoxSynthesizer:
    def __init__(self, config: VoicevoxConfig | None = None)
    def initialize(self) -> None
    def load_model(self, vvm_path: Path | None = None) -> None
    def load_all_models(self) -> None
    def synthesize(self, text, style_id, speed_scale, ...) -> bytes
    def tts(self, text, style_id) -> bytes
```

**AquesTalk 向け設計**:
- `AquesTalkConfig`: speed (50-300), voice (0-200), pitch (50-200) のパラメータ
- `AquesTalkSynthesizer`: initialize(), synthesize() メソッド
- サンプルレート: 16000Hz（VOICEVOX の 24000Hz とは異なる）

### 2. xml_pipeline.py パターン

**主要関数**:
- `parse_args()`: CLI 引数解析（--input, --output, --start-page, --end-page, --heading-sound）
- `load_heading_sound()`: 効果音読み込み + リサンプリング
- `process_pages_with_heading_sound()`: ページ処理 + HEADING_MARKER 分割
- `main()`: エントリーポイント

**処理フロー**:
```
XML → xml_parser.parse_book_xml() → xml_parser.to_page()
    → text_cleaner.init_for_content() + clean_page_text()
    → VoicevoxSynthesizer.synthesize() → WAV 出力
```

### 3. text_cleaner.py

**重要機能**:
- `init_for_content()`: LLM 辞書初期化
- `clean_page_text(text, heading_marker)`: テキストクリーニング
  - HEADING_MARKER のプレースホルダー保護
  - URL, ISBN, 括弧英語の除去
  - 句読点正規化、数字→カナ変換、MeCab 変換
- `split_text_into_chunks()`: チャンク分割

**AquesTalk 用追加実装**:
- 数字を `<NUM VAL=123>` タグに変換する関数
- 見出し・段落末への句点自動追加

### 4. xml_parser.py

**データ構造**:
```python
@dataclass
class XmlPage:
    number: int
    source_file: str
    announcement: str
    content_text: str
    figures: list[Figure]

HEADING_MARKER = "\uE000HEADING\uE000"  # 見出しマーカー
```

**関数**:
- `parse_book_xml(xml_path)`: XML 解析
- `to_page(xml_page)`: XmlPage → Page 変換
- `_extract_content_text()`: HEADING_MARKER 付きテキスト抽出

### 5. テストパターン (tests/test_xml_pipeline.py)

**テストクラス構造**:
- `TestParseArgsRequiredInput`: 必須引数テスト
- `TestParseArgsDefaults`: デフォルト値テスト
- `TestParseArgsCustomValues`: カスタム値テスト
- `TestFileNotFoundError`: エラーハンドリング
- `TestInvalidXmlError`: XML パースエラー

**フィクスチャ**:
- `tests/fixtures/sample_book.xml`: テスト用 XML

## AquesTalk 実装設計

### 新規ファイル

1. **src/aquestalk_client.py**
   - `AquesTalkConfig`: dataclass（speed, voice, pitch）
   - `AquesTalkSynthesizer`: 合成クラス
   - `convert_numbers_to_num_tags()`: 数字 → `<NUM>` タグ変換
   - `add_punctuation()`: 句点自動追加

2. **src/aquestalk_pipeline.py**
   - `parse_args()`: CLI 引数（--speed, --voice, --pitch, --heading-sound）
   - `load_heading_sound()`: 16kHz リサンプリング
   - `process_pages_with_heading_sound()`: 見出し速度調整 (speed 80)
   - `main()`: エントリーポイント

3. **tests/test_aquestalk_client.py**
4. **tests/test_aquestalk_pipeline.py**

### AquesTalk10 パラメータ

| パラメータ | 範囲 | デフォルト | 用途 |
|-----------|------|-----------|------|
| speed | 50-300 | 100 | 読み上げ速度 |
| voice | 0-200 | 100 | 声質 |
| pitch | 50-200 | 100 | ピッチ |

### 見出し強調

- 見出しセグメントは speed=80 で読み上げ
- 通常セグメントはユーザー指定の speed で読み上げ

## 注意点

1. **サンプルレート差異**: AquesTalk10 は 16kHz、VOICEVOX は 24kHz
2. **効果音リサンプリング**: 16kHz にリサンプリング必要
3. **HEADING_MARKER 保護**: text_cleaner の既存機能を活用
4. **`<NUM>` タグ**: text_cleaner の数字変換前に適用する必要あり

## 修正ファイル一覧

- なし（Phase 1 は分析のみ）

## 実装のミス・課題

- なし（分析フェーズのため）
