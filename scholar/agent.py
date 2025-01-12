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
load_dotenv()


@dataclass
class MyDeps:  
    http_client: httpx.AsyncClient
    api_key: str = os.getenv("GROQ_API_KEY")


scholarship_agent = Agent(
    retries=3,
    system_prompt=scholar_template,
    model="groq:llama3-70b-8192",
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
    model="groq:llama3-groq-8b-8192",
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
    async with httpx.AsyncClient() as client:
        deps = MyDeps(http_client=client)
        await asyncio.sleep(5)
        result = await scholarship_agent.run(
            user_prompt=prompt,
            deps=deps,  
        )

        formatted_result = to_dict(result.data)


        return formatted_result


async def run_scholarship_list(prompt: str):
    async with httpx.AsyncClient() as client:
        deps = MyDeps(http_client=client)
        await asyncio.sleep(5)
        result = await master_list_agent.run(
            user_prompt=prompt,
            deps=deps,  
        )

        formatted_result = to_dict(result.data)

        return formatted_result




