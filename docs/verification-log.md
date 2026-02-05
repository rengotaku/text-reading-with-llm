# TTS Pipeline Verification Log

## Date: 2025-02-05

## 1. Environment Check

| Item | Status | Details |
|------|--------|---------|
| Python | OK | 3.13 (.venv) |
| qwen-tts | OK | 0.0.5 |
| torch | OK | 2.10.0 + torchaudio 2.10.0 |
| soundfile | OK | 0.13.1 |
| GPU | OK | RTX 4080 SUPER (16GB VRAM, ~12GB free) |

## 2. Sample Data Validation

- `sample/book.md`: 248 pages detected
- Page marker format: `--- Page N (page_NNNN.png) ---` -- regex in `text_cleaner.py` matches correctly
- Text cleaning verified: HTML comments, figure descriptions, page numbers, markdown markers all removed

## 3. API Verification

### `Qwen3TTSModel.from_pretrained`
- kwargs forwarded to `AutoModel.from_pretrained`
- `dtype=` is the correct parameter name (qwen-tts wraps HuggingFace and remaps internally)
- `device_map=` correctly sets GPU device

### `generate_custom_voice`
- Signature: `(text, speaker, language=None, instruct=None, non_streaming_mode=True, **kwargs)`
- Returns: `Tuple[List[np.ndarray], int]` (list of waveforms, sample_rate)
- Code correctly accesses `wavs[0]` from result

## 4. Test Run: Page 4 (single page)

```
Command: PYTHONPATH=$(pwd) .venv/bin/python src/pipeline.py sample/book.md -o output_test --start-page 4 --end-page 4
```

### Results
- Text split into 3 chunks (441, 469, 361 chars)
- Total processing time: 142.9s for 1 page
- Output: `output_test/pages/page_0004.wav` (12MB) + `output_test/book.wav` (12MB)

### Audio File Validation
| File | Sample Rate | Duration | Samples | Amplitude Range |
|------|-------------|----------|---------|-----------------|
| page_0004.wav | 24000 Hz | 246.5s | 5,915,220 | [-0.4766, 0.2969] |
| book.wav | 24000 Hz | 247.0s | 5,927,220 | [-0.4766, 0.2969] |

- book.wav is page_0004.wav + 0.5s silence (12,000 samples at 24kHz)
- Amplitude range is healthy (not clipped, not silent)

## 5. Progress Tracking Feature (Added 2025-02-05)

### New Files
- `src/progress.py` — `ProgressTracker` class for real-time ETA calculation

### Implementation
- Pre-compute all chunks before processing for accurate ETA
- Track chars/second processing speed
- Recalculate ETA after each chunk completion

### Output Format
```
[Progress] Starting: 2 pages, 7 chunks, 2943 chars total
[Progress] Chunk 1/7 | Page 1/2 | Elapsed: 48s | ETA: 4m 37s | Speed: 9 chars/s
[Progress] Chunk 2/7 | Page 1/2 | Elapsed: 1m 34s | ETA: 3m 31s | Speed: 10 chars/s
[Progress] Page 1/2 done (138.4s) | Elapsed: 2m 18s | ETA: 3m 2s
...
[Progress] Complete! 2 pages in 5m 12s (avg 9 chars/s)
```

### Test Run: Pages 4-5 (2 pages, 7 chunks)
- Processing speed: ~9 chars/s (consistent)
- Total time: 5m 12s for 2943 chars
- ETA accuracy: Good — predictions converged as processing progressed

## 6. Reading Dictionary Feature (Added 2025-02-05)

### Problem
TTS models may mispronounce technical terms (e.g., "SRE" as "エスアールエー" instead of "エスアールイー").

### Solution
Created `src/reading_dict.py` with regex-based reading rules for technical terms.

### New Files
- `src/reading_dict.py` — Reading rules dictionary with `apply_reading_rules()` function

### Modified Files
- `src/text_cleaner.py` — Integrated reading rules into `clean_page_text()`

### Technical Note
Used `(?<![A-Za-z])TERM(?![A-Za-z])` pattern instead of `\b` word boundaries because `\b` doesn't work correctly with Japanese text (no spaces between words).

### Sample Conversions
| Original | Converted |
|----------|-----------|
| SRE | エスアールイー |
| SLO | エスエルオー |
| Google | グーグル |
| Kubernetes | クーバネティス |
| CI/CD | シーアイシーディー |
| API | エーピーアイ |
| GitHub | ギットハブ |
| PR | プルリクエスト |

### Coverage
- SRE/DevOps terms (SRE, SLO, SLI, SLA, DevOps, CI/CD, etc.)
- Cloud providers (AWS, GCP, Azure, etc.)
- IT terms (API, HTTP, DNS, SQL, etc.)
- Development tools (Git, GitHub, Docker, Kubernetes, etc.)
- Companies (Google, Amazon, Microsoft, etc.)

## 7. LLM-Based Dictionary Generation (Added 2025-02-05)

### Approach B: Term Extraction → Dictionary Generation
Instead of real-time LLM calls, generate a reading dictionary once using LLM.

### New Files
- `src/llm_reading_generator.py` — LLM-based reading generation utilities
- `src/generate_reading_dict.py` — CLI tool for dictionary generation
- `data/llm_reading_dict.json` — Generated dictionary (275 entries)

### Generation Command
```bash
PYTHONPATH=$(pwd) python src/generate_reading_dict.py sample/book.md --model gpt-oss:20b
```

### Results
- Extracted: 522 unique technical terms
- Generated: 275 readings (53% success rate)
- Processing time: ~18 minutes (21 batches × 25 terms)
- Some batches failed JSON parsing

### Hybrid Architecture
Two-layer dictionary system for robustness:
1. **Static dictionary** (`reading_dict.py`) — Critical terms (SRE, API, AWS, etc.)
2. **LLM dictionary** (`llm_reading_dict.json`) — Additional terms (Blue-Green, Linux, etc.)

### Sample Output
```
Input:  SREの知識地図、Blue-Greenデプロイメント
Output: エスアールイーの知識地図、ブルー・グリーンデプロイメント
```

### Adding New Terms
```bash
# Re-run with --merge to add new terms
python src/generate_reading_dict.py sample/new_book.md --model gpt-oss:20b --merge
```

## 8. MeCab Kanji → Kana Conversion (Added 2025-02-05)

### Purpose
Ensure TTS correctly pronounces all kanji by converting to katakana readings.

### Dependencies
- `fugashi` — MeCab Python wrapper
- `unidic-lite` — Lightweight UniDic dictionary

### New Files
- `src/mecab_reader.py` — MeCab-based kanji to kana conversion

### Processing Pipeline
```
Original:  SREの知識地図、信頼性を定義する
    ↓ Static Dict (SRE, etc.)
Step 1:    エスアールイーの知識地図、信頼性を定義する
    ↓ LLM Dict
Step 2:    エスアールイーの知識地図、信頼性を定義する
    ↓ MeCab
Final:     エスアールイーのチシキチズ、シンライセイをテイギする
```

### Configuration
In `src/text_cleaner.py`:
```python
ENABLE_KANJI_CONVERSION = True  # Set to False to disable
```

### Notes
- Newlines are preserved (line-by-line processing)
- Only kanji is converted; hiragana/katakana/ASCII remain unchanged
- Lazy initialization of MeCab tagger for performance

## 9. Issues Found & Fixed

### dtype parameter (reverted)
- Initially changed `dtype=` to `torch_dtype=` based on HuggingFace convention
- qwen-tts 0.0.5 uses its own `dtype` kwarg and warns if `torch_dtype` is used
- Reverted to original `dtype=torch_dtype`

### Page index display bug (fixed)
- Chunk progress was showing actual page number (e.g., "Page 4/2") instead of index
- Fixed to show "Page 1/2" (current page index / total pages)

### No other code changes needed
- Pipeline code is functional as-is
- Import requires `PYTHONPATH=$(CURDIR)` (handled by Makefile)

## 10. Hash-Based Per-Book Dictionary (Added 2025-02-05)

### Problem
LLM-generated dictionaries were global, not per-book. Different books may need different readings for the same terms.

### Solution
Use content hash (SHA256) to uniquely identify each book and store dictionaries with hash-based filenames.

### New Files
- `src/dict_manager.py` — Hash-based dictionary path management

### Architecture
```
data/readings/
├── 72a2534e9e81.json   ← sample/book.md (hash: 72a2534e9e81)
├── abc123def456.json   ← another_book.md
└── ...
```

### Key Functions
```python
get_content_hash(content: str) -> str        # SHA256[:12]
get_dict_path(input_path: Path) -> Path      # file → hash → path
get_dict_path_from_content(content: str)     # content → hash → path
load_dict_from_content(content: str)         # Auto-load by content hash
```

### Workflow
1. `generate_reading_dict.py sample/book.md` → `data/readings/{hash}.json`
2. `pipeline.py sample/book.md` → auto-loads matching dictionary by hash

### Modified Files
- `src/text_cleaner.py` — Added `init_for_content()` for hash-based loading
- `src/pipeline.py` — Calls `init_for_content(markdown)` before processing
- `src/generate_reading_dict.py` — Uses hash-based paths by default

### Test Results
```
Input:  SREの知識地図、Blue-Greenデプロイメント
Output: エスアールイーのチシキチズ、ブルー・グリーンデプロイメント
```
Dictionary `data/readings/72a2534e9e81.json` (275 entries) auto-loaded successfully.

## 11. Audio Normalization (Added 2025-02-05)

### Problem
Each chunk's audio starts quietly due to TTS model behavior. When chunks are concatenated, volume varies throughout the page.

### Solution
Apply peak normalization to each chunk after TTS generation.

### Implementation
- Added `normalize_audio()` function in `src/tts_generator.py`
- Applied normalization (target peak: 0.9) after each chunk in `src/pipeline.py`

### Results
| Metric | Before | After |
|--------|--------|-------|
| Peak | 0.48 | **0.90** |
| RMS | 0.04 | **0.11** (3x louder) |

Audio is now consistently at 90% peak level throughout the file.

## 12. Punctuation Normalization (Added 2025-02-05)

### Problem
TTS reads long modifier phrases without pause, making speech unnatural.
```
Before: 日本国内初のSREに関するテックカンファレンス (one breath)
```

### Solution
Rule-based punctuation insertion using regex patterns.

### Implementation
- `src/punctuation_normalizer.py` — Pattern-based comma insertion
- Patterns: 〜に関する、〜における、〜による、〜のための、etc.
- Condition: Only insert comma if 8+ characters precede the pattern

### Processing Order
```
Markdown除去 → 読点挿入 → 静的辞書 → LLM辞書 → MeCab
```

### Results
```
Before: 日本国内初のSREに関するテックカンファレンス
After:  日本国内初のSREに関する、テックカンファレンス
```

Short phrases like "問いへの回答" remain unchanged (no unnecessary commas).

## 13. Conclusion

Pipeline is fully functional. Audio files are generated correctly from markdown input.

### Processing Pipeline
```
markdown → pages → text_cleaner:
  1. Static dict (SRE, API, AWS...)
  2. LLM dict (hash-based, per-book)
  3. MeCab (kanji → katakana)
→ TTS → audio files
```

### Usage
```bash
# Generate reading dictionary (one-time per book)
PYTHONPATH=$(pwd) python src/generate_reading_dict.py sample/book.md --model gpt-oss:20b

# Full book (all 248 pages)
make run

# Specific page range
make run INPUT=sample/book.md START_PAGE=4 END_PAGE=10
```
