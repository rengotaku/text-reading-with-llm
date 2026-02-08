# Phase 5 Output

## 作業概要
- User Story 5 (括弧付き用語の重複読み防止) の実装完了
- FAIL テスト 24 件を PASS させた
- 全テスト (81件) が GREEN

## 修正ファイル一覧
- `src/text_cleaner.py` - 括弧付き英語削除機能を追加

## 実装内容

### 追加されたパターン定数

```python
# Parenthetical patterns for English term removal (US5)
# Matches brackets containing only ASCII letters, numbers, spaces, hyphens, periods, commas
# But preserves brackets containing Japanese characters or empty content
PAREN_ENGLISH_FULL = re.compile(r'（[A-Za-z][A-Za-z0-9\s\-.,]*）')
PAREN_ENGLISH_HALF = re.compile(r'\([A-Za-z][A-Za-z0-9\s\-.,]*\)')
```

### 追加された関数

```python
def _clean_parenthetical_english(text: str) -> str:
    """Remove parenthetical English terms for TTS.

    Removes:
    - 全角括弧内の英語のみ: トイル（Toil）→ トイル
    - 半角括弧内の英語のみ: トイル(Toil) → トイル

    Preserves:
    - 日本語を含む括弧: SRE（サイト信頼性）→ 保持
    - 空括弧: （）→ 保持
    - 数字のみ括弧: （1.0）→ 保持
    """
    text = PAREN_ENGLISH_FULL.sub("", text)
    text = PAREN_ENGLISH_HALF.sub("", text)
    return text
```

## テスト結果

### 新規テスト (24件)
- **TestCleanParentheticalFullWidth** (3件): 全角括弧内の英語削除 → PASS
- **TestCleanParentheticalHalfWidth** (3件): 半角括弧内の英語削除 → PASS
- **TestCleanParentheticalPreserve** (4件): 日本語含む括弧の保持 → PASS
- **TestCleanParentheticalAlphabetTerm** (3件): アルファベット用語の処理 → PASS
- **TestCleanParentheticalEdgeCases** (7件): エッジケース → PASS
- **TestCleanParentheticalIdempotent** (4件): 冪等性確認 → PASS

### リグレッションテスト
- US1 (URL処理): 15件 → PASS
- US2/US3 (参照正規化): 24件 → PASS
- US4 (ISBN削除): 18件 → PASS

**Total: 81/81 tests passed** (GREEN)

## 実装のポイント

### パターンマッチング戦略

1. **英語のみ検出**: `[A-Za-z][A-Za-z0-9\s\-.,]*`
   - 最初の文字は必ず英字 → 数字のみの括弧を保持
   - 以降は英字・数字・スペース・ハイフン・ピリオド・カンマ

2. **日本語の除外**: パターンに日本語を含めない
   - 日本語が1文字でも含まれていればマッチしない → 保持される

3. **空括弧の保持**: パターンが最初の文字を要求
   - 空括弧 `（）` や `()` はマッチしない → 保持される

### 冪等性

- 処理済みテキストを再処理しても結果は同じ
- 括弧のないテキストは変化しない

## 注意点

### 次 Phase (Phase 6) で必要な情報

- 本関数は単体で動作し、`clean_page_text()` パイプラインには未統合
- Phase 9 で全関数を統合予定
- 関数の位置: `_clean_isbn()` の直後

### 技術的考慮

- 正規表現パターンは現在グローバル定数（モジュールレベル）
- Phase 10 でパフォーマンス最適化時に `re.compile()` の配置を再確認

## 実装のミス・課題

- なし（全テスト PASS）

## 次ステップ

Phase 6: User Story 6 - 不適切な読点挿入の修正
- ターゲットファイル: `src/punctuation_normalizer.py`
- 実装内容: 「ではありません」等の否定形で「は」の後に読点を入れない
