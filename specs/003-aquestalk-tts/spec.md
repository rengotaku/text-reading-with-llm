# Feature Specification: AquesTalk TTS 対応

**Feature Branch**: `003-aquestalk-tts`
**Created**: 2026-02-08
**Status**: Draft
**Input**: GitHub Issue #1 - AquesTalk 対応: XML から AquesTalk 音声生成

## User Scenarios & Testing *(mandatory)*

### User Story 1 - XML から AquesTalk 音声生成 (Priority: P1)

ユーザーは、既存の XML ブックファイルから AquesTalk を使用して音声ファイルを生成したい。VOICEVOX と同様に、コマンドラインから簡単に実行でき、ページ単位の WAV ファイルと結合済みの音声ファイルが出力される。

**Why this priority**: これがフィーチャーの核心機能であり、これなしでは AquesTalk 対応の意味がない。既存の xml_parser と text_cleaner を再利用することで、VOICEVOX 版と一貫した動作を保証する。

**Independent Test**: `python -m src.aquestalk_pipeline -i sample/book.xml` を実行し、音声ファイルが生成されることで単独テスト可能。

**Acceptance Scenarios**:

1. **Given** 有効な XML ブックファイルがある, **When** AquesTalk パイプラインを実行する, **Then** 各ページの WAV ファイルと結合済み book.wav が生成される
2. **Given** XML ファイルに複数ページが含まれる, **When** ページ範囲を指定して実行する, **Then** 指定範囲のみ音声生成される
3. **Given** 存在しない XML ファイルを指定, **When** パイプラインを実行する, **Then** 適切なエラーメッセージが表示される

---

### User Story 2 - 見出し効果音の挿入 (Priority: P2)

ユーザーは、見出し（heading）の前に効果音を挿入したい。VOICEVOX 版と同様に、--heading-sound オプションで音声ファイルを指定できる。

**Why this priority**: VOICEVOX 版との機能パリティを維持するために必要。ただし基本的な音声生成が動作しないと意味がないため P2。

**Independent Test**: `--heading-sound sample/heading-sound.mp3` オプション付きで実行し、見出し前に効果音が挿入されることで単独テスト可能。

**Acceptance Scenarios**:

1. **Given** 見出しを含む XML と効果音ファイル, **When** --heading-sound オプション付きで実行, **Then** 各見出しの前に効果音が挿入される
2. **Given** --heading-sound を指定しない, **When** パイプラインを実行, **Then** 効果音なしで音声生成される
3. **Given** 見出しを含む XML, **When** パイプラインを実行, **Then** 見出し部分がゆっくり（speed 80）読まれ、強調される

---

### User Story 3 - 音声パラメータの調整 (Priority: P3)

ユーザーは、読み上げ速度、声質、ピッチなどの音声パラメータを調整したい。AquesTalk10 の全パラメータに対応する。

**Why this priority**: 音声品質の微調整は基本機能が動作した後で行う拡張機能。

**Independent Test**: `--speed 150 --voice 100 --pitch 100` などのオプションで実行し、音声パラメータが反映されることで単独テスト可能。

**Acceptance Scenarios**:

1. **Given** XML ファイル, **When** --speed オプションで速度を指定, **Then** 指定した速度（50-300）で音声生成される
2. **Given** XML ファイル, **When** --voice オプションで声質を指定, **Then** 指定した声質（0-200）で音声生成される
3. **Given** XML ファイル, **When** --pitch オプションでピッチを指定, **Then** 指定したピッチ（50-200）で音声生成される
4. **Given** パラメータを指定しない, **When** パイプラインを実行, **Then** デフォルト値（speed=100, voice=100, pitch=100）で音声生成される

---

### Edge Cases

- XML ファイルが空または無効な形式の場合、適切なエラーメッセージを表示
- AquesTalk ライブラリが見つからない場合、セットアップ手順を案内するエラーを表示
- 効果音ファイルが見つからない場合、警告を表示して効果音なしで続行
- テキストに AquesTalk が対応していない文字が含まれる場合、適切に処理または警告
- 見出し・段落が既に句点で終わっている場合、句点を重複追加しない（「。。」回避）

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: システムは XML ファイルを解析し、AquesTalk で音声を生成できなければならない
- **FR-002**: システムは既存の xml_parser モジュールを使用して XML を解析しなければならない
- **FR-003**: システムは既存の text_cleaner モジュールを使用してテキストをクリーニングしなければならない
- **FR-004**: システムは HEADING_MARKER を認識し、見出し効果音を挿入できなければならない
- **FR-005**: システムはページ単位の WAV ファイルと結合済みの book.wav を出力しなければならない
- **FR-006**: システムは CLI からページ範囲（--start-page, --end-page）を指定できなければならない
- **FR-007**: システムは読み上げ速度（speed: 50-300）を CLI から調整できなければならない
- **FR-008**: システムは AquesTalk10 ライブラリを使用しなければならない
- **FR-012**: システムは声質（voice: 0-200）を CLI から調整できなければならない
- **FR-013**: システムはピッチ（pitch: 50-200）を CLI から調整できなければならない
- **FR-009**: システムは数値を AquesTalk の `<NUM>` タグ形式で読み上げなければならない
- **FR-010**: システムは見出し末・段落末に句点がない場合、自動で句点を追加しなければならない（ただし句点の連続「。。」は回避する）
- **FR-011**: システムは見出し（heading）をゆっくり読む（speed 80）ことで強調しなければならない

### Key Entities

- **AquesTalkSynthesizer**: AquesTalk による音声合成を担当するクラス。VoicevoxSynthesizer と同様のインターフェースを持つ
- **AudioSegment**: 音声データを表現。効果音と合成音声を結合する際に使用

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: ユーザーは1コマンドで XML から AquesTalk 音声を生成できる
- **SC-002**: 250ページの書籍を10分以内に音声変換できる
- **SC-003**: VOICEVOX 版と同等の出力構造（pages/ ディレクトリ、book.wav）を持つ
- **SC-004**: 既存の text_cleaner による読み変換（数字、略語等）が AquesTalk 音声にも適用される

## Assumptions

- AquesTalk10 ライブラリを使用する（別途導入が必要）
- AquesTalk の音声合成はローカルで実行される（ネットワーク不要）
- AquesTalk10 の出力サンプルレートは 16000Hz（効果音は 16000Hz にリサンプリング）
- AquesTalk 風記法（アクセント・強弱制御 `'` `_` `/` 等）は本フィーチャーのスコープ外とする
- VOICEVOX との切り替えは別コマンド（aquestalk_pipeline.py）で行う
- 数値読みは AquesTalk の `<NUM>` タグを使用（text_cleaner の数値変換は AquesTalk 用に置換）
- AquesTalk10 パラメータ: speed(50-300), voice(0-200), pitch(50-200) すべて対応

## Out of Scope

- AquesTalk 風記法（アクセント・強弱・イントネーション制御）
- VOICEVOX と AquesTalk の統合 CLI（別々のコマンドとして提供）

## Dependencies

- AquesTalk10: 株式会社アクエストの音声合成ライブラリ（別途導入）
- 既存モジュール: xml_parser, text_cleaner, pipeline（一部機能）

## Clarifications

### Session 2026-02-08

- Q: XML 記法と AquesTalk 記法で移行可能な機能は？ → A: 調査結果を [research.md](./research.md) に文書化。readAloud 属性 + 数値タグ `<NUM>` を対応。AquesTalk 固有のアクセント記法はスコープ外を維持。
- Q: 見出し・段落末のポーズ処理は？ → A: 見出し末 + 段落末（句点なし）に `。` を自動追加。ただし句点の連続「。。」は回避する。
- Q: AquesTalk の出力サンプルレートは？ → A: 8000Hz（AquesTalk pico 標準）。効果音は 8000Hz にリサンプリング。
- Q: 見出し（heading）を強調できないか？ → A: 見出しをゆっくり読む（speed 80）で強調感を出す。AquesTalk には直接的な音量・強調制御がないため、速度で代替。
- Q: どの AquesTalk バージョンを使用するか？ → A: AquesTalk10 を使用。speed, voice, pitch の全パラメータに対応。pyaquestalk (pico ベース) ではなく AquesTalk10 を別途導入。

## Related

- Issue #1: AquesTalk 対応: XML から AquesTalk 音声生成
- 002-xml-ttl-loader: VOICEVOX 版 XML パイプライン（参考実装）
- [research.md](./research.md): AquesTalk 記法調査レポート
