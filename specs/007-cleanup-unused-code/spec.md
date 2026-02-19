# Feature Specification: 不要機能の削除リファクタリング

**Feature Branch**: `007-cleanup-unused-code`
**Created**: 2026-02-19
**Status**: Draft
**Input**: GitHub Issue #5 - リファクタリング: 不用な機能を洗い出して削除する

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 不要なソースコードの削除 (Priority: P1)

開発者として、現在使用していないソースコードモジュールを削除して、コードベースの見通しを良くし、保守コストを下げたい。

現在のプロジェクトでは `xml-tts` の `xml2` パイプラインのみを使用している。旧形式のXMLパイプライン、AquesTalk連携、旧テキストパイプラインなど、使われていないモジュールが残っており、これらを安全に削除する。

**Why this priority**: 不要コードの存在はコードベースの理解を妨げ、依存関係の管理を複雑にする。最も直接的な改善効果がある。

**Independent Test**: 削除後に既存の xml2 パイプライン関連テストが全てパスし、`make xml-tts PARSER=xml2` が正常動作することで検証できる。

**Acceptance Scenarios**:

1. **Given** 現在使用していないソースモジュールが存在する, **When** 不要モジュールを削除する, **Then** xml2 パイプライン関連の全テストがパスする
2. **Given** 不要モジュールを削除済み, **When** `make xml-tts PARSER=xml2` を実行する, **Then** 正常にTTS生成が完了する
3. **Given** 不要モジュールを削除済み, **When** `make gen-dict` を実行する, **Then** 正常に辞書生成が完了する

---

### User Story 2 - 不要テストコードの削除 (Priority: P2)

開発者として、削除したモジュールに対応するテストコードも削除して、テストスイートを整理したい。

**Why this priority**: ソースコード削除後、対応テストがなくなったテストファイルは不要になる。テスト実行の高速化とテストスイートの明確化に貢献する。

**Independent Test**: テストスイート全体を実行し、削除対象外のテストが全てパスし、テスト対象のないテストファイルが残っていないことで検証できる。

**Acceptance Scenarios**:

1. **Given** 不要モジュールが削除されている, **When** 対応するテストファイルを削除する, **Then** 残りのテストスイートが全てパスする
2. **Given** テストファイルを整理済み, **When** `make test` を実行する, **Then** エラーなくテストが完了する

---

### User Story 3 - Makefile・設定ファイルの整理 (Priority: P3)

開発者として、削除したモジュールに関連する Makefile ターゲットや設定を整理して、ビルドシステムをシンプルにしたい。

**Why this priority**: 使用しないビルドターゲットの存在は混乱を招く。ソースとテストの削除後に整合性を取る必要がある。

**Independent Test**: `make help` で表示されるターゲットが全て実行可能であり、不要なターゲットが表示されないことで検証できる。

**Acceptance Scenarios**:

1. **Given** 不要モジュールが削除されている, **When** 関連する Makefile ターゲットを削除・修正する, **Then** `make help` に不要なターゲットが表示されない
2. **Given** Makefile を整理済み, **When** 残りの全ターゲットを実行する, **Then** 各ターゲットが正常に動作する

### Edge Cases

- 削除対象モジュールが他の使用中モジュールから参照されていた場合はどうするか？→ 削除前に参照関係を調査し、参照がある場合はその参照も修正する
- `__pycache__` に残るキャッシュファイルはどうするか？→ 対応する `.pyc` ファイルも合わせて削除する

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 現在使用していないソースモジュールを特定し、一覧化できること
- **FR-002**: 不要モジュールの削除後、xml2 パイプライン（`src/xml2_pipeline.py`, `src/xml2_parser.py`）が正常に動作すること
- **FR-003**: 不要モジュールの削除後、辞書管理機能（`src/dict_manager.py`, `src/generate_reading_dict.py`, `src/llm_reading_generator.py`）が正常に動作すること
- **FR-004**: 不要モジュールの削除後、テキスト前処理機能（`src/text_cleaner.py`, `src/punctuation_normalizer.py`, `src/number_normalizer.py`）が正常に動作すること
- **FR-005**: 削除対象モジュールに対応するテストファイルも合わせて削除すること
- **FR-006**: Makefile の不要ターゲット（旧パイプライン関連）を削除・修正すること
- **FR-007**: 削除後の全テストが成功すること

### 削除候補モジュール（調査結果に基づく暫定リスト）

現在 `xml-tts xml2` のみ使用しているという前提で、以下が削除候補：

**ソースファイル**:
- `src/xml_pipeline.py` - 旧XMLパイプライン（xml2 に置き換え済み）
- `src/xml_parser.py` - 旧XMLパーサー（xml2_parser に置き換え済み）
- `src/aquestalk_client.py` - AquesTalk クライアント（未使用）
- `src/aquestalk_pipeline.py` - AquesTalk パイプライン（未使用）
- `src/pipeline.py` - 旧テキストパイプライン（xml2_pipeline に置き換え済み）
- `src/tts_generator.py` - 旧TTS生成（xml2_pipeline に統合済みの可能性）
- `src/voicevox_client.py` - VOICEVOX クライアント（xml2_pipeline から使用されている可能性あり、要調査）
- `src/reading_dict.py` - 旧辞書機能（dict_manager に置き換え済みの可能性）
- `src/toc_extractor.py` - 目次抽出（Makefile の `toc` ターゲットで使用、要調査）
- `src/organize_chapters.py` - チャプター整理（Makefile の `organize` ターゲットで使用、要調査）
- `src/mecab_reader.py` - MeCab読み取り（text_cleaner から使用されている可能性あり、要調査）
- `src/progress.py` - プログレスバー（他モジュールから使用されている可能性あり、要調査）
- `src/test_tts_normalize.py` - src 内のテストファイル（tests/ に移動済みの可能性）

**テストファイル**:
- `tests/test_xml_pipeline.py` - 旧XMLパイプラインのテスト
- `tests/test_xml_parser.py` - 旧XMLパーサーのテスト
- `tests/test_aquestalk_client.py` - AquesTalk のテスト
- `tests/test_aquestalk_pipeline.py` - AquesTalk パイプラインのテスト

**Makefile ターゲット**:
- `run` / `run-simple` - 旧テキストパイプライン用ターゲット
- `xml-tts` の `xml` 分岐 - 旧XMLパイプライン用
- `toc` - 目次抽出（使用状況要確認）
- `organize` - チャプター整理（使用状況要確認）

### Key Entities

- **xml2パイプライン**: 現在唯一使用されているTTSパイプライン。`xml2_pipeline.py` + `xml2_parser.py` で構成
- **辞書管理**: `dict_manager.py` + `generate_reading_dict.py` + `llm_reading_generator.py` で構成される読み辞書機能
- **テキスト前処理**: `text_cleaner.py` + `punctuation_normalizer.py` + `number_normalizer.py` で構成

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 削除後のソースファイル数が削除前より少なくとも5ファイル減少する
- **SC-002**: 削除後の全テストが100%パスする
- **SC-003**: `make xml-tts PARSER=xml2` が削除前と同一の動作結果を返す
- **SC-004**: `make gen-dict` が削除前と同一の動作結果を返す
- **SC-005**: Makefile の `make help` に表示される全ターゲットが実行可能である

## Assumptions

- 「xml-tts の xml2 のみ利用」という前提に基づき、旧XMLパイプライン・AquesTalkパイプライン・旧テキストパイプラインは不要と判断
- `voicevox_client.py`、`mecab_reader.py`、`progress.py` は xml2 パイプラインから間接的に使用されている可能性があり、実装フェーズで依存関係を精査する
- `toc_extractor.py` と `organize_chapters.py` は Makefile から参照されているが、ユーザーが使用しているかは実装フェーズで確認する
- 削除は Git で管理されているため、必要に応じて復元可能
