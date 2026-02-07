"""XML book parser for TTS pipeline.

This module parses book.xml files and extracts page content for text-to-speech processing.
Supports paragraph, heading, list, and figure elements with readAloud filtering.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Union
import xml.etree.ElementTree as ET

from src.text_cleaner import Page


@dataclass
class Figure:
    """Figure information from XML.

    Attributes:
        file_path: Path to the figure image file
        description: Text description of the figure
        read_aloud: Whether to read the description ("true", "false", "optional")
    """
    file_path: str
    description: str
    read_aloud: str


@dataclass
class XmlPage:
    """Page data extracted from XML.

    Attributes:
        number: Page number (1-indexed)
        source_file: Source image file name
        announcement: Page announcement text (e.g., "1ページ")
        content_text: Extracted text from content elements
        figures: List of figures on this page
    """
    number: int
    source_file: str
    announcement: str
    content_text: str
    figures: list[Figure]


def parse_book_xml(xml_path: Union[str, Path]) -> list[XmlPage]:
    """Parse book.xml and return list of XmlPage.

    Args:
        xml_path: Path to the XML file (string or pathlib.Path)

    Returns:
        List of XmlPage objects, one per page in the XML

    Raises:
        FileNotFoundError: If the XML file does not exist
        xml.etree.ElementTree.ParseError: If the XML is malformed
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    pages = []
    for page_elem in root.findall("page"):
        # Extract page attributes
        number = int(page_elem.get("number"))
        source_file = page_elem.get("sourceFile", "")

        # Extract page announcement
        announcement_elem = page_elem.find("pageAnnouncement")
        announcement = announcement_elem.text if announcement_elem is not None and announcement_elem.text else ""

        # Extract content text
        content_elem = page_elem.find("content")
        content_text = _extract_content_text(content_elem) if content_elem is not None else ""

        # Extract figures
        figures = []
        for figure_elem in page_elem.findall("figure"):
            read_aloud = figure_elem.get("readAloud", "true")

            file_elem = figure_elem.find("file")
            file_path = file_elem.text if file_elem is not None and file_elem.text else ""

            desc_elem = figure_elem.find("description")
            description = desc_elem.text if desc_elem is not None and desc_elem.text else ""

            figures.append(Figure(
                file_path=file_path,
                description=description,
                read_aloud=read_aloud
            ))

        pages.append(XmlPage(
            number=number,
            source_file=source_file,
            announcement=announcement,
            content_text=content_text,
            figures=figures
        ))

    return pages


def _extract_content_text(content_elem) -> str:
    """Extract text from content element in DOM order.

    Extracts text from paragraph, heading, and list/item elements
    while preserving their order in the XML document.

    Args:
        content_elem: The <content> XML element

    Returns:
        Concatenated text with newlines between elements
    """
    texts = []

    for child in content_elem:
        if child.tag == "paragraph":
            if child.text:
                texts.append(child.text)
        elif child.tag == "heading":
            if child.text:
                texts.append(child.text)
        elif child.tag == "list":
            # Extract all items from the list
            for item in child.findall("item"):
                if item.text:
                    texts.append(item.text)

    return "\n".join(texts)


def to_page(xml_page: XmlPage) -> Page:
    """Convert XmlPage to existing Page dataclass.

    Combines announcement, content text, and figure descriptions
    (when readAloud != "false") into a single text string.

    Args:
        xml_page: The XmlPage to convert

    Returns:
        Page instance with combined text
    """
    parts = []

    # Add announcement first
    if xml_page.announcement:
        parts.append(xml_page.announcement)

    # Add content text
    if xml_page.content_text:
        parts.append(xml_page.content_text)

    # Add figure descriptions (if readAloud != "false")
    for fig in xml_page.figures:
        if fig.read_aloud != "false" and fig.description:
            parts.append(fig.description)

    text = "\n".join(parts)
    return Page(number=xml_page.number, text=text)
