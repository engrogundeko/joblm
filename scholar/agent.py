import asyncio
import os
import re
import httpx
from pydantic_ai import Agent
from .prompt import scholar_template, list_scholar_4_dev
from dataclasses import dataclass
from .schema import Scholarship, ListScholar4Dev
from dotenv import load_dotenv
from pprint import pprint
from log import logger
load_dotenv()


@dataclass
class MyDeps:  
    http_client: httpx.AsyncClient
    api_key: str = os.getenv("GEMINI_API_KEY")


scholarship_agent = Agent(
    retries=3,
    system_prompt=scholar_template,
    model='gemini-1.5-flash',
    result_type=Scholarship
    
)

# master_detailed_agent = Agent(
#     retries=3,
#     system_prompt=scholar_template,
#     model="groq:gemma2-9b-it",
#     result_type=Scholar4DevDetails,
#     deps_type=MyDeps
#     )

master_list_agent = Agent(
    retries=3,
    system_prompt=list_scholar_4_dev,
    model="gemini-1.5-flash",
    result_type=ListScholar4Dev,
    deps_type=MyDeps
    )

def to_dict(obj):
        """Convert any object to a dictionary recursively"""
        def convert(item):
            if isinstance(item, list):
                return [convert(i) for i in item]
            elif isinstance(item, dict):
                return {k: convert(v) for k, v in item.items()}
            elif hasattr(item, "__dict__"):
                return {k: convert(v) for k, v in item.__dict__.items()}
            else:
                return item

        # Handle different input types
        if isinstance(obj, list):
            return [convert(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif hasattr(obj, "__dict__"):
            return convert(obj.__dict__)
        else:
            return obj

async def run_scholarship(prompt: str):
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
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
                deps = MyDeps(http_client=client)
                await asyncio.sleep(5)
                result = await scholarship_agent.run(
                    user_prompt=prompt,
                    deps=deps,  
                )

                formatted_result = to_dict(result.data)
                return formatted_result
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Too Many Requests
                logger.warning(f"Rate limited on attempt {attempt + 1}. Waiting {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            logger.error(f"HTTP error in run_scholarship: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            raise
        except Exception as e:
            logger.error(f"Error in run_scholarship: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            raise


async def run_scholarship_list(prompt: str):
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
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
                deps = MyDeps(http_client=client)
                await asyncio.sleep(5)
                result = await master_list_agent.run(
                    user_prompt=prompt,
                    deps=deps,  
                )

                formatted_result = to_dict(result.data)
                return formatted_result
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Too Many Requests
                logger.warning(f"Rate limited on attempt {attempt + 1}. Waiting {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            logger.error(f"HTTP error in run_scholarship_list: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            raise
        except Exception as e:
            logger.error(f"Error in run_scholarship_list: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            raise




