# Research: 新XMLフォーマット対応

**Branch**: `004-new-xml-format` | **Date**: 2026-02-17

## R1: 新 XML フォーマット構造分析

### Findings

book2.xml（sample/book2.xml、約620KB）を分析：

```xml
<book>
    <metadata><title>Converted Book</title></metadata>
    <toc begin="17" end="20">
        <entry level="1" number="1" title="「企画」で失敗" />
        <entry level="2" number="1.1" title="なんでもできる..." />
        ...
    </toc>
    <front-matter>
        <!-- page comments -->
        <paragraph readAloud="true">...</paragraph>
        <heading level="2" readAloud="true">...</heading>
        ...
    </front-matter>
    <!-- Main content starts here -->
    <heading level="1" readAloud="true">第1章 タイトル</heading>
    <paragraph readAloud="true">本文...</paragraph>
    <list><item>リスト項目</item></list>
    ...
</book>
```

**Decision**: 以下の要素をスキップ
- `<toc>` セクション全体
- `<front-matter>` セクション全体
- `<metadata>` セクション

**Rationale**: 仕様で明確に読み上げ対象外と指定。

---

## R2: 見出しマーカー設計

**Decision**: 新マーカー定数を使用
- `CHAPTER_MARKER` (\uE001) → chapter（level=1）
- `SECTION_MARKER` (\uE002) → section（level=2+）

**Rationale**: Unicode Private Use Area 文字を使用。text_cleaner は特殊文字を保持する設計。

---

## R3: 見出し読み上げ形式

**Decision**: 見出しテキストを以下の形式に変換
- level=1: `第{number}章 {title}` （例: 第1章 「企画」で失敗）
- level=2+: `第{number}節 {title}` （例: 第1.1節 なんでもできる...）

**Rationale**: 仕様で明確に指定された形式。

---

## R4: 効果音設計

**Decision**: 2 種類の効果音を CLI オプションで指定
- `--chapter-sound` （デフォルト: `assets/sounds/chapter.mp3`）
- `--section-sound` （デフォルト: `assets/sounds/section.mp3`）

**Rationale**: シンプルな設計。後方互換性不要のため、既存オプションとの整合を考慮不要。

---

## 未解決事項

なし
