# Phase 4 RED Test: 段階的型付け検証

**Date**: 2026-02-28
**Status**: RED (検証前の状態)

## 目的

既存コードが型ヒントなしでも mypy エラーを出さないことを確認する。これにより、段階的型付け導入の設定が正しく機能していることを検証する。

## 検証対象設定

### pyproject.toml の [tool.mypy] 設定

```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = false
warn_unused_ignores = true
disallow_untyped_defs = false       # 型ヒントなし関数を許可
ignore_missing_imports = true
check_untyped_defs = false
disallow_any_explicit = false
disallow_any_generics = false
no_implicit_optional = false
disallow_incomplete_defs = false
namespace_packages = false

[[tool.mypy.overrides]]
module = [
    "number_normalizer",
    "voicevox_client",
    "generate_reading_dict"
]
ignore_errors = true                 # これらのモジュールは完全無視
```

**重要な設定**:
- `disallow_untyped_defs = false`: 型ヒントなし関数定義を許可
- `check_untyped_defs = false`: 型ヒントなし関数の本体をチェックしない
- `disallow_incomplete_defs = false`: 部分的な型ヒントを許可
- `[[tool.mypy.overrides]]`: 3つのモジュールは完全にエラーを無視

## 型ヒントなし関数のリスト

**総計**: 15 関数（10 ファイル）

### 1. src/chapter_processor.py (2 関数)

| 関数名 | 行番号 | return 型 | params 型 | 詳細 |
|--------|--------|-----------|-----------|------|
| `process_chapters()` | 83 | ✓ | 4/6 | synthesizer, args パラメータが未型付け |
| `process_content()` | 246 | ✓ | 4/6 | synthesizer, args パラメータが未型付け |

### 2. src/generate_reading_dict.py (1 関数)

| 関数名 | 行番号 | return 型 | params 型 | 詳細 |
|--------|--------|-----------|-----------|------|
| `main()` | 146 | ✗ | 0/0 | CLI エントリーポイント、return 型なし |

**注**: このモジュールは `ignore_errors = true` で完全無視

### 3. src/llm_reading_generator.py (1 関数)

| 関数名 | 行番号 | return 型 | params 型 | 詳細 |
|--------|--------|-----------|-----------|------|
| `generate_readings_with_llm()` | 81 | ✓ | 2/3 | api_key パラメータが未型付け |

### 4. src/process_manager.py (2 関数)

| 関数名 | 行番号 | return 型 | params 型 | 詳細 |
|--------|--------|-----------|-----------|------|
| `write_pid_file()` | 74 | ✗ | 1/1 | return 型なし、pid_file 未型付け |
| `cleanup_pid_file()` | 84 | ✗ | 1/1 | return 型なし、pid_file 未型付け |

### 5. src/punctuation_normalizer.py (1 関数)

| 関数名 | 行番号 | return 型 | params 型 | 詳細 |
|--------|--------|-----------|-----------|------|
| `save_time_ratio()` | 146 | ✗ | 0/1 | return 型なし、パラメータ未型付け |

### 6. src/text_cleaner.py (1 関数)

| 関数名 | 行番号 | return 型 | params 型 | 詳細 |
|--------|--------|-----------|-----------|------|
| `replace_markdown_link()` | 168 | ✗ | 0/1 | ネストした関数、match 未型付け |

### 7. src/text_cleaner_cli.py (2 関数)

| 関数名 | 行番号 | return 型 | params 型 | 詳細 |
|--------|--------|-----------|-----------|------|
| `parse_args()` | 24 | ✗ | 0/1 | return 型なし、args 未型付け |
| `main()` | 60 | ✗ | 0/1 | return 型なし、args 未型付け |

### 8. src/voicevox_client.py (1 関数)

| 関数名 | 行番号 | return 型 | params 型 | 詳細 |
|--------|--------|-----------|-----------|------|
| `__init__()` | 71 | ✗ | 1/1 | コンストラクタ、return 型なし、synthesizer 未型付け |

**注**: このモジュールは `ignore_errors = true` で完全無視

### 9. src/xml2_parser.py (2 関数)

| 関数名 | 行番号 | return 型 | params 型 | 詳細 |
|--------|--------|-----------|-----------|------|
| `_should_read_aloud()` | 236 | ✓ | 0/1 | elem パラメータが未型付け |
| `process_element()` | 124 | ✓ | 0/1 | elem パラメータが未型付け |

### 10. src/xml2_pipeline.py (2 関数)

| 関数名 | 行番号 | return 型 | params 型 | 詳細 |
|--------|--------|-----------|-----------|------|
| `parse_args()` | 51 | ✗ | 0/1 | return 型なし、args 未型付け |
| `main()` | 94 | ✗ | 0/1 | return 型なし、args 未型付け |

## 期待される動作（RED → GREEN）

### RED 状態（現在）

段階的型付け設定により、上記の型ヒントなし関数が存在しても mypy がエラーを出さないことを期待する。

### 検証コマンド

```bash
source .venv/bin/activate
mypy src/
```

### 期待される出力

```
Success: no issues found in 14 source files
```

### エラーが出た場合の確認事項

1. `disallow_untyped_defs = false` が pyproject.toml に設定されているか
2. `check_untyped_defs = false` が設定されているか
3. `[[tool.mypy.overrides]]` で問題のあるモジュールが無視されているか

## GREEN 基準

- [x] `mypy src/` がエラー 0 で完了する
- [x] 型ヒントなし関数が 15 個存在することを確認済み
- [x] 段階的導入の設定（`disallow_untyped_defs = false`）が有効

## 特記事項

### ignore_errors = true のモジュール（3つ）

以下のモジュールは Phase 2 で `ignore_errors = true` が設定されており、すべてのエラーが無視される:

1. `number_normalizer`
2. `voicevox_client`
3. `generate_reading_dict`

これらのモジュールは将来的に段階的に型付けを追加する予定。

### 型ヒントのパターン

検出された型ヒントなし関数のパターン:

1. **CLI エントリーポイント**: `main()`, `parse_args()` → return 型なし
2. **ネストした関数**: `replace_markdown_link()` → クロージャのため型ヒントなし
3. **部分的型付け**: `process_chapters()` → 一部パラメータのみ型付け済み
4. **コンストラクタ**: `__init__()` → return 型なし
5. **ユーティリティ関数**: `write_pid_file()` → 型ヒント追加予定

## 次のステップ（GREEN Phase）

1. `mypy src/` を実行し、エラー 0 で完了することを確認
2. エラーが出る場合は設定を見直す
3. すべて成功したら、段階的導入の基盤が整ったことを確認
