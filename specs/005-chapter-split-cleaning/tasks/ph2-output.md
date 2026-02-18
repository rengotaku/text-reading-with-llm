# Phase 2 Output: テキストクリーニングの適用

**Date**: 2026-02-18
**Status**: 完了
**User Story**: US1 - テキストクリーニングの適用

## 実行タスク

- [x] T013 Read RED tests: specs/005-chapter-split-cleaning/red-tests/ph2-test.md
- [x] T014 [US1] Update process_content() to call clean_page_text() in src/xml2_pipeline.py
- [x] T015 Verify `make test` PASS (GREEN)
- [x] T016 Verify `make test` passes all tests (no regressions)
- [x] T017 Edit and rename: specs/005-chapter-split-cleaning/tasks/ph2-output-template.md → ph2-output.md

## 変更ファイル一覧

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/xml2_pipeline.py | 修正 | process_content() に clean_page_text() 呼び出しを追加（L203） |
| tests/test_xml2_pipeline.py | 修正 | RED テストのモック修正（generate_audio のモック追加） |

## 実装内容

### src/xml2_pipeline.py

**変更箇所**: L196-203

マーカー除去後、TTS 生成前に `clean_page_text()` を呼び出すように修正:

```python
# マーカー除去
if text.startswith(CHAPTER_MARKER) and chapter_sound is not None:
    audio_segments.append(chapter_sound)
    text = text[len(CHAPTER_MARKER):]
elif text.startswith(SECTION_MARKER) and section_sound is not None:
    audio_segments.append(section_sound)
    text = text[len(SECTION_MARKER):]

# テキストクリーニング
text = text.strip()
if not text:
    continue

# clean_page_text() 適用（NEW）
text = clean_page_text(text)
```

### tests/test_xml2_pipeline.py

**変更箇所**: TestProcessContentAppliesCleanPageText クラスの3テスト

RED フェーズで作成されたテストに `generate_audio` のモックを追加:
- `test_process_content_calls_clean_page_text`
- `test_process_content_applies_clean_page_text_to_each_item`
- `test_process_content_cleans_text_after_marker_removal`

理由: 元のテストは `synthesizer.synthesize` をモックしていたが、実際には `generate_audio` 関数が `synthesizer.synthesize()` を呼び出して bytes を期待する。`generate_audio` を直接モックすることで正しく動作するようになった。

## テスト結果

```
PYTHONPATH=/data/projects/text-reading-with-llm .venv/bin/python -m pytest tests/ -v
============================= 413 passed in 0.81s ==============================
```

### Phase 2 固有テスト (9件)

```
tests/test_xml2_pipeline.py::TestProcessContentAppliesCleanPageText::test_process_content_calls_clean_page_text PASSED
tests/test_xml2_pipeline.py::TestProcessContentAppliesCleanPageText::test_process_content_applies_clean_page_text_to_each_item PASSED
tests/test_xml2_pipeline.py::TestProcessContentAppliesCleanPageText::test_process_content_cleans_text_after_marker_removal PASSED
tests/test_xml2_pipeline.py::TestProcessContentRemovesUrl::test_url_not_passed_to_tts PASSED
tests/test_xml2_pipeline.py::TestProcessContentRemovesUrl::test_http_url_removed PASSED
tests/test_xml2_pipeline.py::TestProcessContentRemovesParentheticalEnglish::test_parenthetical_english_removed PASSED
tests/test_xml2_pipeline.py::TestProcessContentRemovesParentheticalEnglish::test_multiple_parenthetical_english_removed PASSED
tests/test_xml2_pipeline.py::TestProcessContentConvertsNumbersToKana::test_numbers_converted_to_kana PASSED
tests/test_xml2_pipeline.py::TestProcessContentConvertsNumbersToKana::test_year_number_converted PASSED
```

**全テスト**: 413 passed (既存 404 + 新規 9)
**リグレッション**: なし（既存 404 テストすべて PASS）

## 発見した問題/課題

### 1. RED テストのモック設定不備

**問題**: RED フェーズで作成された `TestProcessContentAppliesCleanPageText` の3テストが `synthesizer.synthesize` のみをモックしており、`generate_audio` 関数が期待する bytes ではなく tuple を返していた。

**解決**: `generate_audio` 関数を直接モックすることで解決。テストインフラの修正であり、テストの意図や期待値は変更していない。

### 2. clean_page_text() の呼び出しタイミング

**確認事項**:
- ✅ マーカー除去後に呼び出す（マーカーは効果音挿入用、クリーニング対象外）
- ✅ `text.strip()` と空文字列チェックは維持
- ✅ TTS 生成前に適用
- ✅ 全 ContentItem に対して適用

## clean_page_text() の効果

実装により、以下のクリーニング処理が xml2_pipeline でも適用されるようになった:

| 機能 | 変換例 |
|------|--------|
| URL 除去 | `https://example.com` → （削除） |
| 括弧内英語除去 | `信頼性 (Reliability)` → `信頼性` |
| 数値カナ変換 | `123` → `ひゃくにじゅうさん` |
| ISBN 除去 | `ISBN 978-4-XXXX-XXXX-X` → （削除） |
| 句読点正規化 | `,` → `、`, `.` → `。` |
| 参照正規化 | `[1]`, `(p.123)` → （削除） |

## 次フェーズへの引き継ぎ

### Phase 3 (US2: チャプター単位の分割出力)

**前提条件**:
- ✅ clean_page_text() が process_content() で動作することを確認済み
- ✅ マーカー処理フローが確立（CHAPTER_MARKER / SECTION_MARKER）

**実装するもの**:
1. `ContentItem.chapter_number` フィールド追加（src/xml2_parser.py）
2. `parse_book2_xml()` で chapter 追跡ロジック追加
3. `sanitize_filename()` 関数実装（日本語タイトル→ファイル名変換）
4. `process_chapters()` 関数実装（chapter 単位での WAV 出力）
5. `main()` で `process_chapters()` 呼び出し

**注意点**:
- chapter_number はオプショナル（デフォルト None）にすること（後方互換性）
- chapter がない場合は従来通り book.wav のみ出力
- chapters/ ディレクトリは自動作成（mkdir with parents=True, exist_ok=True）
- サニタイズ: 半角英数字とアンダースコアのみ、最大20文字

**Phase 3 で流用可能な実装パターン**:
- `process_content()` の audio_segments 処理パターン（L182-226）
- `main()` の output_dir 生成パターン（L263-266）
