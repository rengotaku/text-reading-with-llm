# Feature Specification: チャプター分割とクリーニング

**Feature Branch**: `005-chapter-split-cleaning`
**Created**: 2026-02-18
**Status**: Draft
**Input**: User description: "チャプター分割とクリーニング"

## 背景

004-new-xml-format で作成した xml2_pipeline には、既存の xml_pipeline が持つ重要な機能が欠落している：

| 機能 | xml_pipeline | xml2_pipeline (現状) |
|------|-------------|---------------------|
| テキストクリーニング | ✅ `clean_page_text()` | ❌ import のみ、未使用 |
| 分割出力 | ✅ `pages/page_NNNN.wav` | ❌ `book.wav` のみ |
| cleaned_text.txt | ✅ クリーニング済み | ❌ 生テキスト |

xml2_pipeline に既存パイプラインの機能を統合し、chapter 単位での分割出力とテキストクリーニングを実装する。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - テキストクリーニングの適用 (Priority: P1)

ユーザーは xml2_pipeline で処理した音声が、既存パイプラインと同等の品質（URL除去、カナ変換、辞書適用等）で読み上げられることを期待する。

**Why this priority**: テキストクリーニングなしでは、URLや英語括弧が読み上げられ、音声品質が著しく低下する。

**Independent Test**: book2.xml を処理し、生成された音声がクリーニング済みテキストに基づいていることを確認。

**Acceptance Scenarios**:

1. **Given** URL を含む paragraph 要素, **When** xml2_pipeline で処理する, **Then** URL は読み上げられない
2. **Given** 括弧内英語 (English) を含むテキスト, **When** 処理する, **Then** 括弧内英語は読み上げられない
3. **Given** ISBN を含むテキスト, **When** 処理する, **Then** ISBN は読み上げられない
4. **Given** 「図1.2」のような参照, **When** 処理する, **Then** 「ず1の2」と読み上げられる
5. **Given** 数字「123」を含むテキスト, **When** 処理する, **Then** 「ひゃくにじゅうさん」と読み上げられる
6. **Given** 漢字を含むテキスト, **When** 処理する, **Then** カナに変換されて読み上げられる

---

### User Story 2 - チャプター単位の分割出力 (Priority: P2)

ユーザーは xml2_pipeline の出力が chapter（章）単位で分割されたWAVファイルとして保存されることを期待する。

**Why this priority**: 長い書籍を一括で出力すると、特定の章だけ聴き直すことができない。分割により利便性が向上する。

**Independent Test**: 複数 chapter を含む book2.xml を処理し、chapters/ ディレクトリに chapter 毎のWAVが出力されることを確認。

**Acceptance Scenarios**:

1. **Given** 3つの chapter を含む book2.xml, **When** xml2_pipeline で処理する, **Then** `chapters/` ディレクトリに3つのWAVファイルが生成される
2. **Given** chapter 要素, **When** 処理する, **Then** `ch{NN}_{title}.wav` 形式でファイル名が付与される
3. **Given** 複数の chapter, **When** 処理する, **Then** 全 chapter を結合した `book.wav` も生成される
4. **Given** chapter 内に section がある, **When** 処理する, **Then** section は所属する chapter のWAVに含まれる

---

### User Story 3 - cleaned_text.txt の品質向上 (Priority: P3)

ユーザーは cleaned_text.txt にクリーニング済みのテキストが出力され、実際の読み上げ内容を確認できることを期待する。

**Why this priority**: デバッグや確認のために、実際に読み上げられるテキストを確認できる必要がある。

**Independent Test**: book2.xml を処理し、cleaned_text.txt に clean_page_text() 適用済みテキストが出力されることを確認。

**Acceptance Scenarios**:

1. **Given** book2.xml を処理, **When** cleaned_text.txt を確認する, **Then** URLや括弧英語が除去されている
2. **Given** 見出し要素, **When** cleaned_text.txt を確認する, **Then** 「第N章」「第N.N節」形式で整形されている
3. **Given** 数字や漢字を含むテキスト, **When** cleaned_text.txt を確認する, **Then** カナに変換されている

---

### Edge Cases

- chapter を含まない book2.xml の場合、全コンテンツを `book.wav` として出力する
- chapter タイトルが空の場合、`ch{NN}_untitled.wav` として出力する
- chapter タイトルにファイル名として使用できない文字が含まれる場合、サニタイズする
- クリーニング後にテキストが空になった場合、その要素はスキップする

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: システムは xml2_pipeline で処理する全テキストに `clean_page_text()` を適用しなければならない
- **FR-002**: システムは chapter 要素ごとに個別の WAV ファイルを `chapters/` ディレクトリに出力しなければならない
- **FR-003**: システムは chapter ファイル名を `ch{NN}_{sanitized_title}.wav` 形式で生成しなければならない
- **FR-004**: システムは全 chapter を結合した `book.wav` も出力しなければならない
- **FR-005**: システムは cleaned_text.txt にクリーニング済みテキストを出力しなければならない
- **FR-006**: システムは URL、括弧内英語、ISBN をテキストから除去しなければならない
- **FR-007**: システムは数字をカナ読みに変換しなければならない
- **FR-008**: システムは漢字をカナに変換しなければならない
- **FR-009**: システムは chapter のない XML を処理した場合、全コンテンツを `book.wav` として出力しなければならない

### Key Entities

- **ContentItem**: 読み上げ対象のコンテンツ単位（既存：text, item_type, heading_info）
  - **追加属性**: chapter_number（所属章番号、null の場合は章なし）
- **ChapterInfo**: 章情報（number, title, sanitized_filename）

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: book2.xml を処理して生成された音声に URL や括弧英語が含まれていない
- **SC-002**: 3 chapter の book2.xml を処理すると、3つの個別WAVファイルが `chapters/` に生成される
- **SC-003**: cleaned_text.txt の内容が `clean_page_text()` 適用後のテキストと一致する
- **SC-004**: 既存の xml_pipeline と同等のテキストクリーニングが適用される

## Assumptions

- 既存の `clean_page_text()` 関数は変更せずに再利用する
- chapter 要素は book2.xml のルート直下に存在する
- chapter 番号は XML の `number` 属性から取得する
- ファイル名のサニタイズは半角英数字とアンダースコアのみ許可する
- 効果音は既存の実装（chapter_sound, section_sound）をそのまま使用する
