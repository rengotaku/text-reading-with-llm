# Research: mypy 型チェック導入

**Feature**: 014-mypy-type-checking
**Date**: 2026-02-27

## 1. mypy 設定ベストプラクティス

### Decision: 段階的導入設定を採用

**Rationale**: 既存コードに型ヒントがない状態から始めるため、厳格モードは段階的に有効化する。初期設定では警告レベルを抑え、新規コードに集中する。

**設定オプション分析**:

| オプション | 推奨値 | 理由 |
|-----------|--------|------|
| `python_version` | "3.10" | プロジェクトの最小サポートバージョン |
| `warn_return_any` | true | Any 型の暗黙的な返却を警告 |
| `warn_unused_ignores` | true | 不要な type: ignore を検出 |
| `disallow_untyped_defs` | false | 既存コードに型がないため無効化 |
| `ignore_missing_imports` | true | サードパーティライブラリの型スタブ不足を許容 |
| `files` | ["src"] | 型チェック対象を src/ に限定 |

**Alternatives Considered**:

1. **strict = true**: 全オプション有効化 → 既存コードで大量エラー発生のため却下
2. **check_untyped_defs = true**: 型なし関数内も検査 → 段階2で検討
3. **disallow_any_generics = true**: ジェネリクス Any 禁止 → 段階3で検討

### 段階的導入ロードマップ

```
Phase 1 (now):     基本設定 + 警告のみ
Phase 2 (future):  check_untyped_defs = true
Phase 3 (future):  disallow_untyped_defs = true (新規ファイルのみ)
Phase 4 (future):  strict = true (全ファイル)
```

## 2. サードパーティライブラリ型スタブ

### Decision: ignore_missing_imports = true を使用

**Rationale**: 現在の依存関係の多くは型スタブが不完全または存在しない。プロジェクト進行を妨げないよう、まず無視設定を使用。

**依存関係の型スタブ状況**:

| パッケージ | 型スタブ | 対応策 |
|-----------|---------|--------|
| soundfile | ❌ なし | ignore_missing_imports |
| pyyaml | ✅ types-PyYAML | 将来追加可 |
| numpy | ✅ 組み込み | 利用可能 |
| requests | ✅ types-requests | 将来追加可 |
| fugashi | ❌ なし | ignore_missing_imports |
| unidic-lite | ❌ なし | ignore_missing_imports |
| scipy | ✅ 組み込み | 利用可能 |

**Alternatives Considered**:

1. **types-* パッケージをすべてインストール**: 有効だが、メンテナンス負荷増加
2. **per-module ignore 設定**: 細かい制御可能だが、設定が複雑化

## 3. CI 統合パターン

### Decision: 既存 lint ジョブ内に mypy ステップを追加

**Rationale**:
- 新規ジョブ作成は CI 実行時間増加（並列化メリットなし）
- 既存の lint ジョブ（ruff check → ruff format → pytest）の流れに mypy を挿入
- ruff の後、pytest の前が最適（lint → type check → test の順序）

**CI ステップ配置**:

```yaml
- name: Run ruff check
  run: ruff check .

- name: Run ruff format check
  run: ruff format --check .

- name: Run mypy        # ← 追加位置
  run: mypy src/

- name: Run pytest
  run: PYTHONPATH=. pytest tests/ --forked --tb=short -q
```

**Alternatives Considered**:

1. **独立 mypy ジョブ**: 並列実行可能だが、CI リソース消費増加
2. **pytest 後に配置**: 論理的な流れに反する（型エラーはテスト前に検出すべき）

## 4. mypy インストール方法

### Decision: pyproject.toml の dev 依存に追加

**Rationale**: 既存の開発ツール（ruff, pytest）と同様の方法で管理。

**変更内容**:

```toml
[project.optional-dependencies]
dev = [
    "ruff",
    "pre-commit",
    "pytest",
    "pytest-cov",
    "pytest-timeout",
    "pytest-forked",
    "mypy",  # 追加
]
```

## まとめ

| 決定事項 | 選択 |
|---------|------|
| 設定アプローチ | 段階的導入（厳格モード無効） |
| 型スタブ対応 | ignore_missing_imports = true |
| CI 統合 | 既存 lint ジョブに mypy ステップ追加 |
| インストール | dev 依存に mypy 追加 |
