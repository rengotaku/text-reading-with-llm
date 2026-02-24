# Research: VOICEVOX style_id to VVM Mapping

**Date**: 2026-02-24
**Feature**: 012-vvm-load-optimization

## 調査結果

### style_id と VVM ファイルの関係

**重要な発見**: VVM ファイル番号（0.vvm, 1.vvm, ...）は style_id と直接対応しない

- **VVM ファイル番号** = Voice Model ID（キャラクター/話者を識別）
- **style_id** = 特定の話し方スタイル（通常、喜び、怒りなど）
- 各 VVM ファイルには 1 人の話者と複数のスタイルが含まれる

### VOICEVOX Core の内部動作

1. `synthesizer.create_audio_query(text, style_id)` を呼ぶと：
   - Core がロード済みの全 VVM ファイルを検索
   - 該当する style_id を含む VVM を特定
   - その VVM モデルで音声合成を実行

2. マッピング情報は VVM ファイル内のメタデータに格納
   - `synthesizer.get_metas()` でスピーカー情報を取得可能
   - 各スピーカーに紐づく style_id のリストが得られる

### 実装アプローチ

#### 決定: 静的マッピング（コード内定義）

VVM 0.16.x での主要な style_id → VVM ファイル対応：

| style_id | 話者名 | スタイル | VVM ファイル |
|----------|--------|----------|--------------|
| 0-1 | 四国めたん | あまあま/ノーマル | 0.vvm |
| 2-3 | ずんだもん | ノーマル/あまあま | 1.vvm |
| 4-5 | 春日部つむぎ | ノーマル | 2.vvm |
| 6-7 | 雨晴はう | ノーマル | 3.vvm |
| 8 | 波音リツ | ノーマル | 4.vvm |
| 9-10 | 玄野武宏 | ノーマル/喜び | 5.vvm |
| 11 | 白上虎太郎 | ふつう | 6.vvm |
| 12 | 青山龍星 | ノーマル | 13.vvm |
| 13 | 青山龍星 | ノーマル | 13.vvm |
| ... | ... | ... | ... |

**注意**: 完全なマッピングは実装時に `get_metas()` で動的に取得して確定する

### バージョン不一致解消

- 現状: VVM ファイル 0.16.1 vs Core 0.16.3
- 解決策: VVM ファイルを Core 0.16.3 に合わせて再ダウンロード
- コマンド: `make setup-voicevox` で再取得

## 参考資料

- VOICEVOX/voicevox_core GitHub Issues #548
- VOICEVOX Core Usage Documentation
- プロジェクト内 src/voicevox_client.py 実装
