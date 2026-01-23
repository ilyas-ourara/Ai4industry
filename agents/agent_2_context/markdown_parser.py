"""
Markdown Parser for Agent 2.
Parses Markdown content and extracts structured information.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger
import yaml


@dataclass
class ParsedSection:
    """Represents a parsed section from Markdown."""
    level: int
    title: str
    content: str
    line_start: int
    line_end: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: List["ParsedSection"] = field(default_factory=list)


@dataclass
class ParsedMarkdown:
    """Result of parsing a Markdown document."""
    frontmatter: Dict[str, Any]
    title: Optional[str]
    sections: List[ParsedSection]
    raw_content: str
    links: List[Dict[str, str]]
    tables: List[str]


class MarkdownParser:
    """
    Parser for structured Markdown documents.
    Extracts frontmatter, sections, and metadata.
    """

    # Regex patterns
    FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    TABLE_PATTERN = re.compile(r"(\|.+\|\n)+", re.MULTILINE)
    PAGE_COMMENT_PATTERN = re.compile(r"<!--\s*Page\s+(\d+)\s*-->")

    def __init__(self):
        """Initialize the Markdown parser."""
        self._logger = logger.bind(component="MarkdownParser")

    def parse(self, content: str) -> ParsedMarkdown:
        """
        Parse Markdown content into structured format.
        
        Args:
            content: Markdown string content
            
        Returns:
            ParsedMarkdown object with extracted structure
        """
        self._logger.info("Parsing Markdown content...")
        
        # Extract frontmatter
        frontmatter, content_without_fm = self._extract_frontmatter(content)
        
        # Extract title (first H1)
        title = self._extract_title(content_without_fm)
        
        # Parse sections
        sections = self._parse_sections(content_without_fm)
        
        # Extract links
        links = self._extract_links(content)
        
        # Extract tables
        tables = self._extract_tables(content)
        
        result = ParsedMarkdown(
            frontmatter=frontmatter,
            title=title,
            sections=sections,
            raw_content=content,
            links=links,
            tables=tables,
        )
        
        self._logger.info(
            f"Parsed: {len(sections)} sections, "
            f"{len(links)} links, {len(tables)} tables"
        )
        
        return result

    def parse_file(self, file_path: Path) -> ParsedMarkdown:
        """
        Parse a Markdown file.
        
        Args:
            file_path: Path to Markdown file
            
        Returns:
            ParsedMarkdown object
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {file_path}")
        
        content = file_path.read_text(encoding="utf-8")
        return self.parse(content)

    def _extract_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """Extract YAML frontmatter from content."""
        match = self.FRONTMATTER_PATTERN.match(content)
        
        if match:
            try:
                frontmatter = yaml.safe_load(match.group(1))
                content_without_fm = content[match.end():]
                return frontmatter or {}, content_without_fm
            except yaml.YAMLError as e:
                self._logger.warning(f"Failed to parse frontmatter: {e}")
        
        return {}, content

    def _extract_title(self, content: str) -> Optional[str]:
        """Extract the main title (first H1) from content."""
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None

    def _parse_sections(self, content: str) -> List[ParsedSection]:
        """Parse all sections from Markdown content."""
        lines = content.split("\n")
        sections: List[ParsedSection] = []
        section_stack: List[ParsedSection] = []
        
        current_content_lines: List[str] = []
        current_line_start = 0
        
        for i, line in enumerate(lines):
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            
            if heading_match:
                # Close previous section's content
                if section_stack:
                    section_stack[-1].content = "\n".join(current_content_lines).strip()
                    section_stack[-1].line_end = i - 1
                
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                
                new_section = ParsedSection(
                    level=level,
                    title=title,
                    content="",
                    line_start=i,
                    line_end=i,
                    metadata=self._extract_section_metadata(lines, i),
                )
                
                # Find parent for this section
                while section_stack and section_stack[-1].level >= level:
                    section_stack.pop()
                
                if section_stack:
                    section_stack[-1].children.append(new_section)
                else:
                    sections.append(new_section)
                
                section_stack.append(new_section)
                current_content_lines = []
                current_line_start = i + 1
                
            else:
                current_content_lines.append(line)
        
        # Close final section
        if section_stack:
            section_stack[-1].content = "\n".join(current_content_lines).strip()
            section_stack[-1].line_end = len(lines) - 1
        
        return sections

    def _extract_section_metadata(self, lines: List[str], heading_line: int) -> Dict[str, Any]:
        """Extract metadata from around a section heading."""
        metadata = {}
        
        # Look for page comment before or after heading
        search_range = lines[max(0, heading_line - 2):heading_line + 3]
        for line in search_range:
            page_match = self.PAGE_COMMENT_PATTERN.search(line)
            if page_match:
                metadata["page"] = int(page_match.group(1))
                break
        
        return metadata

    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        """Extract all Markdown links."""
        links = []
        for match in self.LINK_PATTERN.finditer(content):
            links.append({
                "text": match.group(1),
                "url": match.group(2),
            })
        return links

    def _extract_tables(self, content: str) -> List[str]:
        """Extract Markdown tables."""
        tables = []
        for match in self.TABLE_PATTERN.finditer(content):
            tables.append(match.group(0).strip())
        return tables

    def get_section_by_path(
        self, 
        parsed: ParsedMarkdown, 
        path: List[str]
    ) -> Optional[ParsedSection]:
        """
        Get a section by its hierarchical path.
        
        Args:
            parsed: ParsedMarkdown object
            path: List of section titles forming the path
            
        Returns:
            ParsedSection if found, None otherwise
        """
        current_sections = parsed.sections
        
        for title in path:
            found = None
            for section in current_sections:
                if section.title.lower() == title.lower():
                    found = section
                    break
            
            if not found:
                return None
            
            current_sections = found.children
        
        return found

    def flatten_sections(self, sections: List[ParsedSection]) -> List[ParsedSection]:
        """
        Flatten nested sections into a single list.
        
        Args:
            sections: Nested list of ParsedSection
            
        Returns:
            Flat list of all sections
        """
        result = []
        
        def flatten(section_list: List[ParsedSection]):
            for section in section_list:
                result.append(section)
                flatten(section.children)
        
        flatten(sections)
        return result

    def extract_text_content(self, parsed: ParsedMarkdown) -> str:
        """
        Extract plain text content from parsed Markdown.
        Removes formatting and metadata.
        
        Args:
            parsed: ParsedMarkdown object
            
        Returns:
            Plain text string
        """
        content = parsed.raw_content
        
        # Remove frontmatter
        content = self.FRONTMATTER_PATTERN.sub("", content)
        
        # Remove HTML comments
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
        
        # Remove Markdown formatting
        content = re.sub(r"\*\*(.+?)\*\*", r"\1", content)  # Bold
        content = re.sub(r"\*(.+?)\*", r"\1", content)  # Italic
        content = re.sub(r"`(.+?)`", r"\1", content)  # Code
        content = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", content)  # Links
        
        # Clean up whitespace
        content = re.sub(r"\n{3,}", "\n\n", content)
        
        return content.strip()
