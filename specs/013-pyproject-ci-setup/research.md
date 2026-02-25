# Research: pyproject.toml 整備 + CI テスト追加

**Date**: 2026-02-25
**Status**: Complete

## 1. pyproject.toml [project] セクション構造

### Decision
PEP 621 準拠の `[project]` セクションを使用する。

### Rationale
- Python パッケージングの標準仕様
- pip 21.3+ でネイティブサポート
- setuptools, flit, poetry など主要ツールが対応

### Structure

```toml
[project]
name = "text-reading-with-llm"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "soundfile",
    "pyyaml",
    "numpy",
    "requests",
    "fugashi",
    "unidic-lite",
]

[project.optional-dependencies]
dev = [
    "ruff",
    "pre-commit",
    "pytest",
    "pytest-cov",
]
```

### Alternatives Considered
- **setup.py**: 旧式、pyproject.toml に移行が推奨
- **requirements.txt 維持**: 二重管理になる、不採用

---

## 2. GitHub Actions pytest 設定

### Decision
既存の lint.yml に pytest ステップを追加する。

### Rationale
- 単一ワークフローで lint + test を実行
- ジョブを分離せず、シンプルに保つ
- ローカル専用プロジェクトなので複雑な CI は不要

### Structure

```yaml
- name: Install dependencies
  run: pip install -e ".[dev]"

- name: Run tests
  run: pytest tests/ -v
```

### Alternatives Considered
- **別ワークフロー (test.yml)**: 管理コスト増、不採用
- **Matrix build (複数 Python バージョン)**: ローカル専用なので不要

---

## 3. VOICEVOX wheel 対応

### Decision
Makefile の setup-voicevox ターゲットで別途インストールを継続。

### Rationale
- VOICEVOX Core は PyPI にないため、pip install の dependencies に含められない
- 外部 URL からの wheel インストールが必要
- 既存の Makefile ターゲットが正常動作している

### Implementation
- pyproject.toml には含めない
- Makefile の `setup` ターゲットで `setup-voicevox` を呼び出す
- README に手順を明記

---

## 4. egg-info ディレクトリ

### Decision
`src/UNKNOWN.egg-info/` を削除し、.gitignore に `*.egg-info/` を確認。

### Rationale
- UNKNOWN は pyproject.toml に name がなかったため生成された
- 正しい name 設定後、`text_reading_with_llm.egg-info/` が生成される
- egg-info は .gitignore に含まれているため、コミット不要

### Note
現在の .gitignore: `*.egg-info/` - 対応済み

---

## Resolved Clarifications

このフィーチャーに NEEDS CLARIFICATION はなし。全ての技術的詳細が明確。
