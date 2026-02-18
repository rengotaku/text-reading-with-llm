# Phase 3 Output: US2 - 見出し速度調整

**Date**: YYYY-MM-DD
**Status**: 完了 | エラー
**User Story**: US2 - 見出し速度調整

## 実行タスク

- [ ] T024 Read setup analysis
- [ ] T025 Read previous phase output
- [ ] T033 Read RED tests
- [ ] T034 Implement format_heading_text() in src/xml2_parser.py
- [ ] T035 Update parse_book2_xml() to handle heading elements with markers
- [ ] T036 Verify `make test` PASS (GREEN)
- [ ] T037 Verify all tests pass

## 変更ファイル一覧

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/xml2_parser.py | 修正 | format_heading_text() 追加、heading 処理拡張 |
| tests/test_xml2_parser.py | 修正 | heading 関連テスト追加 |

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

Phase 4 (US3 - 音声パイプライン統合) で実装するもの:
- `xml2_pipeline.py` 全体
- `parse_args()`, `load_sound()`, `process_content()`, `main()`
- 注意点: CHAPTER_MARKER/SECTION_MARKER での分割処理
