# Phase 2 RED Tests

## Summary

- Phase: Phase 2 - User Story 1 - XML to TTS Pipeline
- FAIL Test Count: 33 test methods (all fail due to ImportError)
- Test File: tests/test_xml_parser.py

## FAIL Test List

| Test File | Test Method | Expected Behavior |
|-----------|-------------|-------------------|
| tests/test_xml_parser.py | test_parse_book_xml_returns_list | parse_book_xml returns a list |
| tests/test_xml_parser.py | test_parse_book_xml_returns_xmlpage_instances | Each element is XmlPage |
| tests/test_xml_parser.py | test_parse_book_xml_page_count | sample_book.xml has 3 pages |
| tests/test_xml_parser.py | test_xmlpage_has_number | XmlPage has number field |
| tests/test_xml_parser.py | test_xmlpage_has_content_text | XmlPage has content_text field |
| tests/test_xml_parser.py | test_xmlpage_has_announcement | XmlPage has announcement field |
| tests/test_xml_parser.py | test_xmlpage_has_figures | XmlPage has figures field |
| tests/test_xml_parser.py | test_xmlpage_has_source_file | XmlPage has source_file field |
| tests/test_xml_parser.py | test_extract_paragraph_text_single | Extract single paragraph text |
| tests/test_xml_parser.py | test_extract_paragraph_text_multiple | Extract multiple paragraph texts |
| tests/test_xml_parser.py | test_extract_paragraph_preserves_order | Paragraph order preserved |
| tests/test_xml_parser.py | test_extract_heading_text_level1 | Extract level=1 heading |
| tests/test_xml_parser.py | test_extract_heading_text_chapter | Extract chapter heading |
| tests/test_xml_parser.py | test_heading_order_with_paragraphs | Heading/paragraph order preserved |
| tests/test_xml_parser.py | test_extract_list_items | Extract list items |
| tests/test_xml_parser.py | test_list_items_preserve_order | List items order preserved |
| tests/test_xml_parser.py | test_extract_page_announcement_page1 | Page 1 announcement = "1ページ" |
| tests/test_xml_parser.py | test_extract_page_announcement_page2 | Page 2 announcement = "2ページ" |
| tests/test_xml_parser.py | test_extract_page_announcement_page3 | Page 3 announcement = "3ページ" |
| tests/test_xml_parser.py | test_to_page_returns_page_instance | to_page returns Page |
| tests/test_xml_parser.py | test_to_page_preserves_number | to_page preserves page number |
| tests/test_xml_parser.py | test_to_page_includes_announcement | to_page includes announcement |
| tests/test_xml_parser.py | test_to_page_includes_content_text | to_page includes content |
| tests/test_xml_parser.py | test_to_page_announcement_before_content | Announcement before content |
| tests/test_xml_parser.py | test_figure_extracted_from_page | Figure extracted from page |
| tests/test_xml_parser.py | test_figure_has_file_path | Figure has file_path |
| tests/test_xml_parser.py | test_figure_has_description | Figure has description |
| tests/test_xml_parser.py | test_figure_has_read_aloud | Figure has read_aloud |
| tests/test_xml_parser.py | test_to_page_includes_figure_description_when_optional | Include figure desc when optional |
| tests/test_xml_parser.py | test_parse_book_xml_with_pathlib_path | Accept pathlib.Path |
| tests/test_xml_parser.py | test_parse_book_xml_with_string_path | Accept string path |
| tests/test_xml_parser.py | test_page_numbers_are_integers | Page numbers are int |
| tests/test_xml_parser.py | test_page_numbers_are_sequential | Page numbers are 1, 2, 3 |
| tests/test_xml_parser.py | test_content_text_is_not_empty | content_text is not empty |

## Implementation Hints

### Module to Create

`src/xml_parser.py` with:

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Union

@dataclass
class Figure:
    """Figure information from XML."""
    file_path: str
    description: str
    read_aloud: str  # "true", "false", "optional"

@dataclass
class XmlPage:
    """Page data extracted from XML."""
    number: int
    source_file: str
    announcement: str
    content_text: str
    figures: list[Figure]

def parse_book_xml(xml_path: Union[str, Path]) -> list[XmlPage]:
    """Parse book.xml and return list of XmlPage."""
    ...

def to_page(xml_page: XmlPage) -> Page:
    """Convert XmlPage to existing Page dataclass."""
    ...
```

### Key Implementation Notes

1. Use `xml.etree.ElementTree` for parsing
2. Import `Page` from `src.text_cleaner`
3. Extract text from `<paragraph>`, `<heading>`, `<list>/<item>` in DOM order
4. Include `<pageAnnouncement>` text in announcement field
5. Include figure description in to_page() when read_aloud != "false"

## FAIL Output Example

```
tests/test_xml_parser.py:17: in <module>
    from src.xml_parser import Figure, XmlPage, parse_book_xml, to_page
E   ModuleNotFoundError: No module named 'src.xml_parser'
```

## Test Class Summary

| Class | Test Count | Purpose |
|-------|------------|---------|
| TestParseBookXmlReturnsPages | 3 | Basic parse_book_xml behavior |
| TestXmlPageHasNumberAndText | 5 | XmlPage dataclass fields |
| TestExtractParagraphText | 3 | Paragraph extraction |
| TestExtractHeadingText | 3 | Heading extraction |
| TestExtractListItems | 2 | List item extraction |
| TestExtractPageAnnouncement | 3 | Page announcement extraction |
| TestToPageConversion | 5 | XmlPage to Page conversion |
| TestFigureDataclass | 4 | Figure dataclass fields |
| TestToPageWithFigureDescription | 1 | Figure description in to_page |
| TestParseBookXmlWithPath | 2 | Path type handling |
| TestEdgeCases | 3 | Edge cases |

## Next Steps

1. phase-executor reads this RED output
2. Create `src/xml_parser.py` with implementation
3. Run `make test` to verify GREEN (all tests pass)
4. Generate `tasks/ph2-output.md`
