# Phase 2 Output: US1 - 基本パース

**Date**: YYYY-MM-DD
**Status**: 完了 | エラー
**User Story**: US1 - 新XMLフォーマットの基本パース

## 実行タスク

- [ ] T007 Read previous phase output
- [ ] T016 Read RED tests
- [ ] T017 Create dataclasses HeadingInfo, ContentItem in src/xml2_parser.py
- [ ] T018 Create constants CHAPTER_MARKER, SECTION_MARKER in src/xml2_parser.py
- [ ] T019 Implement parse_book2_xml() in src/xml2_parser.py
- [ ] T020 Implement _should_read_aloud() helper in src/xml2_parser.py
- [ ] T021 Verify `make test` PASS (GREEN)
- [ ] T022 Verify all tests pass

## 変更ファイル一覧

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/xml2_parser.py | 新規 | book2.xml パーサー |
| tests/test_xml2_parser.py | 新規 | パーサーテスト |
| tests/fixtures/sample_book2.xml | 新規 | テストフィクスチャ |

## テスト結果

```
make test 出力 (抜粋)
...
X passed, 0 failed
```

**カバレッジ**: XX% (目標: 80%)

## 発見した問題/課題

1. **[Issue]**: [description] → [resolution or deferred to Phase N]

## 次フェーズへの引き継ぎ

Phase 3 (US2 - 見出し速度調整) で実装するもの:
- `format_heading_text()`: 「第N章」「第N.N節」形式
- `parse_book2_xml()` の heading 処理を拡張
- 注意点: heading.number 属性の取得方法確認
