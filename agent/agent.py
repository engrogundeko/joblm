from .prompt import new_user_template, job_template, job_extract_template
from .schema import user_parser, job_parser, job_extract_parser
import asyncio
from .llm import GeminiLLM

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

load_dotenv()
gemini_llm = GeminiLLM()
llm_llama = ChatGroq(
    model="llama-3.2-90b-text-preview",
    # model="mixtral-8x7b-32768",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)
llm_mixtra = ChatGroq(
    model="llama3-groq-70b-8192-tool-use-preview",
    # model="gemma2-7b-it",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)


def to_dict(arg):
    def convert(obj):
        if isinstance(obj, list):
            return [convert(item) for item in obj]
        elif hasattr(obj, "__dict__"):
            return {key: convert(value) for key, value in obj.__dict__.items()}
        else:
            return obj

    result = {}

    if isinstance(arg, list):
        result[arg[0].__class__.__name__.lower()] = [convert(item) for item in arg]
    elif hasattr(arg, "__dict__"):
        result[arg.__class__.__name__.lower()] = convert(arg)
    else:
        result[str(arg)] = arg
    return result


user_info_prompt = PromptTemplate(
    partial_variables={"format_instructions": user_parser.get_format_instructions()},
    template=new_user_template,
)
job_info_prompt = PromptTemplate(
    partial_variables={"format_instructions": job_parser.get_format_instructions()},
    template=job_template,
)
job_extract_prompt = PromptTemplate(
    partial_variables={
        "format_instructions": job_extract_parser.get_format_instructions()
    },
    template=job_extract_template,
)

user_chain = user_info_prompt | llm_mixtra | user_parser
job_chain = job_info_prompt | llm_mixtra | job_parser
