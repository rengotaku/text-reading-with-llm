# Phase 2 Output: User Story 1 - テスト設定の標準化

**Date**: 2026-03-02
**Status**: Completed
**User Story**: US1 - テスト設定の標準化

## Executed Tasks

- [x] T006 前フェーズ出力を読む: specs/016-dev-env-optimization/tasks/ph1-output.md
- [x] T007 [US1] pyproject.toml に `[tool.pytest.ini_options]` セクションを追加
- [x] T008 [US1] カバレッジ閾値を設定: `--cov-fail-under=70`
- [x] T009 [US1] XML レポート出力を追加: `--cov-report=xml:coverage.xml`
- [x] T010 `pytest` を実行し、カバレッジレポートが表示されることを確認
- [x] T011 カバレッジ閾値の動作確認
- [x] T012 作成: specs/016-dev-env-optimization/tasks/ph2-output.md

## Changed Files

| File | Change Type | Summary |
|------|-------------|---------|
| pyproject.toml | Modified | `[tool.pytest.ini_options]` セクションを追加 |
| coverage.xml | New | カバレッジ XML レポート（pytest 実行時自動生成） |

## Implementation Details

### pyproject.toml 変更内容

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
addopts = [
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=xml:coverage.xml",
    "--cov-fail-under=70",
]
```

**設定説明**:
- `testpaths`: テストディレクトリを `tests/` に明示
- `pythonpath`: PYTHONPATH=. を設定（CI との一貫性）
- `--cov=src`: src/ ディレクトリのカバレッジを計測
- `--cov-report=term-missing`: ターミナルに未カバー行を表示
- `--cov-report=xml:coverage.xml`: XML レポートを生成（CI 用）
- `--cov-fail-under=70`: カバレッジ閾値 70%（現在 72%）

### 閾値を 70% に設定した理由

Phase 1 の分析により、現在のカバレッジは 72% であることが判明。
- 当初計画: 80% 閾値
- 実際の設定: 70% 閾値
- 理由: 既存テストを失敗させずに段階的に改善するため、現在値より少し低めに設定

## Test Results

```
============================= 509 passed in 1.56s ==============================
================================ tests coverage ================================
_______________ coverage: platform linux, python 3.13.11-final-0 _______________

Name                            Stmts   Miss  Cover   Missing
-------------------------------------------------------------
src/chapter_processor.py          152     17    89%   108, 146-147, 149-150, ...
src/dict_manager.py                78     41    47%   68, 84-85, 105, 107, ...
src/generate_reading_dict.py      126     43    66%   35-55, 78-143, ...
src/llm_reading_generator.py       69     31    55%   97-144, 149-152, ...
src/mecab_reader.py                44     11    75%   84-100
src/number_normalizer.py          118     38    68%   209, 247, 250, ...
src/process_manager.py             40     31    22%   25-30, 42-71, 80-81, 90-91
src/punctuation_normalizer.py      96     35    64%   95-97, 228-259, ...
src/reading_dict.py                 9      0   100%
src/text_cleaner.py               151     36    76%   127, 150-154, 293, ...
src/text_cleaner_cli.py            64      5    92%   152-156
src/voicevox_client.py            148     57    61%   88-90, 97, 123-141, ...
src/xml2_parser.py                 97      4    96%   79, 140-141, 190
src/xml2_pipeline.py              104     16    85%   125-126, 169, 196-202, ...
-------------------------------------------------------------
TOTAL                            1296    365    72%
Coverage XML written to file coverage.xml
Required test coverage of 70% reached. Total coverage: 71.84%
```

**Coverage**: 72% (target: 70%) ✅

### 閾値動作確認

```bash
# 閾値 70%: PASS ✅
$ pytest -q
Required test coverage of 70% reached. Total coverage: 71.84%
509 passed in 1.56s

# 閾値 80%: FAIL ❌
$ pytest --cov-fail-under=80 -q
ERROR: Coverage failure: total of 72 is less than fail-under=80
FAIL Required test coverage of 80% not reached. Total coverage: 71.84%
509 passed in 1.55s
```

閾値チェックが正常に動作することを確認。

## Discovered Issues

なし。全タスクが計画通りに完了。

## Handoff to Next Phase

### Phase 3 (User Story 2 - CI でのカバレッジ可視化):

前提条件（Phase 2 で完了）:
- ✅ `coverage.xml` が pytest 実行時に自動生成される
- ✅ pyproject.toml にカバレッジ設定が記述されている

実装項目:
- `.github/workflows/ci.yml` に permissions セクションを追加
- pytest ステップでカバレッジ設定を適用（pyproject.toml から継承）
- `py-cov-action/python-coverage-comment-action` ステップを追加

注意事項:
- CI では既に `PYTHONPATH=. pytest tests/ --forked --tb=short -q` を実行中
- pyproject.toml の addopts が自動適用されるため、pytest コマンドの引数調整が必要
- 既存の `--forked --tb=short -q` オプションは維持すること
