from typing import Any
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_core.documents import Document
import asyncio
import httpx
from log import logger


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
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    async def _fetch_with_retry(self, url: str) -> str:
        """Fetch HTML content with retry logic for rate limiting."""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching URL: {url} (Attempt {attempt + 1}/{self.max_retries})")
                async with httpx.AsyncClient(
                    timeout=60.0,
                    follow_redirects=True,
                    verify=True,
                    http2=True,
                    transport=httpx.AsyncHTTPTransport(
                        retries=2,  # Number of retries
                        verify=True,
                    )
                ) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    logger.info(f"Successfully fetched URL: {url}")
                    return response.text
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Too Many Requests
                    logger.warning(f"Rate limited on attempt {attempt + 1}. Waiting {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                    self.retry_delay *= 2  # Exponential backoff
                    continue
                logger.error(f"HTTP error occurred while fetching {url}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    self.retry_delay *= 2  # Exponential backoff
                    continue
                raise
            except Exception as e:
                logger.error(f"Error occurred while fetching {url}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    self.retry_delay *= 2  # Exponential backoff
                    continue
                raise

    async def aload(self) -> list[Document]:
        """Load documents asynchronously with retry logic."""
        documents = []
        for url in self.web_paths:
            try:
                html_content = await self._fetch_with_retry(url)
                document = self._to_document(url, html_content)
                documents.append(document)
            except Exception as e:
                logger.error(f"Error loading document from {url}: {e}")
                continue
        return documents

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
