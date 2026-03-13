# Phase 3 RED Tests: 長文セクションの分割処理

**Date**: 2026-03-14
**Status**: RED (FAIL verified)
**User Story**: US2 - 長文セクションの分割処理

## Summary

| Item | Value |
|------|-------|
| テスト作成数 | 47 |
| FAIL数 | 47 (全て ImportError) |
| テストファイル | tests/test_dialogue_converter.py |

## テストクラス構成

| クラス | タスク | テスト数 | 対象関数 |
|--------|--------|----------|----------|
| TestShouldSplit | T032 | 12 | should_split() |
| TestSplitByHeading | T033 | 15 | split_by_heading() |
| TestSplitContextContinuity | T034 | 6 | split_by_heading() + convert_section() |
| TestBoundaryCharacterCount | T035 | 14 | should_split() + split_by_heading() + convert_section() |

## 失敗テスト一覧

### T032: should_split() - 文字数判定関数 (12件)

| テストメソッド | 期待動作 |
|---------------|---------|
| test_should_split_returns_bool | bool値を返す |
| test_should_split_false_for_short_section | 3,500文字以下 → False |
| test_should_split_true_for_long_section | 4,001文字以上 → True |
| test_should_split_false_for_empty_section | 空セクション → False |
| test_should_split_false_for_single_short_paragraph | 短い段落1つ → False |
| test_should_split_true_for_5000_chars | 5,000文字 → True |
| test_should_split_true_for_10000_chars | 10,000文字 → True |
| test_should_split_counts_all_paragraphs | 全段落の文字数を合算して判定 |
| test_should_split_with_none_input | None入力のエラーハンドリング |
| test_should_split_exactly_4000_chars | 4,000文字境界値の判定 |
| test_should_split_with_unicode_content | Unicode文字の文字数カウント |
| test_should_split_with_special_characters | 特殊文字を含むセクション |

### T033: split_by_heading() - 見出し単位分割関数 (15件)

| テストメソッド | 期待動作 |
|---------------|---------|
| test_split_by_heading_returns_list | Sectionのリストを返す |
| test_split_by_heading_returns_section_objects | 各要素がSectionインスタンス |
| test_split_by_heading_preserves_section_number | セクション番号が保持される |
| test_split_by_heading_preserves_title | タイトル情報が保持される |
| test_split_by_heading_preserves_chapter_number | chapter_numberが保持される |
| test_split_by_heading_splits_at_heading_markers | ## で始まる行で分割 |
| test_split_by_heading_no_heading_returns_single | 見出しなしは1セクション |
| test_split_by_heading_empty_section | 空セクションの処理 |
| test_split_by_heading_preserves_all_paragraphs | 全段落が保持される |
| test_split_by_heading_with_none_input | None入力のエラーハンドリング |
| test_split_by_heading_each_part_under_4000 | 分割後は各パート4,000文字以下 |
| test_split_by_heading_multiple_headings | 複数見出しで適切に分割 |
| test_split_by_heading_with_large_data | 1,000段落以上の大規模データ |
| test_split_by_heading_with_empty_string_paragraphs | 空文字列段落を含む場合 |

### T034: 分割後の連続性テスト (6件)

| テストメソッド | 期待動作 |
|---------------|---------|
| test_split_sections_maintain_order | 分割後セクションの順序維持 |
| test_split_then_convert_produces_valid_results | 分割 → convert_section() で有効な結果 |
| test_split_sections_have_non_empty_paragraphs | 空セクションが生成されない |
| test_convert_section_with_split_sets_was_split_flag | was_split=True が設定される |
| test_split_preserves_content_no_data_loss | テキストの欠落なし |
| test_split_sections_can_each_generate_dialogue_xml | 各分割セクションからXML生成可能 |

### T035: 境界ケーステスト (14件)

| テストメソッド | 期待動作 |
|---------------|---------|
| test_boundary_3500_chars_no_split | 3,500文字 → False |
| test_boundary_3800_chars_no_split | 3,800文字 → False |
| test_boundary_3999_chars_no_split | 3,999文字 → False |
| test_boundary_4000_chars | 4,000文字（境界値） |
| test_boundary_4001_chars_split | 4,001文字 → True |
| test_boundary_4100_chars_split | 4,100文字 → True |
| test_boundary_4500_chars_split | 4,500文字 → True |
| test_boundary_0_chars_no_split | 0文字 → False |
| test_boundary_1_char_no_split | 1文字 → False |
| test_boundary_negative_char_count_handling | 空段落リスト → False |
| test_boundary_exactly_threshold_split_by_heading | 閾値付近の分割動作 |
| test_boundary_convert_section_short_no_split | 3,500文字 → was_split=False |
| test_boundary_convert_section_long_with_split | 4,500文字 → was_split=True |
| test_boundary_multiple_small_paragraphs_sum_over_threshold | 多数の短段落の合計判定 |
| test_boundary_single_huge_paragraph | 8,000文字の巨大単一段落 |

## 実装ヒント

- `should_split(section: Section) -> bool`: 全段落の文字数を合算し、4,000文字超ならTrue
- `split_by_heading(section: Section) -> list[Section]`: 段落内の `## ` で始まる行を見出しとして分割点に使用
- `convert_section()`: should_split()がTrueの場合にsplit_by_heading()を呼び出し、was_split=Trueを設定
- エッジケース: None入力、空セクション、見出しなしの長文、Unicode文字

## make test 出力（抜粋）

```
ERROR tests/test_dialogue_converter.py::TestShouldSplit::test_should_split_returns_bool - ImportError: should_split is not yet implemented
ERROR tests/test_dialogue_converter.py::TestShouldSplit::test_should_split_false_for_short_section - ImportError
ERROR tests/test_dialogue_converter.py::TestShouldSplit::test_should_split_true_for_long_section - ImportError
ERROR tests/test_dialogue_converter.py::TestSplitByHeading::test_split_by_heading_returns_list - ImportError
ERROR tests/test_dialogue_converter.py::TestSplitByHeading::test_split_by_heading_returns_section_objects - ImportError
ERROR tests/test_dialogue_converter.py::TestSplitContextContinuity::test_split_sections_maintain_order - ImportError
ERROR tests/test_dialogue_converter.py::TestSplitContextContinuity::test_convert_section_with_split_sets_was_split_flag - ImportError
ERROR tests/test_dialogue_converter.py::TestBoundaryCharacterCount::test_boundary_3500_chars_no_split - ImportError
ERROR tests/test_dialogue_converter.py::TestBoundaryCharacterCount::test_boundary_4001_chars_split - ImportError
ERROR tests/test_dialogue_converter.py::TestBoundaryCharacterCount::test_boundary_convert_section_long_with_split - ImportError
...
======================== 663 passed, 47 errors in 4.26s ========================
```
