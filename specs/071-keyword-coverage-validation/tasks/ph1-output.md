# Phase 1 Output: Setup

**Date**: 2026-03-28
**Status**: Completed

## Executed Tasks

- [x] T001 Read: src/prompt_loader.py（プロンプト読み込みパターン確認）
- [x] T002 Read: src/dialogue_converter.py（ollama 使用パターン確認）
- [x] T003 Read: src/prompts/generate_dialogue.txt（プロンプト形式確認）
- [x] T004 Read: tests/test_prompt_loader.py（テストパターン確認）
- [x] T005 Edit: specs/071-keyword-coverage-validation/tasks/ph1-output.md

## Existing Code Analysis

### prompt_loader.py

**Structure**:
- `PROMPTS_DIR`: プロンプトディレクトリパス（`src/prompts/`）
- `PromptLoadError`: プロンプト読み込みエラー例外
- `load_prompt(name, **kwargs)`: プロンプトファイル読み込み、`(system, user)` タプルを返す
- `get_available_prompts()`: 利用可能なプロンプト名リストを返す

**Key Patterns**:
1. プロンプトファイル形式: `[SYSTEM]\n...\n[USER]\n...`
2. プレースホルダー置換: `{placeholder}` 形式
3. 未置換プレースホルダーチェック: 正規表現 `\{[a-z_]+\}`

**Required Updates**: なし（既存機能をそのまま利用）

### dialogue_converter.py

**Structure**:
- `ollama` インポート: CI環境判定後に条件付きインポート
- `DEFAULT_MODEL = "gpt-oss:20b"`: デフォルトモデル
- `generate_introduction/generate_conclusion/generate_dialogue`: LLM呼び出し関数

**LLM呼び出しパターン**:
```python
def generate_xxx(
    ...,
    model: str = DEFAULT_MODEL,
    ollama_chat_func: Callable[..., Any] | None = None,
) -> str:
    system, user = load_prompt("prompt_name", **kwargs)

    if ollama_chat_func is None:
        ollama_chat_func = ollama.chat

    response = ollama_chat_func(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response["message"]["content"]
```

**Required Updates**: なし（パターンを keyword_extractor.py で再利用）

### prompts/generate_dialogue.txt

**Format**:
```
[SYSTEM]
システムメッセージ（役割定義）

[USER]
ユーザーメッセージ（{placeholder} で動的コンテンツを挿入）
```

**Required for extract_keywords.txt**:
- `[SYSTEM]` セクション: キーワード抽出の専門家としての役割定義
- `[USER]` セクション: `{section_text}` プレースホルダーで原文を挿入
- 出力形式: カンマ区切りのキーワードリスト

## Existing Test Analysis

### tests/test_prompt_loader.py

**Coverage**:
- `load_prompt`: 正常系・エラー系（存在しないファイル、未置換プレースホルダー）
- `get_available_prompts`: リスト返却、期待されるプロンプト含有
- プロンプトディレクトリ: 存在確認、`[SYSTEM]`/`[USER]` セクション検証

**Test Patterns**:
1. 個別プロンプトのテスト: `test_load_xxx_prompt`
2. エラーケース: `pytest.raises(PromptLoadError)`
3. ディレクトリ検証: ファイル存在、セクション含有

**Required for test_keyword_extractor.py**:
- プロンプトファイル読み込みテスト
- キーワード抽出関数のモックテスト（`ollama_chat_func` パラメータ活用）
- エッジケース（空テキスト）

**Does not exist**:
- `tests/test_keyword_extractor.py` → Create new
- `tests/test_coverage_validator.py` → Create new

## Technical Decisions

1. **プロンプト形式**: 既存の `[SYSTEM]/[USER]` 形式を採用（一貫性維持）
2. **LLM呼び出し**: `ollama_chat_func` パラメータパターンを採用（テスタビリティ確保）
3. **モジュール構成**: 独立した `keyword_extractor.py` と `coverage_validator.py` を作成（単一責任）

## Handoff to Next Phase

### Phase 2 (US1: キーワード抽出) で実装するもの

**src/prompts/extract_keywords.txt**:
- `[SYSTEM]`: キーワード抽出の専門家として定義
- `[USER]`: `{section_text}` を含む、出力形式（カンマ区切り）を指定

**src/keyword_extractor.py**:
- `extract_keywords(section_text, model, ollama_chat_func)`:
  - `load_prompt("extract_keywords", section_text=section_text)` でプロンプト取得
  - `ollama_chat_func` で LLM 呼び出し
  - レスポンスをカンマで分割、trim、重複除去して `list[str]` を返す

**Reusable Existing Code**:
- `load_prompt` 関数をそのまま使用
- `ollama_chat_func` パターンでテスタビリティ確保

**Caveats**:
- CI環境では `ollama` が利用不可のため、テストでは `ollama_chat_func` をモック
- 空テキスト入力時は LLM 呼び出し前に空リストを返す（効率化）
