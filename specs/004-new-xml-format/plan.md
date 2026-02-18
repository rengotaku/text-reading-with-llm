# Implementation Plan: 新XMLフォーマット対応

**Branch**: `004-new-xml-format` | **Date**: 2026-02-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-new-xml-format/spec.md`

## Summary

book2.xml フォーマット専用のパーサーとパイプラインを実装する。主な機能：
- `<toc>` と `<front-matter>` セクションをスキップ
- `<heading>` 要素に level 属性に応じた効果音マーカー（chapter/section）を付与
- 見出しを「第N章」「第N.N節」形式で読み上げ
- **後方互換性は不要**（book2.xml 専用）

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: xml.etree.ElementTree（標準ライブラリ）, voicevox_core, soundfile, numpy
**Storage**: Files（WAV 出力、assets/sounds/*.mp3）
**Testing**: pytest
**Target Platform**: Linux（Ubuntu）
**Project Type**: single（src/ + tests/）
**Performance Goals**: 既存パイプラインと同等（book2.xml 全体を数分で処理）
**Constraints**: VOICEVOX Core のメモリ使用量（GPU/CPU モード）
**Scale/Scope**: 単一ファイル処理（数百ページの書籍）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution ファイルが存在しないため、以下のプロジェクト固有ルールを適用：
- ✅ venv 使用必須 → 既存環境準拠
- ✅ Makefile ターゲット使用 → 既存パターン維持
- ✅ TDD ワークフロー → speckit フローに準拠

## Project Structure

### Documentation (this feature)

```text
specs/004-new-xml-format/
├── spec.md              # 仕様書 ✅
├── plan.md              # This file ✅
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── checklists/          # 品質チェックリスト ✅
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── xml2_parser.py       # 新規: book2.xml 専用パーサー
├── xml2_pipeline.py     # 新規: book2.xml 専用パイプライン
├── xml_parser.py        # 既存（変更なし）
├── xml_pipeline.py      # 既存（変更なし）
├── text_cleaner.py      # 既存（変更なし）
├── voicevox_client.py   # 既存（変更なし）
└── pipeline.py          # 既存（変更なし）

tests/
├── fixtures/
│   ├── sample_book.xml      # 既存フィクスチャ
│   └── sample_book2.xml     # 新規: book2.xml テスト用
├── test_xml2_parser.py      # 新規: book2.xml パーサーテスト
├── test_xml2_pipeline.py    # 新規: book2.xml パイプラインテスト
├── test_xml_parser.py       # 既存（変更なし）
└── test_xml_pipeline.py     # 既存（変更なし）

assets/sounds/
├── chapter.mp3          # 既存 ✅
└── section.mp3          # 既存 ✅

sample/
├── book.xml             # 既存フォーマット
└── book2.xml            # 新フォーマット（約620KB）
```

**Structure Decision**: book2.xml 専用の新規ファイル（xml2_parser.py, xml2_pipeline.py）を作成。既存コードは変更しない。

## Complexity Tracking

違反なし。新規ファイル追加のみで既存コードへの影響なし。

---

# Phase 0: Research

## Research Summary

### R1: 新 XML フォーマット構造分析

**Decision**: book2.xml は以下の構造を持つ
- `<book>` ルート要素
- `<metadata>` → `<title>`
- `<toc>` → `<entry level="N" number="X.Y" title="...">` （スキップ）
- `<front-matter>` → `<heading>`, `<paragraph>` （スキップ）
- 本文: `<heading level="N">`, `<paragraph>`, `<list>` → `<item>`

**Rationale**: XML サンプル分析により構造を特定。

### R2: 見出しマーカー設計

**Decision**: 新マーカー定数を使用
- `CHAPTER_MARKER` (\uE001) → chapter（level=1）用効果音
- `SECTION_MARKER` (\uE002) → section（level=2+）用効果音

**Rationale**: Unicode Private Use Area 文字を使用し、text_cleaner を通過させる。

### R3: 見出し読み上げ形式

**Decision**: 見出しテキストを以下の形式に変換
- level=1: `第{number}章 {title}`
- level=2+: `第{number}節 {title}`

**Rationale**: 仕様で明確に指定された形式。

### R4: 効果音ロード設計

**Decision**: 2 種類の効果音を CLI オプションで指定
- `--chapter-sound` （デフォルト: `assets/sounds/chapter.mp3`）
- `--section-sound` （デフォルト: `assets/sounds/section.mp3`）

**Rationale**: シンプルな設計。後方互換性不要のため、既存オプションとの整合を考慮不要。

---

# Phase 1: Design

## Data Model

### 新規データ構造

```python
# src/xml2_parser.py

@dataclass
class HeadingInfo:
    """見出し情報"""
    level: int           # 1=chapter, 2+=section
    number: str          # "1", "1.2", "3.10" etc.
    title: str           # 見出しテキスト
    read_aloud: bool = True


@dataclass
class ContentItem:
    """コンテンツ単位"""
    item_type: str       # "paragraph", "heading", "list_item"
    text: str            # テキスト内容（マーカー含む）
    heading_info: HeadingInfo | None = None
```

### マーカー定数

```python
# src/xml2_parser.py
CHAPTER_MARKER = "\uE001"  # chapter 効果音用
SECTION_MARKER = "\uE002"  # section 効果音用
```

## API Contracts

### xml2_parser.py

```python
def parse_book2_xml(xml_path: Path) -> list[ContentItem]:
    """Parse book2.xml and extract content items.

    Skips:
    - <toc> section
    - <front-matter> section
    - Elements with readAloud="false"

    Processes:
    - <heading level="N"> with chapter/section markers
    - <paragraph> elements
    - <list> → <item> elements

    Returns:
        List of ContentItem in document order
    """


def format_heading_text(level: int, number: str, title: str) -> str:
    """Format heading for TTS.

    Returns:
        "第{number}章 {title}" for level=1
        "第{number}節 {title}" for level>=2
    """
```

### xml2_pipeline.py

```python
def parse_args(args=None):
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--output", "-o", default="./output")
    parser.add_argument("--chapter-sound", default="assets/sounds/chapter.mp3")
    parser.add_argument("--section-sound", default="assets/sounds/section.mp3")
    parser.add_argument("--style-id", type=int, default=13)
    parser.add_argument("--speed", type=float, default=1.0)
    # ... other options


def main(args=None):
    """Main entry point for book2.xml processing."""
```

## Integration Points

1. **xml2_parser.py** (新規)
   - `parse_book2_xml()`: book2.xml 専用パーサー
   - `ContentItem`, `HeadingInfo`: データクラス
   - `CHAPTER_MARKER`, `SECTION_MARKER`: マーカー定数
   - `format_heading_text()`: 見出し整形

2. **xml2_pipeline.py** (新規)
   - `parse_args()`: CLI オプション
   - `load_sound()`: 効果音ロード（既存関数を再利用可能）
   - `process_content()`: コンテンツ処理
   - `main()`: エントリポイント

3. **text_cleaner.py** (変更なし)
   - 新マーカー文字を自動的に保持

4. **voicevox_client.py** (変更なし)
   - 音声合成

## Quickstart

### 使用方法

```bash
# 基本使用法
python -m src.xml2_pipeline --input sample/book2.xml --output ./output

# chapter/section 別効果音（デフォルト）
python -m src.xml2_pipeline \
    --input sample/book2.xml \
    --chapter-sound assets/sounds/chapter.mp3 \
    --section-sound assets/sounds/section.mp3
```

### テスト実行

```bash
# 新パーサーテスト
make test TEST_PATH=tests/test_xml2_parser.py

# 新パイプラインテスト
make test TEST_PATH=tests/test_xml2_pipeline.py

# 全テスト
make test
```

---

## Next Steps

- Run `/speckit.tasks` to generate tasks.md with TDD workflow
