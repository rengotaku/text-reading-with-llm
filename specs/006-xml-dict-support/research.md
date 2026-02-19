# Research: 読み辞書生成のXMLファイル対応

**Branch**: `006-xml-dict-support` | **Date**: 2026-02-18

## R-001: XMLテキスト抽出方式

**Decision**: `parse_book2_xml()` を使って `ContentItem` リストを取得し、`chapter_number` でグループ化してからテキスト結合 → 用語抽出する

**Rationale**:
- `parse_book2_xml()` は既にチャプター番号を `ContentItem.chapter_number` に格納している
- チャプター単位のグループ化により、Markdownの `split_into_pages()` と同様の処理粒度を実現できる
- `extract_technical_terms()` はプレーンテキストを受け取る関数なので、ContentItemのテキストを結合して渡すだけでよい

**Alternatives considered**:
- A: テキスト全結合 → `split_into_pages()` 経由: Markdown固有のページマーカー（`--- Page N ---`）に依存するため不適切
- B: ContentItem毎に個別に用語抽出: 粒度が細かすぎ、重複排除が非効率

## R-002: ハッシュベース辞書保存のXML対応

**Decision**: 既存の `dict_manager.py` の `save_dict()` / `load_dict()` をそのまま使用する

**Rationale**:
- `save_dict(readings, input_path)` は `input_path.read_text()` でコンテンツハッシュを計算して `data/{hash}/readings.json` に保存
- XMLファイルでも `read_text()` は正常に動作する（XMLの生テキストがハッシュ元になる）
- 辞書の保存形式（JSON）は入力形式に依存しない

**Alternatives considered**: なし（既存の仕組みがそのまま適用可能）

## R-003: 拡張子判別とエラーハンドリング

**Decision**: `main()` 内で `input_path.suffix` をチェックし、`.xml` / `.md` で分岐、それ以外はエラー終了

**Rationale**:
- シンプルな拡張子ベースの判別で十分（MIMEタイプ等は不要）
- `xml2_parser.parse_book2_xml()` は `FileNotFoundError` と `ET.ParseError` を適切にraiseする
- 既存のエラーハンドリングパターン（`logger.error` + `sys.exit(1)`）に合わせる

**Alternatives considered**:
- ファイル内容のマジックバイト判定: 過剰な複雑さ
- 設定ファイルでの形式指定: YAGNI

## R-004: テストアプローチ

**Decision**: `tests/test_generate_reading_dict.py` を新規作成し、XML入力のユニットテストを追加

**Rationale**:
- 既存の `test_xml2_parser.py` がパーサー側のテストをカバー
- 辞書生成のXML対応は `main()` 関数内の分岐ロジックが主な変更点
- テスト用XMLフィクスチャは `tests/fixtures/` に配置
