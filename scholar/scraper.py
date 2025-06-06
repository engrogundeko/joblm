import hashlib
import asyncio
from urllib.parse import urljoin

from log import logger
from .agent import run_scholarship
from app_write import AppwriteClient
from appwrite.query import Query

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from dotenv import load_dotenv
import os

load_dotenv()

PROXY_URL = os.getenv("PROXY_URL")

db = AppwriteClient()

class ScholarshipScraper:
    def __init__(self):
        self.base_url = "https://dixcoverhub.com.ng/category/scholarship"
        self._client = None
        self._semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent requests
        self._last_request_time = 0
        self.request_interval = 1/3  # 3 requests per second


    @property
    async def client(self):
        """Lazy initialize the httpx client"""
        if self._client is None:
            # Update proxy configuration to use the correct format for httpx
            # The format is {"http://": proxy_url, "https://": proxy_url}
            if PROXY_URL:
                proxy_config = {
                    "http://": PROXY_URL,
                    "https://": PROXY_URL
                }
            else:
                proxy_config = None
                
            self._client = httpx.AsyncClient(
                timeout=60.0,  # Increased timeout
                follow_redirects=True,  # Handle redirects automatically
                verify=True,  # Verify SSL certificates
                http2=True,  # Enable HTTP/2 support
                proxies=proxy_config,
                limits=httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10,
                    keepalive_expiry=30.0,
                ),
                # Add retry mechanism
                transport=httpx.AsyncHTTPTransport(
                    retries=3,  # Number of retries
                    verify=True,
                )
            )
        return self._client

    async def __aenter__(self):
        await self.client
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _throttle(self):
        """Ensure requests are throttled to avoid rate limiting"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        # Increase the interval between requests to avoid rate limiting
        self.request_interval = 2  # 1 request per 2 seconds
        if time_since_last < self.request_interval:
            await asyncio.sleep(self.request_interval - time_since_last)
        self._last_request_time = asyncio.get_event_loop().time()

    async def is_new_scholarship(self, scholarship_text: dict) -> bool:
    
        """Check if a scholarship is new by looking up its hash in Appwrite"""
        try:
            title = scholarship_text.get("title", "")
            link = scholarship_text.get("link", "")
            text = f"{title}{link}"
            content_hash = hashlib.md5(text.encode()).hexdigest()
            
            result = await db.list_documents(
                collection_id="scholarships",
                queries=[Query.equal("content_hash", content_hash)]
            )

            print(result)
            
            # If no documents match the hash, the scholarship is new.
            return len(result.get("documents", [])) == 0
        except Exception as e:
            logger.error(f"Error checking scholarship history: {str(e)}")
            return True

    async def get_page(self, page=1):
        """Fetch a specific page of scholarships with rate limiting using a proxy"""
        # Properly construct the URL using urljoin
        if page == 1:
            url = self.base_url
        else:
            url = urljoin(self.base_url, f"page/{page}/")

        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            async with self._semaphore:  # Limit concurrent requests
                try:
                    await self._throttle()  # Ensure rate limiting
                    logger.info(f"Fetching page {page} via proxy: {url} (Attempt {attempt + 1}/{max_retries})")

                    client = await self.client
                    response = await client.get(url)
                    response.raise_for_status()
                    
                    logger.info(f"Successfully fetched page {page}")
                    return response.text
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:  # Too Many Requests
                        logger.warning(f"Rate limited on attempt {attempt + 1}. Waiting {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    logger.error(f"HTTP error fetching page {page}: {str(e)}")
                    return None
                except Exception as e:
                    logger.error(f"Error fetching page {page}: {str(e)}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    return None


    async def get_page_contents(self, max_pages=3):
        """Get contents of multiple pages with rate limiting"""
        tasks = []
        for page in range(1, max_pages + 1):
            tasks.append(self.get_page(page))
        return await asyncio.gather(*tasks)

    async def save_scholarship(self, scholarship_text: dict):
        """Save a scholarship to Appwrite database"""
        title = scholarship_text.get("title", "")
        link = scholarship_text.get("link", "")
        text = f"{title}{link}"
        content_hash = hashlib.md5(text.encode()).hexdigest()
        
        
        try:
            # Create document in Appwrite
            document_data = {
                    'content': scholarship_text.get("content", ""),
                    'title': title,
                    'link': link,
                    "application_link": scholarship_text.get("application_link", ""),
                    'content_hash': content_hash
                }
            db.create_document(
                collection_id="scholarships",
                document_id=self.generate_scholarship_id(scholarship_text),
                data=document_data
            )
            logger.info(f"Saved scholarship: {title}")
        except Exception as e:
            logger.error(f"Error saving scholarship: {str(e)}")

    def generate_scholarship_id(self, scholarship):
        """Generate a unique ID for a scholarship"""
        # Create a unique identifier using title and link
        unique_string = f"{scholarship['title']}{scholarship['link']}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    
    async def parse_with_llm(self, markdown):
        content = await run_scholarship(markdown)
        return content

    async def parse_scholarship(self, soup) :
        "Not Implemented" 
        raise NotImplementedError("Subclasses must implement parse_scholarship")
         
    def to_md(self, html_content):
        return md(html_content)

    def clean_content(self, content: str) -> str:
        """Clean the scholarship content by removing extra whitespace and formatting"""
        if not content:
            return ""
            
        # Split content into lines and remove empty ones
        lines = [line.strip() for line in content.split('\n')]
        # Remove consecutive empty lines
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            if line:  # If line has content
                cleaned_lines.append(line)
                prev_empty = False
            elif not prev_empty:  # If line is empty and previous line wasn't
                cleaned_lines.append(line)
                prev_empty = True
                
        # Join lines and strip any remaining whitespace
        cleaned_content = '\n'.join(cleaned_lines).strip()
        
        # Remove any remaining multiple newlines
        cleaned_content = '\n'.join(filter(None, cleaned_content.split('\n')))
        
        return cleaned_content

    async def check_new_scholarships(self, max_pages=3):
        """Check for new scholarships and return them"""
        new_scholarships = []     
        page_contents = await self.get_page_contents(max_pages)
        for html_content in page_contents:
            if not html_content:
                continue
                
            soup = BeautifulSoup(html_content, 'html.parser')
            
            scholarships = await self.parse_scholarship(soup)
            if scholarships:
                # Filter and save new scholarships
                for scholarship in scholarships:
                    if await self.is_new_scholarship(scholarship):
                        # Process the content
                        try:
                            processed_content = await self.parse_with_llm(scholarship['content'])
                        except Exception as e:
                            logger.error(f"Error processing scholarship: {str(e)}")
                            continue
                        
                        # Clean and update the scholarship
                        # cleaned_content = self.clean_content(processed_content["content"])
                        scholarship['content'] = processed_content.get('content', '')
                        scholarship['application_link'] =  processed_content.get('application_link', '')
                        
                        new_scholarships.append(scholarship)
                        await self.save_scholarship(scholarship)
            
        return new_scholarships
