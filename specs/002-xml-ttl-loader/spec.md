# Feature Specification: XML から TTS へのローダー

**Feature Branch**: `002-xml-ttl-loader`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "sample/book.xml をTTLに読み込んでもらう。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - XML ファイルを TTS パイプラインに読み込む (Priority: P1)

ユーザーが書籍の XML ファイル（`book.xml`）を指定して、TTS パイプラインで音声を生成できるようにする。

**Why this priority**: これが本機能の中核であり、XML からテキストを抽出して TTS に渡せなければ何も始まらない。

**Independent Test**: `sample/book.xml` を入力として指定し、正しく音声ファイルが生成されることで確認できる。

**Acceptance Scenarios**:

1. **Given** `sample/book.xml` が存在する, **When** パイプラインを実行する, **Then** 各ページのテキストが抽出され音声ファイルが生成される
2. **Given** XML ファイルに `<content>` 要素が含まれる, **When** テキスト抽出を行う, **Then** `<paragraph>`, `<heading>`, `<list>` などの要素からテキストが抽出される
3. **Given** XML ファイルに `<pageAnnouncement>` 要素がある, **When** テキスト抽出を行う, **Then** ページ番号アナウンス（例：「1ページ」）も読み上げテキストに含まれる

---

### User Story 2 - 読み上げ不要な要素をスキップする (Priority: P2)

XML 内の `readAloud="false"` 属性や `<pageMetadata>` など、読み上げ不要とマークされた要素をスキップし、ユーザーに不要な情報を読み上げない。

**Why this priority**: 音声品質に直接影響する。不要な情報（ファイル名やページメタデータ）が読み上げられると聴取体験が悪化する。

**Independent Test**: `readAloud="false"` を含む要素がある XML を処理し、その内容が読み上げテキストに含まれないことを確認。

**Acceptance Scenarios**:

1. **Given** `<figure>` 要素に `readAloud="optional"` がある, **When** テキスト抽出を行う, **Then** `<description>` は抽出されるが、`<file readAloud="false">` の内容はスキップされる
2. **Given** `<pageMetadata readAloud="false">` がある, **When** テキスト抽出を行う, **Then** ページメタデータはスキップされる
3. **Given** コメント（`<!-- ... -->`）がある, **When** テキスト抽出を行う, **Then** コメントは無視される

---

### Edge Cases

- 空の `<content>` 要素がある場合 → スキップして次のページへ進む
- `<page>` 要素が存在しない不正な XML → エラーメッセージを表示して終了
- 文字エンコーディングが UTF-8 以外の場合 → UTF-8 として処理を試みる（本プロジェクトは UTF-8 前提）

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: システムは XML ファイル（`.xml`）を入力として受け付け、ページ単位でテキストを抽出できなければならない
- **FR-002**: システムは `<page>` 要素を識別し、各ページの `number` 属性を取得できなければならない
- **FR-003**: システムは `<content>` 要素内の `<paragraph>`, `<heading>`, `<list>`, `<item>` からテキストを抽出できなければならない
- **FR-004**: システムは `readAloud="false"` 属性を持つ要素をスキップしなければならない
- **FR-005**: システムは `<pageAnnouncement>` の内容をページ読み上げの先頭に含めなければならない
- **FR-006**: システムは `<figure>` 要素の `<description>` を抽出できなければならない（`readAloud` 属性に従う）
- **FR-007**: システムは抽出したテキストを既存のテキストクリーニング処理に渡せなければならない
- **FR-008**: システムは不正な XML 形式のファイルに対してわかりやすいエラーメッセージを表示しなければならない

### Key Entities

- **XmlPage**: XML の `<page>` 要素に対応する新規クラス。ページ番号、ソースファイル名、コンテンツを持つ。変換アダプタで既存 Page に変換
- **Content**: `<paragraph>`, `<heading>`, `<list>` などの読み上げ対象テキスト
- **Figure**: 画像とその説明。`readAloud` 属性で読み上げ制御

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `sample/book.xml` を入力として、全ページの音声ファイルが生成される
- **SC-002**: 抽出されたテキストに `readAloud="false"` 要素の内容が含まれない
- **SC-003**: 不正な XML ファイルに対して 1 秒以内にエラーメッセージが表示される

## Clarifications

### Session 2026-02-07

- Q: XML → TTS 統合方式は？ → A: 新規スクリプト（xml_pipeline.py）を作成し、独立した実行エントリポイントとする
- Q: 既存コンポーネントの再利用は？ → A: VoicevoxSynthesizer, text_cleaner, process_pages 等を再利用
- Q: Page オブジェクトの互換性は？ → A: 新規 XmlPage クラスを定義し、変換アダプタを実装
- Q: AquesTalk 風記法（アクセント・強弱制御）対応は？ → A: 将来対応としてスコープ外

## Out of Scope（将来対応）

- **AquesTalk 風記法対応**: アクセント・強弱・読み方の細かい制御（`'` `_` `/` 等の記号による制御）は本フィーチャーでは対応しない。VOICEVOX の自動推定 + 既存の読み辞書（`reading_dict.py`）で対応する

## Assumptions

- 入力は XML ファイルのみを前提とする（Markdown 対応は不要）
- 新規スクリプト `xml_pipeline.py` を作成する（既存 `pipeline.py` は変更しない）
- 既存コンポーネント（VoicevoxSynthesizer, text_cleaner, process_pages 等）を再利用する
- 新規 XmlPage クラスを定義し、変換アダプタで既存 Page に変換して process_pages() に渡す
- 入力 XML は UTF-8 エンコーディングであることを前提とする
- XML のルート要素は `<book>` であることを前提とする
- `<page>` 要素には必ず `number` 属性が存在することを前提とする
- 既存の TTS エンジン（VOICEVOX）との連携方式は変更しない
