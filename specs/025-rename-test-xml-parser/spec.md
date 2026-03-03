# 機能仕様書: XML関連ファイル名の統一

**フィーチャーブランチ**: `025-rename-test-xml-parser`
**作成日**: 2026-03-03
**ステータス**: Draft
**入力**: GitHub Issue #37 - refactor: rename test_xml2_parser.py to test_xml_parser.py（スコープ拡大）

## 概要

ファイル命名の一貫性を向上させるため、`xml2_` プレフィックスを持つすべてのソースファイルとテストファイルを `xml_` にリネームする。`xml2` という番号付けは歴史的経緯によるもので、現在は不要である。

## Clarifications

### Session 2026-03-03

- Q: どこまでリネームしますか？ → A: Option A - `xml2_parser` + `xml2_pipeline` + 全関連テスト（完全統一）

## ユーザーシナリオ & テスト *(必須)*

### ユーザーストーリー 1 - ソースファイル名の統一 (優先度: P1)

開発者として、一貫性のあるファイル命名規則に従ったソースファイルを持ちたい。これにより、モジュールを探しやすくなり、新しい開発者がプロジェクト構造を理解しやすくなる。

**この優先度の理由**: ソースファイルのリネームはインポート文の更新を伴い、最も影響範囲が大きいため最優先。

**独立テスト**: リネーム後に全テストを実行し、すべてが通過することで検証可能。

**受け入れシナリオ**:

1. **Given** `src/xml2_parser.py` が存在する状態で、**When** ファイルを `src/xml_parser.py` にリネームする、**Then** 旧ファイルは存在せず新ファイルが存在する
2. **Given** `src/xml2_pipeline.py` が存在する状態で、**When** ファイルを `src/xml_pipeline.py` にリネームする、**Then** 旧ファイルは存在せず新ファイルが存在する
3. **Given** リネーム完了後、**When** すべてのインポート文を更新する、**Then** インポートエラーが発生しない

---

### ユーザーストーリー 2 - テストファイル名の統一 (優先度: P2)

開発者として、ソースファイルと対応するテストファイルの命名規則が一致していることを期待する。

**この優先度の理由**: テストファイルのリネームはソースファイルに依存するため、P1の後に実施。

**独立テスト**: リネーム後にpytestを実行し、すべてのテストが検出・実行されることで検証可能。

**受け入れシナリオ**:

1. **Given** `tests/test_xml2_parser.py` が存在する状態で、**When** ファイルを `tests/test_xml_parser.py` にリネームする、**Then** 旧ファイルは存在せず新ファイルが存在する
2. **Given** `tests/test_xml2_pipeline_*.py` が存在する状態で、**When** ファイルを `tests/test_xml_pipeline_*.py` にリネームする、**Then** 旧ファイルは存在せず新ファイルが存在する
3. **Given** リネーム完了後、**When** `pytest` を実行する、**Then** すべてのテストが通過する

---

### エッジケース

- リネーム後にインポートエラーが発生した場合 → テスト実行で検出される
- 他のファイルから `xml2_parser` または `xml2_pipeline` を参照している場合 → grep/検索で確認し、すべて更新
- conftest.py などでインポートしている場合 → 同様に更新

## 要件 *(必須)*

### 機能要件

**ソースファイル**:
- **FR-001**: `src/xml2_parser.py` を `src/xml_parser.py` にリネームすること
- **FR-002**: `src/xml2_pipeline.py` を `src/xml_pipeline.py` にリネームすること

**テストファイル**:
- **FR-003**: `tests/test_xml2_parser.py` を `tests/test_xml_parser.py` にリネームすること
- **FR-004**: `tests/test_xml2_pipeline_args.py` を `tests/test_xml_pipeline_args.py` にリネームすること
- **FR-005**: `tests/test_xml2_pipeline_cleaned_text.py` を `tests/test_xml_pipeline_cleaned_text.py` にリネームすること
- **FR-006**: `tests/test_xml2_pipeline_integration.py` を `tests/test_xml_pipeline_integration.py` にリネームすること
- **FR-007**: `tests/test_xml2_pipeline_output.py` を `tests/test_xml_pipeline_output.py` にリネームすること
- **FR-008**: `tests/test_xml2_pipeline_processing.py` を `tests/test_xml_pipeline_processing.py` にリネームすること

**インポート更新**:
- **FR-009**: すべてのファイルで `from src.xml2_parser` を `from src.xml_parser` に更新すること
- **FR-010**: すべてのファイルで `from src.xml2_pipeline` を `from src.xml_pipeline` に更新すること
- **FR-011**: すべてのファイルで `import xml2_parser` を `import xml_parser` に更新すること
- **FR-012**: すべてのファイルで `import xml2_pipeline` を `import xml_pipeline` に更新すること

**品質保証**:
- **FR-013**: リネーム後、すべての既存テストが通過すること
- **FR-014**: テストカバレッジが低下しないこと
- **FR-015**: リネームはgit履歴で追跡可能であること（`git mv` を使用）

### スコープ外

- `specs/` 内のドキュメント更新（過去の記録として保持）
- キャッシュファイル（`.mypy_cache/`, `__pycache__/`）の手動削除（自動再生成される）

## 成功基準 *(必須)*

### 測定可能な成果

- **SC-001**: `xml2_` プレフィックスを持つソース/テストファイルが存在しない
- **SC-002**: `xml_` プレフィックスを持つ対応ファイルがすべて存在する
- **SC-003**: 全テストスイートが100%通過する
- **SC-004**: テストカバレッジがリネーム前と同等（±1%以内）
- **SC-005**: git履歴でファイルのリネームが追跡可能である
- **SC-006**: コード内に `xml2_parser` または `xml2_pipeline` への参照が残っていない（コメント・ドキュメント除く）

## 前提条件

- 対象ファイルがすべて現在存在すること
- CIパイプラインが正常に動作すること

## 影響範囲

| 変更前 | 変更後 |
|--------|--------|
| `src/xml2_parser.py` | `src/xml_parser.py` |
| `src/xml2_pipeline.py` | `src/xml_pipeline.py` |
| `tests/test_xml2_parser.py` | `tests/test_xml_parser.py` |
| `tests/test_xml2_pipeline_args.py` | `tests/test_xml_pipeline_args.py` |
| `tests/test_xml2_pipeline_cleaned_text.py` | `tests/test_xml_pipeline_cleaned_text.py` |
| `tests/test_xml2_pipeline_integration.py` | `tests/test_xml_pipeline_integration.py` |
| `tests/test_xml2_pipeline_output.py` | `tests/test_xml_pipeline_output.py` |
| `tests/test_xml2_pipeline_processing.py` | `tests/test_xml_pipeline_processing.py` |

## インポート更新対象ファイル

以下のファイルでインポート文の更新が必要：
- `tests/test_xml2_parser.py` (リネーム後: `test_xml_parser.py`)
- `tests/test_dict_integration.py`
- `tests/test_xml2_pipeline_*.py` (リネーム後: `test_xml_pipeline_*.py`)
- その他 `xml2_parser` または `xml2_pipeline` をインポートしているファイル
