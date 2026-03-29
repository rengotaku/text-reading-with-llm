# Research: キーワード抽出とカバー率検証

**Date**: 2026-03-28
**Feature**: 071-keyword-coverage-validation

## 調査項目

### 1. LLM キーワード抽出パターン

**Decision**: 既存の prompt_loader.py + ollama パターンを使用

**Rationale**:
- プロジェクト内で確立されたパターン（dialogue_converter.py で実績あり）
- [SYSTEM] / [USER] セクション形式のプロンプトファイル
- プレースホルダー置換による動的プロンプト生成

**Alternatives considered**:
- 独自プロンプト管理: 既存パターンとの一貫性を損なう
- 外部ライブラリ（LangChain等）: オーバースペック

### 2. キーワードマッチング戦略

**Decision**: 大文字小文字を区別しない完全一致

**Rationale**:
- 仕様要件に明記（FR-007: LLM不使用）
- シンプルで決定論的な処理
- 日本語テキストでは大文字小文字の区別は不要だが、英数字混在に対応

**Alternatives considered**:
- 部分一致: 偽陽性が多くなる
- 形態素解析: 処理コストが高い、メリット不明確
- Embedding類似度: LLM使用禁止の制約に反する

### 3. JSON出力スキーマ

**Decision**: Issue #71 で定義されたスキーマを採用

```json
{
  "total_keywords": 12,
  "covered_keywords": 9,
  "coverage_rate": 0.75,
  "missing_keywords": ["2027年", "A社", "B社"]
}
```

**Rationale**:
- 仕様で明確に定義済み
- シンプルで解析しやすい構造
- 必要十分な情報を含む

### 4. プロンプト設計

**Decision**: Issue #71 のプロンプト例を採用（微調整可）

**Rationale**:
- 仕様で詳細なプロンプト例が提供されている
- 出力形式（カンマ区切り）が明確

**出力形式の補足**:
- カンマ区切りのテキストとして出力
- パース時に各キーワードを trim して空白を除去

## 未解決事項

なし。全ての技術的判断が完了。
