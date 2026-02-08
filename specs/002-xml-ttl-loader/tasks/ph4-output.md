# Phase 4 Output

## 作業概要
- パイプライン統合 の実装完了
- FAIL テスト 20 件を PASS させた
- XML から音声生成までの完全なパイプラインを構築

## 修正ファイル一覧
- `src/xml_pipeline.py` - 新規作成（コマンドラインインターフェース実装）
- `specs/002-xml-ttl-loader/tasks.md` - タスク進捗更新

## 実装内容

### src/xml_pipeline.py

#### parse_args() 関数
- argparse ベースのコマンドライン引数パーサー
- 必須引数: `--input` / `-i` (入力 XML ファイル)
- オプション引数とデフォルト値:
  - `--output` / `-o`: デフォルト `./output`
  - `--start-page`: デフォルト 1
  - `--end-page`: デフォルト None
  - `--style-id`: デフォルト 13
  - `--speed`: デフォルト 1.0
  - `--voicevox-dir`: デフォルト `./voicevox_core_cuda`
  - `--max-chunk-chars`: デフォルト 500

#### main() 関数
統合された処理フロー:
1. 引数パース
2. ファイル存在チェック (FileNotFoundError)
3. `xml_parser.parse_book_xml()` で XML パース (ParseError)
4. ページ範囲フィルタリング
5. `xml_parser.to_page()` で Page オブジェクトに変換
6. `text_cleaner.init_for_content()` で辞書初期化
7. `text_cleaner.clean_page_text()` でテキストクリーニング
8. ハッシュベースの出力ディレクトリ生成
9. クリーニング済みテキストの保存
10. VoicevoxSynthesizer 初期化
11. `pipeline.process_pages()` で音声生成

#### エラーハンドリング
- ファイル不存在: `FileNotFoundError` with ファイルパス
- 無効な XML: `xml.etree.ElementTree.ParseError` が raise される
- 空ファイル: ParseError
- XML でない内容: ParseError

## テスト結果

### 全テスト PASS
```
225 passed in 0.18s
```

### Phase 4 テスト内訳
- `test_parse_args_requires_input` - 必須引数チェック ✅
- `test_parse_args_accepts_input_long` - --input 受付 ✅
- `test_parse_args_accepts_input_short` - -i 短縮形 ✅
- `test_output_default` - デフォルト値確認 ✅
- `test_start_page_default` - デフォルト値確認 ✅
- `test_end_page_default` - デフォルト値確認 ✅
- `test_style_id_default` - デフォルト値確認 ✅
- `test_speed_default` - デフォルト値確認 ✅
- `test_voicevox_dir_default` - デフォルト値確認 ✅
- `test_output_custom` - カスタム値設定 ✅
- `test_output_short` - -o 短縮形 ✅
- `test_start_page_custom` - カスタム値設定 ✅
- `test_end_page_custom` - カスタム値設定 ✅
- `test_style_id_custom` - カスタム値設定 ✅
- `test_speed_custom` - カスタム値設定 ✅
- `test_voicevox_dir_custom` - カスタム値設定 ✅
- `test_file_not_found_raises_error` - エラーハンドリング ✅
- `test_file_not_found_error_message` - エラーメッセージ ✅
- `test_invalid_xml_raises_parse_error` - XML エラー ✅
- `test_empty_file_raises_error` - 空ファイルエラー ✅
- `test_non_xml_content_raises_error` - 非 XML エラー ✅

### レグレッションテスト
- US1 (Phase 2): 全テスト PASS ✅
- US2 (Phase 3): 全テスト PASS ✅

## 注意点

### 次 Phase で必要な情報
- **Phase 5 (Polish)**: ドキュメント整備、最終確認
- T065 (Manual test) は VOICEVOX 環境が必要 - スキップ可能
- quickstart.md の例が正しく動作することを確認

### 設計決定事項
1. **init_for_content() の呼び出し**: Page 変換後、クリーニング前に実行
   - 理由: LLM 辞書のハッシュ計算に元テキストが必要
2. **clean_page_text() の個別適用**: ページごとにクリーニング
   - 理由: 既存の split_into_pages() パターンに準拠
3. **出力ディレクトリ**: ハッシュベース (`output/{hash}/`)
   - 理由: 既存パイプラインとの一貫性
4. **クリーニング済みテキスト保存**: `cleaned_text.txt`
   - 理由: デバッグ用、既存パイプラインと同じ

## 実装のミス・課題

### 検出された問題
なし

### 潜在的な改善点
1. **進捗表示**: 既存の ProgressTracker が process_pages() 内で使用されている
2. **エラーメッセージ**: より詳細な XML パースエラー情報を提供できる可能性
3. **ページ範囲指定**: --start-page と --end-page の境界チェックは未実装
   - 例: --end-page が総ページ数を超える場合の警告

### 技術的負債
なし - クリーンな実装、既存コードとの統合も問題なし

## 次のステップ

### T065: Manual Test (OPTIONAL)
VOICEVOX 環境がセットアップされている場合:
```bash
python src/xml_pipeline.py -i sample/book.xml --end-page 3
```

期待される出力:
```
output/{hash}/
├── cleaned_text.txt
├── pages/
│   ├── page_0001.wav
│   ├── page_0002.wav
│   └── page_0003.wav
└── book.wav
```

### T066: Phase Output
完了 ✅ (このファイル)

## 成果物サマリー

| ファイル | 状態 | 説明 |
|---------|------|------|
| `src/xml_pipeline.py` | 新規 | コマンドライン TTS パイプライン (201 行) |
| `tests/test_xml_pipeline.py` | 既存 | Phase 4 RED テスト (20 tests) |
| `specs/002-xml-ttl-loader/tasks.md` | 更新 | T055-T064 完了マーク |
| `specs/002-xml-ttl-loader/tasks/ph4-output.md` | 新規 | このファイル |

## ステータス
✅ **Complete** - Phase 4 パイプライン統合完了
