---
name: speckit-scope-check
description: "Before running speckit.specify, evaluate if the task is simple enough for ecc:plan instead"
---

# Speckit Scope Check

## Problem

speckit.specify は 5 Phase のワークフロー（spec → plan → tasks → implement）を生成する。
設定変更のみ、1-2 ファイル修正、などの軽量タスクには過剰。

## Solution

speckit.specify を実行する前に、タスクの複雑さを評価:

| 条件 | 推奨ワークフロー |
|------|------------------|
| 修正ファイル 1-3 件、設定変更のみ | `ecc:plan` または直接実行 |
| 新規機能、複数コンポーネント連携 | `speckit.specify` |
| リファクタリング、テスト追加のみ | 直接実行 |

## When to Use

- ユーザーが `/speckit.specify` を実行しようとしたとき
- Issue や要件が「設定追加」「ツール導入」「1行修正」レベルのとき

## Recommendation Template

> このタスクは修正量が少なそうです（推定 N ファイル、M 行程度）。
> - `speckit.specify`: 5 Phase の完全ワークフロー（ドキュメント生成含む）
> - `ecc:plan`: 軽量な計画 → 直接実装
>
> どちらを使いますか？

## Examples

### 過剰だったケース

- mypy 導入（pyproject.toml + Makefile + ci.yml = 23行）→ speckit で 2時間
- 実際は 10-15分で完了可能だった

### 適切なケース

- 新規 API エンドポイント追加（複数ファイル、テスト、ドキュメント）
- 認証システムの導入（複数コンポーネント連携）
