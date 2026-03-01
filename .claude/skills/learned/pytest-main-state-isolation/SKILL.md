---
name: pytest-main-state-isolation
description: "Fix test suite hangs when testing main() functions that manage process state (PID files, atexit handlers, global singletons)"
---

# pytest-main-state-isolation

## Problem

テストスイートが以下の症状を示す:
- 個別テストは高速（< 1秒）
- フルスイート実行でハングまたは極端に遅い
- pytest-timeout が効かない

原因: main() 関数がプロセス状態を管理している
- PID ファイル作成/削除
- atexit.register() でクリーンアップ登録
- time.sleep() を含むプロセス管理
- グローバルシングルトン

## Solution

main() を呼び出すテストに状態分離フィクスチャを適用:

```python
import atexit
from unittest.mock import patch
import pytest

@pytest.fixture
def mock_pid_management(tmp_path):
    """PID管理とatexitをモック化してテスト間の状態分離を保証"""
    unique_pid_file = tmp_path / f"test_{id(tmp_path)}.pid"

    with (
        patch("src.your_module.get_pid_file_path", return_value=unique_pid_file),
        patch("src.your_module.kill_existing_process"),
        patch("src.your_module.write_pid_file"),
        patch("src.your_module.cleanup_pid_file"),
        patch.object(atexit, "register"),
    ):
        yield unique_pid_file
```

## Example

実際の適用例 (`tests/test_xml2_pipeline.py`):

```python
@pytest.fixture
def mock_pid_management(tmp_path):
    """Mock PID file management to prevent test interference."""
    unique_pid_file = tmp_path / f"test_pid_{id(tmp_path)}.pid"

    with (
        patch("src.xml2_pipeline.get_pid_file_path", return_value=unique_pid_file),
        patch("src.xml2_pipeline.kill_existing_process"),
        patch("src.xml2_pipeline.write_pid_file"),
        patch("src.xml2_pipeline.cleanup_pid_file"),
        patch.object(atexit, "register"),
    ):
        yield unique_pid_file


class TestMainFunction:
    def test_main_file_not_found_raises_error(self, mock_pid_management):
        # mock_pid_management フィクスチャにより状態が分離される
        with pytest.raises(FileNotFoundError):
            main(["--input", "/nonexistent/path.xml"])
```

## When to Use

- main() 関数のテストでスイート実行が遅い/ハングする
- PID ファイル、ロックファイル、atexit を使用するコードのテスト
- 個別テストは速いがフルスイートで問題が発生する場合
- `time.sleep()` を含むプロセス管理コードのテスト

## Diagnosis Steps

1. **実行時間比較**: 個別テスト vs フルスイート
   ```bash
   # 個別テスト
   pytest tests/test_foo.py::TestClass::test_method -v

   # フルスイート
   pytest tests/test_foo.py -v --durations=10
   ```

2. **状態管理コードを特定**: main() 内で以下を検索
   - `atexit.register()`
   - `time.sleep()`
   - PID/ロックファイル操作
   - グローバル変数への代入

3. **モック対象を決定**: 上記で見つかった関数をリストアップ

4. **フィクスチャ作成**: patch で状態管理をモック化

## Related Patterns

- pytest の `autouse=True` フィクスチャで全テストに自動適用
- `conftest.py` に配置してテストファイル間で共有
- `tmp_path` フィクスチャでテストごとにユニークなパスを生成
