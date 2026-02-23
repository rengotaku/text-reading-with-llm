# ポストモーテム: gen-dict と xml-tts のハッシュ不一致

**日付**: 2026-02-23
**影響**: 辞書が読み込まれない（サイレント障害）
**重大度**: Medium（機能は動作するが辞書適用されない）
**ステータス**: 対策検討中

## 概要

`make gen-dict INPUT=sample/book2.xml` で生成した辞書が、`make xml-tts` 実行時にロードされない。原因はハッシュ計算の入力が異なるため。

## タイムライン

| 日付 | イベント |
|------|---------|
| 2026-02-07 | 002-xml-ttl-loader: `xml2_pipeline.py` 実装。パース後テキストでハッシュ計算 |
| 2026-02-18 | 006-xml-dict-support: `generate_reading_dict.py` XML対応追加。生ファイルでハッシュ計算 |
| 2026-02-23 | 不一致発見 |

## 根本原因

### 直接原因

```python
# gen-dict (generate_reading_dict.py)
output_path = get_dict_path(input_path)
# → input_path.read_text() で生ファイル全体をハッシュ

# xml-tts (xml2_pipeline.py)
combined_text = " ".join(item.text for item in content_items)
content_hash = get_content_hash(combined_text)
# → パース後のテキストのみをハッシュ
```

→ **異なる入力 → 異なるハッシュ → 辞書が見つからない**

### 根本原因

1. **仕様の曖昧さ**: 006-xml-dict-support の spec.md FR-005 に「入力ファイルのコンテンツハッシュ」と記載されているが、「コンテンツ」の定義が曖昧
   - 生ファイル？パース後テキスト？

2. **実装の不整合**:
   - `xml2_pipeline.py`（先行実装）: パース後テキストでハッシュ
   - `generate_reading_dict.py`（後発実装）: 生ファイルでハッシュ
   - 後発実装が先行実装のハッシュ方式を確認せず独自に実装

3. **テストの不足**:
   - gen-dict → xml-tts の統合テストがない
   - 辞書ロード確認テストがない（サイレント失敗）

## 影響範囲

- **影響**: XML入力時、LLM辞書が適用されない
- **影響を受けたユーザー操作**: `make gen-dict INPUT=*.xml` → `make xml-tts`
- **検出方法**: 読み上げ結果の確認（目視/聴取）
- **サイレント障害**: ログに "No LLM dictionary found" と出るのみ

## 教訓

### うまくいかなかったこと

1. **ハッシュ計算の一貫性確認がない**: 複数箇所で同じハッシュを参照する場合、一貫性を保証する仕組みがなかった
2. **統合テストの不足**: gen-dict → xml-tts のEnd-to-Endテストがない
3. **仕様の曖昧さ**: 「コンテンツハッシュ」の定義が明確でなかった

### うまくいったこと

- 個別機能のユニットテストは存在した
- ログに "No LLM dictionary found" が出力されていた（ただし見落としやすい）

## 対策

### 短期対策（今すぐ）

| 対策 | 優先度 | 実装コスト |
|------|--------|-----------|
| A1: gen-dict のハッシュを xml-tts に合わせる | High | Low |
| A2: ハッシュ計算を `dict_manager.py` に一元化 | High | Medium |

**推奨**: A2 - 一元化により将来の不整合を防止

### 中期対策（Issue #14 と統合）

| 対策 | 優先度 |
|------|--------|
| B1: 統合テスト追加（gen-dict → xml-tts） | High |
| B2: 辞書ロード確認の明示的ログ/警告 | Medium |
| B3: Makefile の `make run` でパイプライン一貫性保証 | Medium |

### 長期対策（プロセス改善）

| 対策 | 説明 |
|------|------|
| C1: 仕様テンプレートに「共有状態」セクション追加 | ハッシュ、ファイルパスなど共有状態の定義を必須化 |
| C2: Cross-reference チェックリスト | 既存実装との整合性確認を明示的に要求 |
| C3: サイレント失敗のログレベル見直し | WARNING → ERROR or 明示的エラー |

## 関連Issue

- #14: xml2_pipeline を分割し、Makefile から各ステップを個別実行可能にする
- #15: gen-dict と xml-tts のハッシュ計算を一元化（本ポストモーテムの対策）

## アクションアイテム

- [ ] A2: ハッシュ計算を `dict_manager.py` に一元化
- [ ] B1: 統合テスト追加
- [ ] C3: 辞書ロード失敗時の警告強化
