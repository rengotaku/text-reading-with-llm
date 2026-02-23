# 実装計画: XML パイプライン分割

**ブランチ**: `010-split-xml-pipeline` | **日付**: 2026-02-23 | **仕様**: [spec.md](./spec.md)
**入力**: GitHub Issue #14 - xml2_pipeline を分割し、Makefile から各ステップを個別実行可能にする

## サマリー

`xml2_pipeline.py` の処理を分割し、テキストクリーニングと TTS 生成を独立して実行可能にする。新規 CLI スクリプト `text_cleaner_cli.py` を作成し、`xml2_pipeline.py` に `--cleaned-text` オプションを追加する。Makefile に `clean-text` と `run` ターゲットを追加する。

## 技術コンテキスト

**言語/バージョン**: Python 3.10+
**主要依存関係**: xml.etree.ElementTree, fugashi/unidic-lite (既存)
**ストレージ**: ファイルベース（cleaned_text.txt, WAV ファイル）
**テスト**: pytest
**ターゲットプラットフォーム**: Linux
**プロジェクトタイプ**: single
**パフォーマンス目標**: テキストクリーニング 10 秒以内
**制約**: 既存の xml-tts コマンドとの後方互換性維持
**スケール/スコープ**: 単一プロジェクト、ローカル実行

## Constitution チェック

*Constitution ファイルが存在しないためスキップ*

## プロジェクト構成

### ドキュメント（このフィーチャー）

```text
specs/010-split-xml-pipeline/
├── spec.md              # 機能仕様
├── plan.md              # この計画ファイル
├── research.md          # Phase 0 出力
└── checklists/          # 品質チェックリスト
    └── requirements.md
```

### ソースコード（変更対象）

```text
src/
├── xml2_pipeline.py      # 変更: --cleaned-text オプション追加
└── text_cleaner_cli.py   # 新規: テキストクリーニング CLI

tests/
├── test_xml2_pipeline.py # 変更: 新オプションのテスト追加
└── test_text_cleaner_cli.py # 新規: CLI テスト

Makefile                  # 変更: clean-text, run ターゲット追加
```

**構成決定**: 既存の `src/` ディレクトリ構造を維持。新規 CLI は独立したモジュールとして追加。

## 複雑性追跡

| 違反 | 必要な理由 | より単純な代替案を却下した理由 |
|------|-----------|-------------------------------|
| なし | - | - |

---

## Phase 2: 実装フェーズ

### Phase 2.1 - テキストクリーニング CLI 作成 (P1)

**目的**: `make clean-text` で XML → cleaned_text.txt のみ生成

**変更ファイル**:
1. `src/text_cleaner_cli.py` (新規)
   - argparse で --input, --output オプション実装
   - xml2_pipeline.py の main() からテキストクリーニング部分を抽出
   - 出力ディレクトリはハッシュベースで生成（既存ロジック再利用）

2. `tests/test_text_cleaner_cli.py` (新規)
   - CLI 引数パースのテスト
   - XML → cleaned_text.txt 生成のテスト
   - エラーハンドリングのテスト

3. `Makefile` (変更)
   - `clean-text` ターゲット追加

**受け入れ基準**:
- `make clean-text INPUT=sample.xml` で cleaned_text.txt が生成される
- TTS 処理は実行されない
- 既存の xml-tts コマンドに影響しない

---

### Phase 2.2 - TTS パイプライン入力オプション追加 (P2)

**目的**: `make xml-tts` で既存の cleaned_text.txt から TTS 生成

**変更ファイル**:
1. `src/xml2_pipeline.py` (変更)
   - `--cleaned-text` オプション追加
   - 指定時は XML パース・テキストクリーニングをスキップ
   - cleaned_text.txt を直接読み込んで TTS 生成

2. `tests/test_xml2_pipeline.py` (変更)
   - --cleaned-text オプションのテスト追加
   - 既存テストが引き続き通過することを確認

3. `Makefile` (変更)
   - `xml-tts` ターゲットを更新（オプションで --cleaned-text 対応）

**受け入れ基準**:
- `make xml-tts` で既存の cleaned_text.txt から音声生成
- 既存の `make xml-tts INPUT=sample.xml` も動作維持（後方互換）
- cleaned_text.txt が存在しない場合は明確なエラー

---

### Phase 2.3 - 一括実行ターゲット追加 (P3)

**目的**: `make run` で全ステップを順次実行

**変更ファイル**:
1. `Makefile` (変更)
   - `run` ターゲット追加: gen-dict → clean-text → xml-tts の順次実行
   - 各ステップでエラー時は停止

**受け入れ基準**:
- `make run INPUT=sample.xml` で全ステップが順次実行
- 途中でエラー発生時は後続ステップ未実行
- `make help` で各ターゲットの説明が表示

---

## 依存関係

```
Phase 2.1 (clean-text CLI)
    ↓
Phase 2.2 (--cleaned-text オプション)
    ↓
Phase 2.3 (make run ターゲット)
```

## リスクと対策

| リスク | 影響度 | 対策 |
|--------|--------|------|
| ハッシュベースディレクトリ計算の重複 | 中 | dict_manager.py の get_content_hash を両方から呼び出す |
| 既存テストの破損 | 高 | 各 Phase で既存テスト実行を確認 |
| Makefile の変数展開エラー | 低 | 既存パターンに従う |
