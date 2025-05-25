from log import logger

import httpx
import asyncio
from bs4 import BeautifulSoup
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from .html import AsyncHtmlLoaderWithOuterDivs as AsyncHtml


class DiscoverHubSchema(BaseModel):
    company: str
    location: str
    job_type: str
    date_posted: str
    salary_source: str
    description: str
    is_remote: bool
    min_amount: str
    max_amount: str
    currency: str
    job_level: str
    company_industry: str
    company_url: str
    company_addresses: str
    company_description: str
    job_function: str


parser = PydanticOutputParser(pydantic_object=DiscoverHubSchema)


class DiscoverHubScraper:

    def __init__(self):
        self.jina_reader = "https://r.jina.ai/"
        self.BASE_URLS = [
            "https://dixcoverhub.com.ng/category/graduate-programs/",
            "https://dixcoverhub.com.ng/category/scholarship/",
            "https://dixcoverhub.com.ng/category/internships/",
            "https://dixcoverhub.com.ng/category/jobs/",
            "https://dixcoverhub.com.ng/category/bootcamps/",
        ]
        logger.info("DiscoverHubScraper initialized with URLs: %s", self.BASE_URLS)

    async def fetch(self, url):
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching URL: {url} (Attempt {attempt + 1}/{max_retries})")
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
                    response.raise_for_status()  # Will raise an error for bad status codes
                    logger.info(f"Successfully fetched URL: {url}")
                    return response
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Too Many Requests
                    logger.warning(f"Rate limited on attempt {attempt + 1}. Waiting {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                logger.error(f"HTTP error occurred while fetching {url}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                return None
            except Exception as e:
                logger.error(f"Error occurred while fetching {url}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                return None

    async def fetch_data(self):
        tasks = [self.fetch(url) for url in self.BASE_URLS]
        results = await asyncio.gather(*tasks)
        return [result for result in results if result is not None]

    async def scrape_job_list(self):
        data = []
        try:
            logger.info("Starting scraping job listings.")
            responses = await self.fetch_data()

            for id, (response, url) in enumerate(zip(responses, self.BASE_URLS)):
                parts = url.split("/")
                job_type = parts[-2]
                soup = BeautifulSoup(response.content, "html.parser")

                for li in soup.find_all("li"):
                    id += 1
                    h2 = li.find("h2")
                    job_txt = None
                    job_link = None
                    job_time = None

                    if h2:
                        a_tag = h2.find("a")
                        if a_tag:
                            job_link = a_tag["href"]
                            job_txt = a_tag.get_text()

                        time_tag = li.find("time")
                        if time_tag:
                            job_time = time_tag.get_text()

                        data.append(
                            {
                                "id": id,
                                "job_link": job_link,
                                "job_title": job_txt,
                                "job_time": job_time,
                                "job_type": job_type,
                            }
                        )
            logger.info(f"Scraped {len(data)} job listings.")
        except Exception as e:
            logger.error(f"Error while scraping job list: {e}")
        return data

    async def compile(self, text):
        try:
            template = ""
            llm = ChatGroq(
                model="llama-3.2-90b-text-preview",
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
            )
            prompt = PromptTemplate(
                partial_variables={
                    "format_instructions": parser.get_format_instructions()
                },
                template=template,
            )
            chain = prompt | llm | parser

            info = chain.invoke({"text": text})
            return info
        except Exception as e:
            logger.error(f"Error while compiling text with LLM: {e}")
            return {}

    async def parse(self):
        jobs = []
        try:
            logger.info("Starting the job parsing process.")
            responses = await self.scrape_job_list()
            urls = [url["job_link"] for url in responses]

            job_details = await self.extract_details(urls)

            # Append the job data
            for response, job_detail in zip(responses, job_details):
                jobs.append(
                    {
                        "id": response["id"],
                        "job_link": response["job_link"],
                        "job_title": response["job_title"],
                        "job_time": response["job_time"],
                        "job_type": response["job_type"],
                        "job_text": job_detail,
                    }
                )
            logger.info(f"Parsed {len(jobs)} jobs successfully.")
        except Exception as e:
            logger.error(f"Error while parsing job details: {e}")
        return jobs

    async def extract_details(self, urls):
        loader = AsyncHtml(urls)
        docs = await loader.aload()
        all_content = [con.page_content for con in docs]
        return all_content
