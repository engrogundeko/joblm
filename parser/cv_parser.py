import json
from typing import List
from dotenv import load_dotenv
import nest_asyncio

load_dotenv()

# bring in deps
from log import logger
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
from langchain.prompts import PromptTemplate
from .schema import (
    affiliation_parser,
    interest_parser,
    publication_parser,
    work_parser,
    skill_parser,
    award_parser,
    project_parser,
    education_parser,
    volunteer_parser,
    personal_parser,
)
from .prompt import (
    professional_template,
    personal_info_template,
    work_info_template,
    interest_template,
    publication_template,
    volunteering_template,
    award_template,
    project_template,
    skill_template,
    education_info_template,
)
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.2-90b-text-preview",
    # model="mixtral-8x7b-32768",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

# set up parser
parser = LlamaParse(result_type="markdown")  # "markdown" and "text" are available

# use SimpleDirectoryReader to parse our file
file_extractor = {".pdf": parser}


async def parse_cv(file_path: str | List[str]):
    logger.info(f"Started parsing CV from file(s): {file_path}")

    try:
        # Initialize the reader with async support
        reader = SimpleDirectoryReader(
            input_files=[file_path], 
            file_extractor=file_extractor
        )
        
        # Use async load_data
        documents = await reader.aload_data()
        logger.info(f"Loaded {len(documents)} documents from {file_path}")

        content = ""
        metadata = {}  # Initialize metadata dictionary
        
        for idx, document in enumerate(documents):
            if idx == 3:
                logger.info("Processed 3 documents, stopping further parsing.")
                break
            content = content + document.text
            metadata = document.metadata
            logger.debug(f"Processed document {idx + 1}: {metadata['file_name']}")

        if not metadata:  # Check if metadata was populated
            raise ValueError("No metadata available - no documents were processed")

        # Prepare the result dictionary
        result = dict(
            file_name=metadata["file_name"],
            file_type=metadata["file_type"],
            file_size=metadata["file_size"],
            text=content,
        )

        logger.info(f"Successfully parsed CV from {file_path}. Returning result.")
        return result

    except Exception as e:
        logger.error(f"Error while parsing CV from {file_path}: {e}")
        raise


personal_info_prompt = PromptTemplate(
    partial_variables={
        "format_instructions": personal_parser.get_format_instructions()
    },
    template=personal_info_template,
)


work_experience_prompt = PromptTemplate(
    partial_variables={"format_instructions": work_parser.get_format_instructions()},
    template=work_info_template,
)

education_prompt = PromptTemplate(
    partial_variables={
        "format_instructions": education_parser.get_format_instructions()
    },
    template=education_info_template,
)


skill_prompt = PromptTemplate(
    partial_variables={"format_instructions": skill_parser.get_format_instructions()},
    template=skill_template,
)
projects_prompt = PromptTemplate(
    partial_variables={"format_instructions": project_parser.get_format_instructions()},
    template=project_template,
)

award_prompt = PromptTemplate(
    partial_variables={"format_instructions": award_parser.get_format_instructions()},
    template=award_template,
)

volunteering_prompt = PromptTemplate(
    partial_variables={
        "format_instructions": volunteer_parser.get_format_instructions()
    },
    template=volunteering_template,
)


publication_prompt = PromptTemplate(
    partial_variables={
        "format_instructions": publication_parser.get_format_instructions()
    },
    template=publication_template,
)

interest_professional_prompt = PromptTemplate(
    partial_variables={
        "format_instructions": interest_parser.get_format_instructions()
    },
    template=interest_template,
)

professional_affiliations_prompt = PromptTemplate(
    partial_variables={
        "format_instructions": affiliation_parser.get_format_instructions()
    },
    template=professional_template,
)

personal_chain = personal_info_prompt | llm | personal_parser
education_chain = education_prompt | llm | education_parser
work_chain = work_experience_prompt | llm | work_parser
volunteering_chain = volunteering_prompt | llm | volunteer_parser
award_chain = award_prompt | llm | award_parser
affiliation_chain = professional_affiliations_prompt | llm | affiliation_parser
publication_chain = publication_prompt | llm | publication_parser
projects_chain = projects_prompt | llm | project_parser
interest_chain = interest_professional_prompt | llm | interest_parser
skills_chain = skill_prompt | llm | skill_parser


async def parse_resume(resume_text):
    personal_info = personal_chain.invoke({"resume_text": resume_text})
    edu_info = education_chain.invoke({"resume_text": resume_text})
    work_info = work_chain.invoke({"resume_text": resume_text})
    publication_info = publication_chain.invoke({"resume_text": resume_text})
    volunteering_info = volunteering_chain.invoke({"resume_text": resume_text})
    interest_info = interest_chain.invoke({"resume_text": resume_text})
    skill_info = skills_chain.invoke({"resume_text": resume_text})
    affiliation_info = affiliation_chain.invoke({"resume_text": resume_text})
    award_info = award_chain.invoke({"resume_text": resume_text})
    project_info = projects_chain.invoke({"resume_text": resume_text})

    return to_dict(
        personal_info,
        edu_info,
        publication_info,
        work_info,
        volunteering_info,
        interest_info,
        skill_info,
        affiliation_info,
        award_info,
        project_info,
    )


def to_dict(*args):
    def convert(obj):
        if isinstance(obj, list):
            return [convert(item) for item in obj]
        elif hasattr(obj, "__dict__"):
            return {key: convert(value) for key, value in obj.__dict__.items()}
        else:
            return obj

    result = {}
    for arg in args:
        if isinstance(arg, list):
            result[arg[0].__class__.__name__.lower()] = [convert(item) for item in arg]
        elif hasattr(arg, "__dict__"):
            result[arg.__class__.__name__.lower()] = convert(arg)
        else:
            result[str(arg)] = arg
    return result


# cv_parser = parse_cv(r"C:\Users\Admin\Desktop\SolveByte\jobLM\curriculum-vitae (1).pdf")

# text = cv_parser["text"]

# resume = parse_resume(text)
# with open("andrew_ng.json", "w") as file:
#     json.dump(resume, file, indent=4)
