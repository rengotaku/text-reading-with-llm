"""XML book2 parser for TTS pipeline.

This module parses book2.xml files and extracts content items for text-to-speech processing.
Supports heading, paragraph, and list/item elements with readAloud filtering.
Skips <toc>, <front-matter>, and <metadata> sections.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Union
import xml.etree.ElementTree as ET


# Marker constants for chapter and section sound effects
# Using Unicode private use area characters to avoid text cleaner interference
CHAPTER_MARKER = "\uE001"
SECTION_MARKER = "\uE002"


@dataclass
class HeadingInfo:
    """Heading information from XML.

    Attributes:
        level: Heading level (1=chapter, 2+=section)
        number: Heading number ("1", "1.2", "3.10", etc.)
        title: Heading text
        read_aloud: Whether to read the heading aloud
    """
    level: int
    number: str
    title: str
    read_aloud: bool = True


@dataclass
class ContentItem:
    """Content item extracted from XML.

    Attributes:
        item_type: Type of content ("paragraph", "heading", "list_item")
        text: Text content (may include markers)
        heading_info: Heading information (only for heading items)
    """
    item_type: str
    text: str
    heading_info: HeadingInfo | None = None


def format_heading_text(level: int, number: str, title: str) -> str:
    """Format heading for TTS.

    Args:
        level: Heading level (1=chapter, 2+=section)
        number: Heading number ("1", "1.2", etc.)
        title: Heading text

    Returns:
        "第{number}章 {title}" for level=1
        "第{number}節 {title}" for level>=2
    """
    if level == 1:
        return f"第{number}章 {title}"
    else:
        return f"第{number}節 {title}"


def parse_book2_xml(xml_path: Union[str, Path]) -> list[ContentItem]:
    """Parse book2.xml and extract content items.

    Skips:
    - <toc> section
    - <front-matter> section
    - <metadata> section
    - Elements with readAloud="false"

    Processes:
    - <chapter> elements (as level 1 headings)
    - <section> elements (as level 2 headings)
    - <heading level="N"> elements
    - <paragraph> elements
    - <list>/<item> elements

    Args:
        xml_path: Path to the XML file (string or pathlib.Path)

    Returns:
        List of ContentItem objects in document order

    Raises:
        FileNotFoundError: If the XML file does not exist
        xml.etree.ElementTree.ParseError: If the XML is malformed
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Build heading number mapping from TOC
    heading_number_map: dict[str, str] = {}
    toc = root.find("toc")
    if toc is not None:
        for entry in toc.findall("entry"):
            title = entry.get("title", "")
            number = entry.get("number", "")
            if title and number:
                heading_number_map[title] = number

    content_items: list[ContentItem] = []

    def process_element(elem) -> None:
        """Recursively process an element and its children."""
        # Skip metadata, toc, and front-matter sections
        if elem.tag in ("metadata", "toc", "front-matter"):
            return

        # Process chapter (as level 1 heading)
        if elem.tag == "chapter":
            title = elem.get("title", "")
            number = elem.get("number", "")
            if title:
                formatted_text = format_heading_text(1, number, title) if number else title
                marked_text = CHAPTER_MARKER + formatted_text
                heading_info = HeadingInfo(level=1, number=number, title=title, read_aloud=True)
                content_items.append(ContentItem(
                    item_type="heading",
                    text=marked_text,
                    heading_info=heading_info
                ))
            # Process children of chapter
            for child in elem:
                process_element(child)

        # Process section (as level 2 heading)
        elif elem.tag == "section":
            title = elem.get("title", "")
            number = elem.get("number", "")
            if title:
                formatted_text = format_heading_text(2, number, title) if number else title
                marked_text = SECTION_MARKER + formatted_text
                heading_info = HeadingInfo(level=2, number=number, title=title, read_aloud=True)
                content_items.append(ContentItem(
                    item_type="heading",
                    text=marked_text,
                    heading_info=heading_info
                ))
            # Process children of section
            for child in elem:
                process_element(child)

        # Process headings
        elif elem.tag == "heading":
            if _should_read_aloud(elem) and elem.text:
                text = elem.text.strip()
                if text:
                    level = int(elem.get("level", "1"))
                    # Look up number from TOC mapping
                    number = heading_number_map.get(text, "")
                    # Format heading text
                    if number:
                        formatted_text = format_heading_text(level, number, text)
                    else:
                        formatted_text = text
                    marker = CHAPTER_MARKER if level == 1 else SECTION_MARKER
                    marked_text = marker + formatted_text
                    heading_info = HeadingInfo(level=level, number=number, title=text, read_aloud=True)
                    content_items.append(ContentItem(
                        item_type="heading",
                        text=marked_text,
                        heading_info=heading_info
                    ))

        # Process paragraphs
        elif elem.tag == "paragraph":
            if _should_read_aloud(elem) and elem.text:
                text = elem.text.strip()
                if text:
                    content_items.append(ContentItem(
                        item_type="paragraph",
                        text=text,
                        heading_info=None
                    ))

        # Process lists
        elif elem.tag == "list":
            for item in elem.findall("item"):
                if item.text:
                    text = item.text.strip()
                    if text:
                        content_items.append(ContentItem(
                            item_type="list_item",
                            text=text,
                            heading_info=None
                        ))

    # Process all children of the root element
    for elem in root:
        process_element(elem)

    return content_items


def _should_read_aloud(elem) -> bool:
    """Check if element should be read aloud based on readAloud attribute.

    Returns True if:
    - readAloud attribute is missing (default: read)
    - readAloud="true"

    Returns False if:
    - readAloud="false"

    Args:
        elem: XML element to check

    Returns:
        True if element should be read aloud, False otherwise
    """
    read_aloud = elem.get("readAloud", "true")
    return read_aloud != "false"
