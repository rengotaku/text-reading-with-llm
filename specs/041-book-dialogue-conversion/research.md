# Research: 書籍内容の対話形式変換

**Branch**: `041-book-dialogue-conversion`
**Date**: 2026-03-13

## 1. LLMモデル選択

### Decision: gpt-oss:20b

### Rationale
Issue#51での検証結果に基づき、gpt-oss:20bを採用:
- 対話形式の生成品質が高い
- 内容の正確性が維持される
- ローカルOllamaで実行可能

### Alternatives Considered

| モデル | 対話形式 | 内容正確性 | 備考 |
|--------|---------|-----------|------|
| gpt-oss:20b | ✅ | ✅ | **採用** |
| Llama-3-ELYZA-JP:8B | ✅ | ✅ | 軽量代替（リソース制約時） |
| gpt-oss-swallow:20b | △ | ❌ | 内容歪みが大きい |

## 2. LLM処理戦略（2段階）

### Decision: 構造分析 → 対話生成の2段階処理

### Rationale
単一プロンプトでは長文処理時にコンテキストが失われる。2段階に分けることで:
- Step 1で全体構造を把握
- Step 2で対話品質に集中

### Step 1: 構造分析

```text
入力: セクション内の段落群
出力: introduction / dialogue / conclusion の分類

プロンプト概要:
- 導入部（背景説明、定義）を特定
- 本論（詳細説明、例示）を対話候補に
- 結論（まとめ、要点）を特定
```

### Step 2: 対話生成

```text
入力: dialogue部分 + 導入・結論（参考情報）
出力: A（博士）/ B（助手）の対話形式テキスト

プロンプト概要:
- A（博士）: 内容を説明する立場
- B（助手）: 疑問を投げかける、相槌を打つ
- 元の内容の要点を維持（80%以上カバー目標）
```

### Alternatives Considered
- 1段階処理: 長文で品質低下
- 3段階以上: オーバーエンジニアリング

## 3. 長文分割戦略

### Decision: 4,000文字で見出し単位分割

### Rationale
検証結果:
- 800文字: 5秒で処理 ✅
- 1,200文字: 23秒で処理 ✅
- 3,500文字: 237秒で処理 ✅
- 4,000文字超: 品質低下のリスク

### Implementation
- 3,500文字以内: そのまま処理
- 4,000文字超: subsection/heading単位で分割
- 分割点: 既存のXML構造（subsection, heading）を活用
- num_predict: 1500〜2000推奨

### Alternatives Considered
- 文単位分割: コンテキスト断絶
- 固定文字数分割: 文脈無視の分割点

## 4. VOICEVOX話者割り当て

### Decision: 3話者構成

| 話者 | 役割 | キャラクター | style_id |
|------|------|-------------|----------|
| narrator | 導入・結論 | 青山龍星 | 13 |
| A | 博士（説明役） | 麒ヶ島宗麟 | 67 |
| B | 助手（質問役） | 四国めたん | 2 |

### Rationale
- narrator: 既存パイプラインと同じ青山龍星で一貫性維持
- A（博士）: 落ち着いた男性声で説明
- B（助手）: 明るい女性声で質問

### Alternatives Considered
- 2話者のみ: 導入/結論の読み上げが不自然
- 4話者以上: 複雑化、リスナーの混乱

## 5. 出力XML構造

### Decision: dialogue-section構造

```xml
<section number="1.1" title="セクションタイトル">
  <introduction speaker="narrator">
    導入テキスト...
  </introduction>
  <dialogue>
    <utterance speaker="A">博士の発言...</utterance>
    <utterance speaker="B">助手の発言...</utterance>
    <utterance speaker="A">博士の発言...</utterance>
    ...
  </dialogue>
  <conclusion speaker="narrator">
    結論テキスト...
  </conclusion>
</section>
```

### Rationale
- 既存のXML構造（chapter/section）を維持
- 話者情報を属性として保持
- TTSパイプラインでの処理が容易

## 6. 既存モジュールとの連携

### Decision: 並行パイプライン方式

```text
既存: xml_pipeline.py (1話者)
新規: dialogue_pipeline.py (3話者)

共通利用:
- voicevox_client.py (変更なし)
- text_cleaner.py (変更なし)
- xml_parser.py (変更なし)
```

### Rationale
- 既存機能を壊さない
- 段階的な導入が可能
- Makefileで両方のパイプラインを選択可能に

## 7. Makefile統合

### Decision: dialogue ターゲット追加

```makefile
dialogue: dialogue-convert gen-dict clean-text dialogue-tts

dialogue-convert:  # LLMで対話形式XMLに変換
gen-dict:          # 既存: 読み辞書生成
clean-text:        # 既存: テキスト正規化
dialogue-tts:      # 新規: 複数話者TTS生成
```

### Rationale
- 既存のrunターゲットと並列に提供
- 各ステップを独立して実行可能
