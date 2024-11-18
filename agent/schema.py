from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

import random


def get_random_countries():
    countries = [
        "argentina",
        "australia",
        "austria",
        "bahrain",
        "belgium",
        "brazil",
        "canada",
        "chile",
        "china",
        "colombia",
        "costa rica",
        "czech republic",
        "czechia",
        "denmark",
        "ecuador",
        "egypt",
        "finland",
        "france",
        "germany",
        "greece",
        "hong kong",
        "hungary",
        "india",
        "indonesia",
        "ireland",
        "israel",
        "italy",
        "japan",
        "kuwait",
        "luxembourg",
        "malaysia",
        "malta",
        "mexico",
        "morocco",
        "netherlands",
        "new zealand",
        "nigeria",
        "norway",
        "oman",
        "pakistan",
        "panama",
        "peru",
        "philippines",
        "poland",
        "portugal",
        "qatar",
        "romania",
        "saudi arabia",
        "singapore",
        "south africa",
        "south korea",
        "spain",
        "sweden",
        "switzerland",
        "taiwan",
        "thailand",
        "türkiye",
        "turkey",
        "ukraine",
        "united arab emirates",
        "uk",
        "united kingdom",
        "usa",
        "us",
        "united states",
        "uruguay",
        "venezuela",
        "vietnam",
        "usa/ca",
        "worldwide",
    ]
    valid = random.sample(countries, 2)
    valid.extend(["wordwide", "united states", "germany"])
    return random.sample(countries, 5)


class UserSchema(BaseModel):
    message: str = Field(
        description=" The email should include personalized details derived from the resume content, such as the user’s name, relevant experience, skills, and any unique accomplishments. Present the final output as a structured JSON response."
    )

class JobExtractSchema(BaseModel):
    job_title: str = Field(description="The official title/position being advertised (e.g., 'Senior Software Engineer', 'Product Manager')")
    job_description: str = Field(description="A clear summary of the role and its purpose (e.g., 'Lead the development of cloud-based applications and mentor junior developers')")
    required_skills: list[str] = Field(description="Technical and soft skills explicitly mentioned as requirements (e.g., ['Python', 'AWS', 'Team Leadership', 'Agile Methodologies'])")
    responsibilities: list[str] = Field(description="Key duties and tasks associated with the role (e.g., ['Design and implement scalable solutions', 'Code review', 'Sprint planning'])")
    qualifications: list[str] = Field(description="Required education, certifications, and experience levels (e.g., ['Bachelor's in Computer Science', '5+ years experience', 'AWS Certification'])")
    location: str = Field(description="Specify if Remote, On-site, or Hybrid, including city/country if applicable (e.g., 'Remote', 'Hybrid - New York, NY', 'On-site - London, UK')")
    salary_range: str = Field(description="Include minimum and maximum salary if provided, with currency (e.g., '$120,000 - $160,000 USD per year')")
    company_info: str = Field(description="Company name, industry, size, and brief description (e.g., 'TechCorp Inc. - Fortune 500 technology company with 5000+ employees specializing in cloud solutions')")
    keywords: list[str] = Field(description="Important terms and phrases that characterize the role (e.g., ['full-stack', 'cloud architecture', 'team lead', 'enterprise software'])")

class JobSchema(BaseModel):
    search_term: str = Field(
        description="Main job title or keywords relevant to the candidate's expertise."
    )
    location: str = Field(
        description="Desired city or region where the candidate is looking for a job."
    )
    results_wanted: int = Field(
        description="Number of job listings to return in the search results."
    )
    hours_old: int = Field(description="Maximum age of the job listings in hours.")
    country_indeed: str = Field(
        description=f"Country code for Indeed searches. VALID countries include: {get_random_countries()}"
    )
    is_remote: bool = Field(
        description="Flag indicating whether the search is for remote positions only."
    )
    google_search_term: str = Field(
        description="Customized Google search query based on job title, location, and other criteria."
    )
  
  

    


job_parser = PydanticOutputParser(pydantic_object=JobSchema)
user_parser = PydanticOutputParser(pydantic_object=UserSchema)
job_extract_parser = PydanticOutputParser(pydantic_object=JobExtractSchema)
