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

---

## Speckit 設定

### ディレクトリ構成

```
.specify/                    # Speckit 設定
├── scripts/bash/            # Bash スクリプト
│   ├── common.sh            # 共通関数
│   ├── create-new-feature.sh # 新規フィーチャー作成
│   ├── check-prerequisites.sh # 前提条件チェック
│   ├── setup-plan.sh        # プラン設定
│   └── update-agent-context.sh # エージェントコンテキスト更新
├── templates/               # テンプレート
│   ├── spec-template.md     # 仕様テンプレート
│   ├── plan-template.md     # 計画テンプレート
│   ├── tasks-template.md    # タスクテンプレート
│   ├── checklist-template.md # チェックリストテンプレート
│   └── agent-file-template.md # エージェントファイルテンプレート
└── memory/                  # 憲法・メモリ用

.claude/
├── commands/                # Speckit コマンド
│   ├── speckit.specify.md   # 仕様作成
│   ├── speckit.clarify.md   # 曖昧さ解消
│   ├── speckit.plan.md      # 実装計画
│   ├── speckit.tasks.md     # タスク生成
│   ├── speckit.checklist.md # チェックリスト生成
│   ├── speckit.analyze.md   # 一貫性分析
│   ├── speckit.implement.md # 実装実行
│   ├── speckit.constitution.md # プロジェクト憲法
│   └── speckit.taskstoissues.md # GitHub Issue 変換
└── agents/                  # サブエージェント
    ├── phase-executor.md    # GREEN フェーズ + 通常 Phase 実行
    └── tdd-generator.md     # RED フェーズ（テスト実装）

specs/                       # フィーチャー仕様格納
└── ###-feature-name/        # フィーチャーブランチ名と同一
    ├── spec.md              # 機能仕様
    ├── plan.md              # 実装計画
    ├── tasks.md             # タスクリスト
    ├── research.md          # リサーチ結果
    ├── data-model.md        # データモデル
    ├── quickstart.md        # クイックスタート
    ├── contracts/           # API コントラクト
    ├── checklists/          # チェックリスト
    ├── tasks/               # Phase 出力
    └── red-tests/           # RED テスト出力
```

### ワークフロー

1. `/speckit.specify` - 仕様作成（フィーチャーブランチ作成）
2. `/speckit.clarify` - 仕様の曖昧さを解消
3. `/speckit.plan` - 技術計画作成
4. `/speckit.tasks` - タスク生成（TDD ワークフロー）
5. `/speckit.checklist` - 要件品質チェックリスト作成
6. `/speckit.analyze` - 一貫性分析
7. `/speckit.implement` - 実装実行（Phase 単位）

### TDD ワークフロー

各 User Story Phase は TDD フローで実行:
- **tdd-generator** (opus): テスト実装 → RED 確認 → `red-tests/ph{N}-test.md` 出力
- **phase-executor** (sonnet): 実装 → GREEN 確認 → 検証 → `tasks/ph{N}-output.md` 出力

## Recent Changes
- 008-ruff-precommit-setup: Added Python 3.10+ + ruff, pre-commit（開発用依存関係として追加）
- 007-cleanup-unused-code: Added Python 3.10+ + xml.etree.ElementTree, voicevox_core, MeCab, soundfile, numpy
- 006-xml-dict-support: Added Python 3.10+ + xml.etree.ElementTree（標準ライブラリ）, src/xml2_parser, src/dict_manager, src/llm_reading_generator

## Active Technologies
- Python 3.10+ + ruff, pre-commit（開発用依存関係として追加） (008-ruff-precommit-setup)
