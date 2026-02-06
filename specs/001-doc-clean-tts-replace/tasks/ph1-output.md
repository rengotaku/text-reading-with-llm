# Phase 1 Output: Setup

**Completed**: 2026-02-06
**Tasks**: T001-T005

## Existing Code Analysis

### src/text_cleaner.py (170 lines)

**Key Functions**:
- `clean_page_text()`: Main pipeline (lines 66-128)
  - HTML comment removal
  - Figure description removal
  - Page number markers removal
  - Markdown formatting cleanup
  - List conversion
  - Code block removal
  - TTS normalization chain: punctuation → numbers → reading rules → LLM dict → MeCab

**Current Processing Order**:
1. `normalize_punctuation()` - 読点挿入
2. `normalize_numbers()` - 数字正規化
3. `apply_reading_rules()` - 読み辞書適用
4. `apply_llm_readings()` - LLM辞書適用
5. `convert_to_kana()` - MeCab変換

**Integration Points for New Features**:
- URL/ISBN/括弧処理: `clean_page_text()` 先頭部分（markdown処理後、punctuation前）
- 参照正規化: `normalize_numbers()` と同時期
- コロン/鉤括弧/読点除外: `punctuation_normalizer.py` 内

### src/punctuation_normalizer.py (195 lines)

**Key Functions**:
- `normalize_punctuation()`: Entry point (lines 63-82)
- `_normalize_line()`: Rule application (lines 85-129)

**Current Rules**:
1. 連体修飾句パターン後の読点 (RENTAI_PATTERNS)
2. 副詞句パターン後の読点 (ADVERB_PATTERNS)
3. 接続パターン後の読点 (CONJUNCTION_PATTERNS)
4. 「は」の後の読点 (6文字以上の prefix 後)

**Integration Points for New Features**:
- US6: Rule 4 に negative lookahead 追加
- US7: `_normalize_colons()` 新規関数
- US8: `_normalize_brackets()` 新規関数

### tests/ Directory

- **Status**: Empty (no existing tests)
- **Action**: All tests are new implementation

## Environment Verification

```
pytest: 9.0.2 ✅
Python: 3.13.11 ✅
venv: active ✅
make test: runs (0 items collected) ✅
```

## Implementation Strategy

### text_cleaner.py Changes

新規関数追加位置 (clean_page_text 内):
```python
# After markdown cleanup, before punctuation normalization:
text = _clean_urls(text)           # US1
text = _clean_isbn(text)           # US4
text = _clean_parenthetical_english(text)  # US5
text = _normalize_references(text)  # US2/US3
```

### punctuation_normalizer.py Changes

1. **US6**: `_normalize_line()` Rule 4 修正
   - 「ではありません」等のパターンで除外
2. **US7**: `_normalize_colons()` 新規追加
3. **US8**: `_normalize_brackets()` 新規追加

パイプライン順序 (normalize_punctuation 内):
```python
line = _normalize_colons(line)     # US7: コロン変換
line = _normalize_brackets(line)   # US8: 鉤括弧変換
line = _normalize_line(line)       # 既存ルール + US6修正
```

## Next Phase

Phase 2: US1 URL処理 (TDD)
- tdd-generator で RED テスト実装
- phase-executor で GREEN 実装
