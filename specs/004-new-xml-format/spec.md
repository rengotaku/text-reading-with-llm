# Feature Specification: 新XMLフォーマット対応

**Feature Branch**: `004-new-xml-format`
**Created**: 2026-02-17
**Status**: Draft
**Input**: User description: "xml-ttsを新しいフォーマットに対応させて。sample/book2.xml がそれです。"

## Clarifications

### Session 2026-02-17

- Q: TOC エントリの読み上げ形式 → A: TOC は無視（読み上げ対象外、抽出不要）
- Q: 見出しレベルと効果音 → A: レベル別に異なる効果音（chapter と section で別の音）
- Q: front-matter セクションの扱い → A: 読み上げ対象外（スキップ）
- Q: 見出しの読み上げ形式 → A: 自然な日本語形式（「第1章 ...」「第1.1節 ...」）
- Q: 効果音ファイルの保存場所 → A: `assets/sounds/` ディレクトリ（chapter.mp3, section.mp3）
- Q: 既存 book.xml との後方互換性 → A: 不要（book2.xml 専用パーサーとして実装）

## 背景

既存の xml_parser.py は `<page>` ベースの XML フォーマット（book.xml）を処理している。新しいフォーマット（book2.xml）は異なる構造を持つ：

| 項目 | 既存フォーマット（book.xml） | 新フォーマット（book2.xml） |
|------|------------------------------|------------------------------|
| 基本構造 | `<page number="N">` | `<toc>`, `<front-matter>`, コンテンツ要素 |
| ページ区切り | `<page>` 要素 | `<!-- page N -->` コメント |
| 読み上げ制御 | `readAloud` 属性 | `readAloud` 属性（同様） |
| 目次 | なし | `<toc>` に `<entry>` 要素（読み上げ対象外） |
| コンテンツ | `<content>` 内の各要素 | 直接の `<heading>`, `<paragraph>` 要素 |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 新XMLフォーマットの基本パース (Priority: P1)

ユーザーは新しい XML フォーマット（book2.xml）を xml_pipeline.py で処理し、音声ファイルを生成したい。

**Why this priority**: これが機能の核心であり、これがなければ新フォーマットは全く使用できない。

**Independent Test**: book2.xml を xml_pipeline.py に渡して音声ファイルが生成されることを確認。

**Acceptance Scenarios**:

1. **Given** book2.xml が存在する, **When** xml_pipeline.py で処理する, **Then** 各読み上げ対象要素のテキストが抽出される
2. **Given** `readAloud="true"` の `<paragraph>` 要素, **When** パースする, **Then** そのテキストが音声生成対象となる
3. **Given** `readAloud="false"` の `<heading>` 要素, **When** パースする, **Then** そのテキストはスキップされる
4. **Given** `<toc>` セクション, **When** パースする, **Then** 読み上げ対象から除外される
5. **Given** `<front-matter>` セクション, **When** パースする, **Then** 読み上げ対象から除外される

---

### User Story 2 - 見出し音効の適用 (Priority: P2)

ユーザーは `<heading>` 要素の前に見出し用効果音が挿入されることを期待する。chapter（level=1）と section（level=2）で異なる効果音を使用する。

**Why this priority**: 聴いている人が書籍の構造を把握しやすくするため。

**Independent Test**: heading 要素を含む book2.xml を処理し、レベルに応じた効果音マーカーが付与されることを確認。

**Acceptance Scenarios**:

1. **Given** `level="1"` の `<heading>` 要素（chapter）, **When** パースする, **Then** chapter 用効果音（assets/sounds/chapter.mp3）が挿入される
2. **Given** `level="2"` の `<heading>` 要素（section）, **When** パースする, **Then** section 用効果音（assets/sounds/section.mp3）が挿入される
3. **Given** 見出しテキスト, **When** 読み上げる, **Then** 「第N章 タイトル」「第N.N節 タイトル」形式で読み上げられる

---

### Edge Cases

- 空の `<paragraph>` 要素がある場合、スキップされる
- `readAloud` 属性がない要素は、デフォルトで読み上げ対象とする（既存動作との整合性）
- `<!-- page N -->` コメントは処理に影響しない（テキスト抽出には不要）
- 不正な XML 構造の場合、適切なエラーメッセージを表示する
- level=3 以上の見出しがある場合、section と同じ扱いとする
- 効果音ファイルが存在しない場合、警告を出力して効果音なしで続行する

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: システムは book2.xml フォーマットの `<paragraph>` 要素からテキストを抽出できなければならない
- **FR-002**: システムは book2.xml フォーマットの `<heading>` 要素からテキストを抽出し、レベルに応じたマーカーを付与しなければならない
- **FR-003**: システムは `readAloud` 属性に基づいて要素を読み上げ対象から除外できなければならない
- **FR-004**: システムは `<toc>` セクションを読み上げ対象から除外しなければならない
- **FR-005**: システムは `<front-matter>` セクションを読み上げ対象から除外しなければならない
- **FR-006**: ~~削除~~ *(後方互換性不要のため)*
- **FR-007**: システムは見出しを「第N章 タイトル」「第N.N節 タイトル」形式で読み上げなければならない
- **FR-008**: システムは chapter（level=1）に `assets/sounds/chapter.mp3` の効果音を適用しなければならない
- **FR-009**: システムは section（level=2以上）に `assets/sounds/section.mp3` の効果音を適用しなければならない

### Key Entities

- **XmlContent**: 読み上げ対象のコンテンツ単位（テキスト、タイプ、level）
- **HeadingMarker**: 見出しマーカー種別（CHAPTER_MARKER, SECTION_MARKER）
- **SoundAssets**: 効果音ファイル（assets/sounds/chapter.mp3, assets/sounds/section.mp3）

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: book2.xml を処理して、`<toc>` と `<front-matter>` 以外の `readAloud="true"` 要素からテキストが抽出される
- **SC-002**: ~~削除~~ *(後方互換性不要のため)*
- **SC-003**: 抽出されたテキストから音声ファイルが正常に生成される
- **SC-004**: chapter と section で異なる効果音が再生される
- **SC-005**: 見出しが「第N章」「第N.N節」形式で読み上げられる

## Assumptions

- このパーサーは book2.xml フォーマット専用（既存 book.xml は対象外）
- `readAloud` 属性のデフォルト値は `true`（属性がない場合は読み上げ対象）
- ページコメント（`<!-- page N -->`）は音声生成には影響しない
- `<list>` 要素は新フォーマットにも存在し、既存と同様に処理する
- level=3 以上の見出しは section と同じ効果音を使用する
- 効果音ファイルは `assets/sounds/` ディレクトリに配置される
