# Quickstart: mypy 型チェック

## セットアップ

mypy は dev 依存としてインストールされます。

```bash
# venv をセットアップ済みの場合
pip install -e ".[dev]"

# または Makefile から
make setup
```

## 基本的な使い方

### ローカルで型チェック実行

```bash
# Makefile 経由（推奨）
make lint

# 直接実行
mypy src/
```

### 特定ファイルのみチェック

```bash
mypy src/text_cleaner.py
```

## 型ヒントの書き方

### 基本的な関数

```python
def greet(name: str) -> str:
    return f"Hello, {name}"

def add(a: int, b: int) -> int:
    return a + b
```

### Optional と Union

```python
from typing import Optional

def find_user(user_id: int) -> Optional[str]:
    """ユーザーが見つからない場合は None を返す"""
    ...
```

### リストと辞書

```python
from typing import Dict, List

def process_items(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}
```

### Python 3.10+ の型ヒント（推奨）

```python
# Union の代わりに |
def get_value(key: str) -> str | None:
    ...

# list, dict を直接使用
def process(items: list[str]) -> dict[str, int]:
    ...
```

## エラー対処

### サードパーティライブラリのインポートエラー

型スタブがないライブラリをインポートすると警告が出る場合があります。
現在の設定では `ignore_missing_imports = true` で抑制されています。

### 特定の行を無視する

```python
# 型エラーを無視（理由を必ず記載）
result = some_untyped_function()  # type: ignore[no-untyped-call]  # external library
```

### 無視可能なエラーコード

| コード | 説明 |
|--------|------|
| `no-untyped-call` | 型なし関数の呼び出し |
| `no-untyped-def` | 型なし関数の定義 |
| `import-untyped` | 型なしモジュールのインポート |
| `attr-defined` | 存在しない属性へのアクセス |

## CI での動作

PR を作成すると、GitHub Actions で自動的に mypy が実行されます。
型エラーがあると CI が失敗します。

```
✓ Run ruff check
✓ Run ruff format check
✓ Run mypy          ← ここで型チェック
✓ Run pytest
```

## よくある質問

### Q: 既存コードに型ヒントを追加する必要がありますか？

A: いいえ、現在は `disallow_untyped_defs = false` のため、型ヒントなしのコードもエラーになりません。新規コードから段階的に型を追加してください。

### Q: 型チェックが遅い場合は？

A: `mypy --cache-fine-grained src/` でインクリメンタルキャッシュを有効化できます。通常は自動的にキャッシュされます。

### Q: IDE で型チェックを有効にするには？

A: VS Code の場合、Pylance 拡張機能が型チェックをサポートしています。
settings.json に以下を追加：

```json
{
    "python.analysis.typeCheckingMode": "basic"
}
```
