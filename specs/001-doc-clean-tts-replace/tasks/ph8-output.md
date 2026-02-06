# Phase 8 Output

## 作業概要
- User Story 8 - 鉤括弧の読点変換 の実装完了
- FAIL テスト 16 件を PASS させた
- `_normalize_brackets()` 関数を新規実装

## 修正ファイル一覧
- `src/punctuation_normalizer.py` - 鉤括弧変換関数の追加と統合

### 変更詳細

#### 1. パターン定数の追加（L77-79）
```python
# Bracket patterns for conversion (US8)
OPEN_BRACKET_PATTERN = re.compile(r'[「『]')
CLOSE_BRACKET_PATTERN = re.compile(r'[」』]')
```

#### 2. `_normalize_brackets()` 関数の実装（L157-173）
```python
def _normalize_brackets(text: str) -> str:
    """Convert Japanese quotation marks to commas for TTS.

    Converts:
    - 「 → 、
    - 」 → 、
    - 『 → 、
    - 』 → 、
    """
    # Convert opening brackets
    text = OPEN_BRACKET_PATTERN.sub("、", text)
    # Convert closing brackets
    text = CLOSE_BRACKET_PATTERN.sub("、", text)

    return text
```

#### 3. `normalize_punctuation()` への統合（L110-111）
```python
# Apply colon normalization before line normalization
line = _normalize_colons(line)
# Apply bracket normalization before line normalization
line = _normalize_brackets(line)
result_lines.append(_normalize_line(line))
```

## テスト結果

### Phase 8 新規テスト (16 tests)
- ✅ TestNormalizeBracketsBasic (2 tests) - 基本的な鉤括弧変換
- ✅ TestNormalizeBracketsWithText (3 tests) - テキスト内の鉤括弧変換
- ✅ TestNormalizeBracketsConsecutive (2 tests) - 連続する鉤括弧
- ✅ TestNormalizeBracketsEdgeCases (7 tests) - エッジケース（空文字列、ネスト等）
- ✅ TestNormalizeBracketsIntegration (2 tests) - normalize_punctuation統合

### リグレッションテスト
- ✅ US1-7 の既存テスト 119 件 すべて PASS
- ✅ 総テスト数: 135 passed

### 変換例

| 入力 | 出力 |
|------|------|
| 「テスト」という言葉 | 、テスト、という言葉 |
| これは「重要な」ポイントです | これは、重要な、ポイントです |
| 「A」と「B」がある | 、A、と、B、がある |
| 「『内側』の外側」 | 、、内側、の外側、 |

## 実装のポイント

### シンプルな置換アプローチ
- 開き鉤括弧（「『）→ 読点（、）
- 閉じ鉤括弧（」』）→ 読点（、）
- 正規表現で文字クラス `[「『]` `[」』]` を使用

### コロン変換との順序
1. `_normalize_colons()` - コロン変換
2. `_normalize_brackets()` - 鉤括弧変換（NEW）
3. `_normalize_line()` - 読点ルール適用

この順序により、鉤括弧変換後の読点が `_normalize_line()` で処理される可能性がある。

### 連続読点の非処理
- RED テストでは「連続する読点（、、）の処理」が示唆されていた
- しかし、実装した `_normalize_brackets()` では連続読点をそのまま残す
- 理由: テストが `、、` のまま期待値を設定しており、正規化を求めていないため
- 例: `「『内側』の外側」` → `、、内側、の外側、` (テスト期待値と一致)

## 注意点

### 次 Phase (Phase 9) で必要な情報
- `_normalize_brackets()` は `punctuation_normalizer.py` の最後の新規関数
- Phase 9 では `text_cleaner.py` と `punctuation_normalizer.py` の全関数をパイプラインに統合
- 統合順序の確認が必要

### Phase 8 で統合済み
- `normalize_punctuation()` に `_normalize_brackets()` はすでに統合済み
- Phase 9 では追加の統合作業は不要（既存統合の確認のみ）

## 実装のミス・課題
- なし

## 技術的負債
- なし

## Phase 9 への引き継ぎ
- `punctuation_normalizer.py` の新規関数実装は完了
- 統合テストで全変換が正しい順序で適用されることを確認する必要あり
- `text_cleaner.py` の `clean_page_text()` にも各関数を統合する必要あり
