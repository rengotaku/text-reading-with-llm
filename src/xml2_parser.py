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
    heading_number_map = {}
    toc = root.find("toc")
    if toc is not None:
        for entry in toc.findall("entry"):
            title = entry.get("title", "")
            number = entry.get("number", "")
            if title and number:
                heading_number_map[title] = number

    content_items = []

    # Process all children of the root element
    for elem in root:
        # Skip metadata, toc, and front-matter sections
        if elem.tag in ("metadata", "toc", "front-matter"):
            continue

        # Process headings
        if elem.tag == "heading":
            if _should_read_aloud(elem) and elem.text:
                text = elem.text.strip()
                if text:
                    # Extract level attribute (default to 1 if missing)
                    level = int(elem.get("level", "1"))

                    # Get heading number from TOC mapping
                    number = heading_number_map.get(text, "")

                    # Format heading text
                    if number:
                        formatted_text = format_heading_text(level, number, text)
                    else:
                        # If no number found in TOC, use original text
                        formatted_text = text

                    # Add appropriate marker
                    if level == 1:
                        marked_text = CHAPTER_MARKER + formatted_text
                    else:
                        marked_text = SECTION_MARKER + formatted_text

                    # Create heading info
                    heading_info = HeadingInfo(
                        level=level,
                        number=number,
                        title=text,
                        read_aloud=True
                    )

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
