# Research: 開発環境の最適化

**Feature**: 016-dev-env-optimization
**Date**: 2026-03-02

## 1. pytest カバレッジ設定

### Decision: pyproject.toml で pytest.ini_options を使用

### Rationale
- 設定の一元管理（pytest.ini や setup.cfg を追加しない）
- pytest 6.0+ で公式サポート
- 既存の pyproject.toml に追加するだけで完了

### 推奨設定

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=xml:coverage.xml",
    "--cov-fail-under=80",
]
```

### Alternatives Considered

| 方式 | 長所 | 短所 | 却下理由 |
|------|------|------|----------|
| pytest.ini | 広いバージョン互換性 | 別ファイル増加 | 設定ファイル分散 |
| setup.cfg | 旧来の標準 | 非推奨化の流れ | pyproject.toml が標準 |
| conftest.py | 動的設定可能 | 可読性低下 | 静的設定で十分 |

---

## 2. GitHub Actions キャッシュ最適化

### Decision: actions/setup-python の cache オプション + キャッシュキー最適化

### Rationale
- 現状既に `cache: 'pip'` を使用中（基本キャッシュは有効）
- `cache-dependency-path: pyproject.toml` も設定済み
- 追加最適化は不要（既に最適な設定）

### 現状の設定（変更不要）

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.10'
    cache: 'pip'
    cache-dependency-path: pyproject.toml
```

### 追加検討事項

| 最適化案 | 効果 | 採用 |
|----------|------|------|
| actions/cache 手動設定 | より細かい制御 | ❌ setup-python で十分 |
| キャッシュキーにハッシュ追加 | 衝突回避 | ❌ 自動で含まれる |
| 複数キャッシュパス | 追加キャッシュ | ❌ pip のみで十分 |

### Alternatives Considered
- `actions/cache@v4` 直接使用: setup-python 内蔵キャッシュの方がシンプル
- pip-tools でロックファイル: 小規模プロジェクトでは過剰

---

## 3. PR カバレッジコメント

### Decision: py-cov-action/python-coverage-comment-action を使用

### Rationale
- Python 専用で設定シンプル
- カバレッジ変化の差分表示サポート
- 外部サービス不要（GitHub のみで完結）
- MIT ライセンス

### 推奨設定

```yaml
- name: Coverage comment
  uses: py-cov-action/python-coverage-comment-action@v3
  with:
    GITHUB_TOKEN: ${{ github.token }}
    MINIMUM_GREEN: 80
    MINIMUM_ORANGE: 60
```

### Alternatives Considered

| ツール | 長所 | 短所 | 却下理由 |
|--------|------|------|----------|
| codecov/codecov-action | 高機能、業界標準 | 外部サービス依存、設定複雑 | シンプルさ優先 |
| irongut/CodeCoverageSummary | .NET 向け | Python 非対応 | 言語不一致 |
| 自作スクリプト | 完全カスタマイズ | メンテナンスコスト | 既存アクションで十分 |

### 必要な権限
- `pull-requests: write`（PR コメント用）
- `contents: write`（カバレッジデータ保存用、オプション）

---

## 4. カバレッジバッジ生成

### Decision: gist + shields.io 動的バッジ方式

### Rationale
- 外部サービス（Codecov 等）不要
- GitHub Gist で自己ホスト
- shields.io でバッジ生成（無料、高可用性）
- py-cov-action でバッジデータも生成可能

### 推奨設定

```yaml
# py-cov-action が自動でバッジデータを生成
- name: Coverage comment
  uses: py-cov-action/python-coverage-comment-action@v3
  with:
    GITHUB_TOKEN: ${{ github.token }}
    COVERAGE_FILE: coverage.xml
```

README.md へのバッジ追加:
```markdown
![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/{user}/{gist_id}/raw/coverage.json)
```

### Alternatives Considered

| 方式 | 長所 | 短所 | 却下理由 |
|------|------|------|----------|
| Codecov | 高機能、PR 統合 | 外部サービス依存 | シンプルさ優先 |
| Coveralls | 老舗サービス | アカウント必要 | 外部依存回避 |
| 静的バッジ | シンプル | 手動更新必要 | 自動更新が必須 |

---

## 5. 現状分析

### 既存設定の確認

**pyproject.toml**:
- pytest-cov は dev 依存に含まれる ✅
- pytest 関連設定なし（追加必要）

**.github/workflows/ci.yml**:
- キャッシュ設定済み ✅
- カバレッジ実行なし（追加必要）
- PR コメント機能なし（追加必要）

### 実装優先順位

1. **P1**: pytest 設定（pyproject.toml）- 基盤
2. **P2**: CI カバレッジ実行 + PR コメント - 可視化
3. **P2**: キャッシュ確認 - 既に最適化済み
4. **P3**: カバレッジバッジ - 付加価値

---

## 6. 実装時の注意点

### カバレッジ閾値について

現在のテストカバレッジを事前確認:
```bash
pytest --cov=src --cov-report=term-missing
```

- 80% 未満の場合、初期は `--cov-fail-under` を低く設定
- または CI では警告のみ、ローカルでは閾値チェック

### CI ワークフローの権限

PR コメントには permissions 設定が必要:
```yaml
permissions:
  contents: write
  pull-requests: write
```

### coverage.xml の生成

PR コメントアクションには XML 形式が必要:
```
--cov-report=xml:coverage.xml
```
