# Project Instructions

## 環境設定

### venv 必須
- このプロジェクトは `.venv` を使用する
- pip install コマンドを実行する前に、必ず venv が有効化されていることを確認すること
- グローバル環境への直接インストールは絶対に禁止

```bash
# venv が有効か確認
which python  # .venv/bin/python であること

# 有効でない場合
source .venv/bin/activate
```

### パッケージインストール手順
1. venv が有効化されていることを確認
2. `pip install -r requirements.txt`
3. 追加パッケージは requirements.txt に追記してからインストール
