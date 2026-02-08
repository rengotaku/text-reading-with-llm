# Research: doc-clean-tts-replace

**Date**: 2026-02-06
**Branch**: `001-doc-clean-tts-replace`

## 1. 既存アーキテクチャ分析

### 処理パイプライン (text_cleaner.py:66-128)

```
clean_page_text()
├── Markdown クリーニング (HTML comments, figures, headings, etc.)
├── normalize_punctuation()     # ← FR-011,012,013 はここに追加
├── normalize_numbers()
├── apply_reading_rules()
├── apply_llm_readings()
└── convert_to_kana()
```

**Decision**: 新規変換ルールは `normalize_punctuation()` の前後に追加し、処理順序を維持する。

### punctuation_normalizer.py の構造

- ルールベースの正規表現処理
- `_normalize_line()` で行単位の変換
- 定数パターン (RENTAI_PATTERNS, ADVERB_PATTERNS, etc.)

**Decision**: FR-011 (「ではありません」除外) は `_normalize_line()` のルール4改良で対応。

## 2. 機能別設計決定

### FR-001,002,003: URL処理

**候補案**:
1. text_cleaner.py に専用関数を追加
2. punctuation_normalizer.py に統合
3. 新規モジュール (url_cleaner.py)

**Decision**: `text_cleaner.py` に専用関数 `_clean_urls()` を追加。
**Rationale**: URL処理はMarkdownクリーニングの一部であり、text_cleaner.py のスコープに適切。

**実装順序**: normalize_punctuation() の前に配置（URL内のコロンがコロン変換の影響を受けないため）

### FR-004,005,006: 図表・注釈参照

**Decision**: `text_cleaner.py` に `_normalize_references()` を追加。
**Rationale**: 参照の正規化はクリーニングの一部。

**パターン**:
- 図X.Y → `図(\d+)[\.．](\d+)` → 読み仮名変換
- 表X.Y → `表(\d+)[\.．](\d+)` → 読み仮名変換
- 注X.Y → `注(\d+)[\.．](\d+)` → 読み仮名変換

### FR-007: ISBN処理

**Decision**: `text_cleaner.py` に `_clean_isbn()` を追加。
**Pattern**: `ISBN[\s-]?[\d-]{10,17}` → 削除または「ISBN省略」

### FR-010: 括弧付き英語表記除去

**Decision**: `text_cleaner.py` に `_clean_parenthetical_english()` を追加。
**Pattern**: `([ぁ-んァ-ヶ一-龯]+)（([A-Za-z\s]+)）` → キャプチャグループ1のみ残す

**注意**: 括弧内が日本語の場合は保持（例: API（アプリケーション...））

### FR-011: 読点挿入除外パターン

**Decision**: `punctuation_normalizer.py` の `_normalize_line()` を修正。

**除外パターン** (負の先読み):
- `ではありません`
- `ではない`
- `にはならない`
- `とはいえない`
- `ではなく`

**実装**: ルール4の正規表現を修正し、除外パターンをネガティブルックアヘッドで追加。

### FR-012: コロン変換

**Decision**: `punctuation_normalizer.py` に新ルールを追加。

**変換対象**: 全角`：`、半角`:`
**変換結果**: `は、`
**除外条件**:
- URL内 (`://`)
- 数字:数字 (`\d:\d`)

**実装順序**: URL処理後に適用（URL内コロンは既に除去済み）

### FR-013: 鉤括弧変換

**Decision**: `punctuation_normalizer.py` に新ルールを追加。
**変換**: `「` → `、` / `」` → `、`

## 3. 処理順序決定

```
clean_page_text()
├── 1. Markdown基本クリーニング (既存)
├── 2. _clean_urls()           # NEW: FR-001,002,003
├── 3. _clean_isbn()           # NEW: FR-007
├── 4. _clean_parenthetical_english()  # NEW: FR-010
├── 5. _normalize_references()  # NEW: FR-004,005,006
├── 6. normalize_punctuation()  # MODIFIED: FR-011,012,013
│   ├── _normalize_colons()     # NEW
│   ├── _normalize_brackets()   # NEW
│   └── _normalize_line()       # MODIFIED: 除外パターン追加
├── 7. normalize_numbers() (既存)
├── 8. apply_reading_rules() (既存)
├── 9. apply_llm_readings() (既存)
└── 10. convert_to_kana() (既存)
```

## 4. テスト戦略

**Approach**: 各変換関数に対して単体テスト + 統合テスト

**テストファイル構成**:
```
tests/
├── test_url_cleaning.py       # FR-001,002,003
├── test_reference_normalization.py  # FR-004,005,006
├── test_isbn_cleaning.py      # FR-007
├── test_parenthetical_cleaning.py   # FR-010
├── test_punctuation_rules.py  # FR-011,012,013
└── test_integration.py        # 全体統合テスト
```

## 5. パフォーマンス考慮

**SC-006要件**: 処理時間10%以内増加

**対策**:
- 正規表現のプリコンパイル
- 変換順序の最適化（頻度の高いパターンを先に）
- 不要な文字列コピーの削減

## 6. 冪等性保証 (FR-009)

**課題**: 同じ入力に対して同じ出力

**対策**:
- 鉤括弧変換: 連続する読点を単一化
- コロン変換: 既に「は、」になっている場合はスキップ
- URL処理: 処理済みマーカーは不要（URLパターンは一意）
