# Phase 3 RED Tests

## Summary
- Phase: Phase 3 - User Story 2 (読み上げ不要な要素をスキップする)
- FAIL tests: 2
- Test file: tests/test_xml_parser.py

## FAIL Test List

| Test File | Test Method | Expected Behavior |
|-----------|-------------|-------------------|
| tests/test_xml_parser.py | TestSkipReadAloudFalseElement::test_skip_paragraph_with_read_aloud_false | `readAloud="false"` の paragraph はスキップされる |
| tests/test_xml_parser.py | TestSkipReadAloudFalseElement::test_skip_heading_with_read_aloud_false | `readAloud="false"` の heading はスキップされる |

## PASS Tests (Already Working)

| Test File | Test Method | Status | Note |
|-----------|-------------|--------|------|
| tests/test_xml_parser.py | TestSkipReadAloudFalseElement::test_include_paragraph_without_read_aloud | PASS | readAloud 属性なしは抽出される |
| tests/test_xml_parser.py | TestSkipReadAloudFalseElement::test_include_heading_without_read_aloud | PASS | readAloud 属性なしは抽出される |
| tests/test_xml_parser.py | TestSkipPageMetadata::test_page_metadata_not_in_content_text | PASS | pageMetadata は content 外 |
| tests/test_xml_parser.py | TestSkipPageMetadata::test_page_metadata_not_in_to_page_output | PASS | pageMetadata は content 外 |
| tests/test_xml_parser.py | TestSkipPageMetadata::test_chapter_page_metadata_not_in_output | PASS | pageMetadata は content 外 |
| tests/test_xml_parser.py | TestExtractFigureDescriptionWhenOptional::test_figure_description_extracted_when_optional | PASS | to_page() で既に実装済み |
| tests/test_xml_parser.py | TestExtractFigureDescriptionWhenOptional::test_figure_description_skipped_when_false | PASS | to_page() で既に実装済み |
| tests/test_xml_parser.py | TestSkipFigureFilePath::test_file_path_not_in_to_page_output | PASS | file_path は出力に含まれない設計 |
| tests/test_xml_parser.py | TestSkipFigureFilePath::test_skip_figure_file_path_not_in_content | PASS | file_path は content 外 |
| tests/test_xml_parser.py | TestIgnoreXmlComments::test_xml_comment_not_in_content_text | PASS | ElementTree が自動処理 |
| tests/test_xml_parser.py | TestIgnoreXmlComments::test_xml_comment_not_in_to_page_output | PASS | ElementTree が自動処理 |
| tests/test_xml_parser.py | TestIgnoreXmlComments::test_xml_comment_not_in_announcement | PASS | ElementTree が自動処理 |

## Implementation Hints

### Required Changes

1. **`_extract_content_text(content_elem)` in `src/xml_parser.py`**:
   - Check `readAloud` attribute on each child element (paragraph, heading)
   - Skip elements where `readAloud="false"`
   - Include elements where `readAloud` is missing, `"true"`, or `"optional"`

### Helper Function (Recommended)

```python
def _should_read_aloud(elem) -> bool:
    """Check if element should be read aloud based on readAloud attribute.

    Returns True if:
    - readAloud attribute is missing (default: read)
    - readAloud="true"
    - readAloud="optional"

    Returns False if:
    - readAloud="false"
    """
    read_aloud = elem.get("readAloud", "true")
    return read_aloud != "false"
```

### Update `_extract_content_text()`

```python
def _extract_content_text(content_elem) -> str:
    texts = []
    for child in content_elem:
        if not _should_read_aloud(child):  # Add this check
            continue
        if child.tag == "paragraph":
            if child.text:
                texts.append(child.text)
        elif child.tag == "heading":
            if child.text:
                texts.append(child.text)
        elif child.tag == "list":
            for item in child.findall("item"):
                if item.text:
                    texts.append(item.text)
    return "\n".join(texts)
```

## FAIL Output Example

```
FAILED tests/test_xml_parser.py::TestSkipReadAloudFalseElement::test_skip_paragraph_with_read_aloud_false
AssertionError: Paragraph with readAloud='false' should be skipped: got 'この段落は読み上げない。
この段落は読み上げる。
この見出しは読み上げない
この見出しは読み上げる'

FAILED tests/test_xml_parser.py::TestSkipReadAloudFalseElement::test_skip_heading_with_read_aloud_false
AssertionError: Heading with readAloud='false' should be skipped: got 'この段落は読み上げない。
この段落は読み上げる。
この見出しは読み上げない
この見出しは読み上げる'

======================== 2 failed, 202 passed in 0.13s =========================
```

## Test Details

### TestSkipReadAloudFalseElement (4 tests)

Tests content element filtering based on `readAloud` attribute.

| Test | Assertion | Status |
|------|-----------|--------|
| test_skip_paragraph_with_read_aloud_false | `"この段落は読み上げない" not in content_text` | FAIL |
| test_skip_heading_with_read_aloud_false | `"この見出しは読み上げない" not in content_text` | FAIL |
| test_include_paragraph_without_read_aloud | `"この段落は読み上げる" in content_text` | PASS |
| test_include_heading_without_read_aloud | `"この見出しは読み上げる" in content_text` | PASS |

### TestSkipPageMetadata (3 tests)

Tests pageMetadata exclusion. All PASS because pageMetadata is outside `<content>`.

### TestExtractFigureDescriptionWhenOptional (2 tests)

Tests figure description handling. All PASS because `to_page()` already implements this.

### TestSkipFigureFilePath (2 tests)

Tests file path exclusion. All PASS because file paths are stored in `Figure.file_path` but never output.

### TestIgnoreXmlComments (3 tests)

Tests XML comment handling. All PASS because ElementTree ignores comments automatically.

## Next Steps

phase-executor should:
1. Read this RED output
2. Implement `_should_read_aloud()` helper
3. Update `_extract_content_text()` to check readAloud
4. Verify `make test` PASS (GREEN)
5. Generate `tasks/ph3-output.md`
