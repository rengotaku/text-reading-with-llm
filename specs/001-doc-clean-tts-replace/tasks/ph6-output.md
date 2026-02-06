# Phase 6 Output

## 作業概要
- Phase 6 - User Story 6: 不適切な読点挿入の修正 の実装完了
- FAIL テスト 6 件を PASS させた
- 「ではありません」「にはならない」等のパターンで「は」の後に読点を挿入しない機能を実装

## 修正ファイル一覧
- `src/punctuation_normalizer.py` - Rule 4 に除外パターン追加（negative lookahead 使用）

## 実装詳細

### 1. EXCLUSION_SUFFIXES 定数追加

「は」の後に読点を挿入しない除外パターンを定義:

```python
EXCLUSION_SUFFIXES = [
    # では系
    "ありません",
    "ありませんでした",
    "ありますが",
    "ある",
    "ない",
    "なかった",
    "なくて",
    "ないか",
    # には系
    "ならない",
    "ならなかった",
    "至らない",
    # とは系
    "言えない",
    "限らない",
]
```

### 2. Rule 4 の修正

`_normalize_line()` の Rule 4 に negative lookahead を追加:

**変更前**:
```python
line = re.sub(
    rf"([^、。！？]{{{ha_prefix_len},}})(は)([^、。！？\s])",
    r"\1\2、\3",
    line
)
```

**変更後**:
```python
exclusion_pattern = "|".join(re.escape(s) for s in EXCLUSION_SUFFIXES)
line = re.sub(
    rf"([^、。！？]{{{ha_prefix_len},}})(は)(?!({exclusion_pattern}))([^、。！？\s])",
    r"\1\2、\4",
    line
)
```

### 3. テスト結果

全 102 テスト PASS:
- US6 新規テスト: 21 tests PASS
- リグレッションテスト（US1-5): 81 tests PASS

## 動作確認

### 除外パターン

以下のパターンでは「は」の後に読点が挿入されない:
- `これは問題ではありません` → `これは問題ではありません`（読点なし）
- `この方法にはならない` → `この方法にはならない`（読点なし）
- `これとは言えない` → `これとは言えない`（読点なし）

### 通常の「は」は引き続き機能

長いフレーズの後の「は」には引き続き読点が挿入される:
- `この技術の導入は重要です` → `この技術の導入は、重要です`（読点あり）
- `私たちの目標は達成することです` → `私たちの目標は、達成することです`（読点あり）

## 次 Phase への引き継ぎ

### 完了した User Story
- US1: URL の除去・簡略化（Phase 2）
- US2/3: 図表・注釈参照の読み上げ（Phase 3）
- US4: ISBN の簡略化（Phase 4）
- US5: 括弧付き用語の重複読み防止（Phase 5）
- US6: 不適切な読点挿入の修正（Phase 6）✅ **NEW**

### 残り User Story
- US7: コロン記号の自然な読み上げ変換（Phase 7）
- US8: 鉤括弧の読点変換（Phase 8）
- 統合テスト（Phase 9）
- Polish（Phase 10）

### 技術的制約
- `EXCLUSION_SUFFIXES` リストは文法的に密接な助詞+動詞/形容詞の組み合わせを定義
- 追加の除外パターンが必要な場合は `EXCLUSION_SUFFIXES` に追加可能
- negative lookahead により、通常の「は」の処理には影響を与えない

## 実装のミス・課題

なし。全テスト PASS、リグレッションなし。
