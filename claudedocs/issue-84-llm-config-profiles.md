# Issue #84: ollama_chat() にリクエスト別パラメータ指定機能を追加

Parent: #54
Issue: https://github.com/rengotaku/text-reading-with-llm/issues/84

## 概要

`ollama_chat()` は現在 `temperature=0.3` でハードコードされており、全リクエストで共有されている。
用途別（読み辞書生成、対話生成、ナレーション等）に最適なパラメータを `config.yaml` から指定できるようにする。

## 設計

### config.yaml 追加セクション

```yaml
llm:
  model: gpt-oss:20b
  api_url: http://localhost:11434/api/chat
  timeout: 300
  defaults:
    temperature: 0.3
    num_predict: 4096
  profiles:
    reading_dict:
      temperature: 0.2
    dialogue:
      temperature: 0.5
      repeat_penalty: 1.2
    introduction:
      temperature: 0.4
    conclusion:
      temperature: 0.4
```

## 実装タスク

- [ ] `config.yaml` に `llm` セクション追加
- [ ] `src/llm_config.py`（新規）に `load_llm_profile(name)` 追加
- [ ] `src/generate_reading_dict.py:ollama_chat()` に `options` 引数追加
- [ ] `src/dialogue_converter.py` の呼び出し側で profile を適用
- [ ] 既存テストが壊れないこと確認
- [ ] 対話出力で品質改善確認
