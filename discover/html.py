from typing import Any
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_core.documents import Document


def _build_metadata(soup: Any, url: str) -> dict:
    """Build metadata from BeautifulSoup output."""
    metadata = {"source": url}
    if title := soup.find("title"):
        metadata["title"] = title.get_text()
    if description := soup.find("meta", attrs={"name": "description"}):
        metadata["description"] = description.get("content", "No description found.")
    if html := soup.find("html"):
        metadata["language"] = html.get("lang", "No language found.")
    return metadata


class AsyncHtmlLoaderWithOuterDivs(AsyncHtmlLoader):
    """Load HTML and extract the first two outer div elements inside <main>."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _extract_outer_divs(self, html_content: str) -> str:
        """Extract the first two outer <div> elements inside the <main> tag."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the <main> tag
        main_tag = soup.find("main")

        if main_tag:
            # Find the direct child div elements inside <main> (ignoring nested divs)
            outer_divs = main_tag.find_all("div", recursive=False)[:2]
            # Convert these divs to Markdown
            markdown = ""
            for div in outer_divs:
                markdown += md(str(div)) + "\n"
            return markdown
        return ""

    def _to_document(self, url: str, text: str) -> Document:
        """Override to process HTML and extract outer divs."""
        # Use the new extraction method for the first two outer divs
        extracted_content = self._extract_outer_divs(text)

        # Build the document with the extracted Markdown content
        metadata = _build_metadata(BeautifulSoup(text, "html.parser"), url)
        return Document(page_content=extracted_content, metadata=metadata)
