from typing import List

from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field


class PersonalSchema(BaseModel):
    full_name: str = Field(
        default="N/A",
        description="Candidate's full name, e.g., 'John Doe'. Please provide the full name of the candidate as listed on the CV or resume."
    )
    phone_number: str = Field(
        default="N/A",
        description="Primary contact number, labeled as 'Phone Number' or similar, e.g., 'Contact: +1 (555) 123-4567'. Please extract the phone number listed under a contact label."
    )
    email_address: str = Field(
        default="N/A",
        description="Primary email address, e.g., 'johndoe@example.com'. Please extract the candidate's main email address."
    )
    linkedin_profile: str | None = Field(
        default="N/A",
        description="URL to LinkedIn or other professional profile links, e.g., 'https://www.linkedin.com/in/johndoe'. Please provide the full URL to the candidate's LinkedIn or another relevant professional online profile.",
    )
    professional_title: str | None = Field(
        default="N/A",
        description="Current job title or stated professional goal, e.g., 'Software Engineer' or 'Data Scientist seeking to leverage AI skills'. Please provide the candidate's current professional title or stated career objective, if available."
    )


class WorkExperienceDetails(BaseModel):
    job_title: str = Field(
        default="N/A",
        description="Position title, e.g., 'Software Engineer, Product Manager, Data Scientist'. Please provide the full title of the job the candidate held."
    )
    company: str = Field(
        default="N/A",
        description="Company or organization name, e.g., 'Google, Microsoft, Tesla'. Please provide the full name of the company or organization."
    )
    location: str = Field(
        default="N/A",
        description="City, State, Country, e.g., 'San Francisco, CA, USA'. Please list the city, state (if applicable), and country where the candidate worked."
    )
    date: str = Field(
        default="N/A",
        description="Start and end dates, e.g., 'January 2020 - December 2022'. Please provide the month and year of both the start and end of employment, or just the start date if still employed."
    )
    responsibilities: str = Field(
        default="N/A",
        description="Key responsibilities, e.g., 'Developed and maintained web applications, led team meetings, managed project timelines'. Please list the candidate’s key tasks and duties in the role."
    )
    achievements: str = Field(
        default="N/A",
        description="Key achievements, e.g., 'Increased revenue by 30%, improved customer satisfaction score by 15%, reduced system downtime by 20%'. Please provide measurable or impactful achievements during the role."
    )
    technology_used: str = Field(
        default="N/A",
        description="List of tools, languages, or technologies used, e.g., 'Python, JavaScript, AWS, MySQL'. Please provide a comma-separated list of technologies, languages, or tools the candidate used in this role."
    )


class EducationDetails(BaseModel):
    degree: str = Field(
        default="N/A",
        description="Degree name (e.g., 'Bachelor's, Master's, Ph.D.', or 'Associate's'). Please provide the exact degree the candidate has completed."
    )
    discipline: str = Field(
        default="N/A",
        description="Major or specialization, e.g., 'Computer Science'. Please specify the candidate's field of study or specialization in string."
    )
    institution: str = Field(
        default="N/A",
        description="Institution name, e.g., 'University of California, Stanford University, Massachusetts Institute of Technology'. Please provide the full name of the institution the candidate attended."
    )
    graduation_date: str = Field(
        default="N/A",
        description="Date or year of graduation, e.g., 'May 2021, 2023'. Please specify the month and year of graduation, or just the year if that’s all that’s available.",
    )
    achievements: str = Field(
        default="N/A",
        decription="Honors, GPA, or notable projects, e.g., 'Graduated with honors, GPA: 3.9, Led a team project on AI-based image recognition'. Please provide a list of any notable academic achievements or projects."
    )


class SkillDetails(BaseModel):
    technical: str = Field(
        default="N/A",
        description="List of technical skills, e.g., 'Python, Java, SQL, Machine Learning, Cloud Computing'. Please provide a comma-separated list of the candidate's technical abilities or expertise."
    )
    soft: str = Field(
        default="N/A",
        description="List of soft skills, e.g., 'Communication, Leadership, Problem Solving, Teamwork'. Please provide a comma-separated list of the candidate’s interpersonal or non-technical skills."
    )
    languages: str = Field(
        default="N/A",
        description="Languages spoken and proficiency level, e.g., 'English (Fluent), French (Intermediate), Spanish (Basic)'. Please list the languages spoken along with the proficiency level for each language."
    )
    certification: str = Field(
        default="N/A",
        description="Relevant professional certifications, e.g., 'Certified Data Scientist, AWS Certified Solutions Architect, PMP'. Please provide a comma-separated list of any certifications the candidate holds."
    )


class ProjectDetails(BaseModel):
    name: str = Field(
        default="N/A",
        description="Name of the project, e.g., 'AI-Based Image Classification, E-Commerce Website Development'. Please provide the full name of the project.",
    )
    description: str = Field(
        default="N/A",
        description="Brief description of the project, e.g., 'Developed an AI-based system to classify images into categories using deep learning techniques.' Please provide a concise summary of the project and its goals."
    )
    technology_used: str = Field(
        default="N/A",
        description="List of tools or technologies used, e.g., 'Python, TensorFlow, AWS, PostgreSQL'. Please provide a comma-separated list of tools, frameworks, or technologies involved."
    )
    role: str = Field(
        default="N/A",
        description="Candidate’s role and specific contributions, e.g., 'Lead Developer, responsible for designing the architecture and implementing the backend services.' Please provide a clear description of the candidate's role and their contributions."
    )
    results: str = Field(
        default="N/A",
        description="Results or impact of the project, if measurable, e.g., 'Increased image classification accuracy by 20%, reduced processing time by 50%.'. Please provide any measurable results or outcomes from the project."
    )


class AwardDetails(BaseModel):
    name: str = Field(
        default="N/A",
        description="Name of the award, e.g., 'Best Research Paper Award, Employee of the Year'. Please provide the full name of the award."
    )
    issuing_organization: str = Field(
        default="N/A",
        description="Organization that issued the award, e.g., 'IEEE, Google'. Please provide the full name of the issuing organization."
    )
    date: str = Field(
        default="N/A",
        description="Date or year of award, e.g., 'October 2022'. Please use the 'Month Year' format."
    )
    description: str = Field(
        default="N/A",description="Brief description of the award")


class VolunteerDetails(BaseModel):
    name: str = Field(
        default="N/A",
        description="Name of the organization or activity, e.g., 'Local Animal Shelter, University Coding Club'. Please provide the full name of the organization or activity."
    )
    position: str = Field(
        default="N/A",
        description="Candidate’s role or position, e.g., 'Volunteer, President'. Please specify the role held in the organization or activity."
    )
    dates: str = Field(
        default="N/A",
        description="Duration of involvement, e.g., 'October 2022 - Present' or 'October 2022 - March 2023'. Please use the 'Month Year' format for both start and end dates."
    )
    responsibilities: str = Field(
        default="N/A",
        description="Key contributions and achievements, e.g., 'Led a team of 10 volunteers to organize weekly events, increased donations by 30%.'. Please provide a summary of the candidate’s contributions and achievements."
    )


class PublicationDetails(BaseModel):
    title: str = Field(
        default="N/A",
        description="Title of the publication or research, e.g., 'Deep Learning for Computer Vision'. Please provide the full title of the publication or research."
    )
    authors: str = Field(
        default="N/A",
        description="List of authors, e.g., 'John Doe, Jane Smith, Michael Johnson'. Please list the authors in the format 'First Last', separated by commas."
    )
    date: str = Field(
        default="N/A",
        description="Date of publication, e.g., 'October 2022'. Please use the 'Month Year' format."
    )
    conference: str = Field(
        default="N/A",
        description="Name of the journal or conference, e.g., 'International Conference on Computer Vision'. Please provide the full name of the journal or conference."
    )
    link: str = Field(
        default=[],
        description="Link to the publication or DOI if available, e.g., 'https://doi.org/10.1109/ICCV.2021.00056'. If no link or DOI is available, leave it blank."
    )


class InterestDetails(BaseModel):
    interest: List[str] = Field(
        default="N/A",
        description="List of interests, e.g., 'Machine Learning, Data Science, Reading'. Provide interests from the resume; if not available, return '[]'."
    )
    professional_submit: str = Field(
        default="N/A",
        description="Summary or goal statement, e.g., 'Seeking a challenging role in AI'. If a professional summary or objective is not available, return empty string ' '."
    )


class AffiliationDetails(BaseModel):
    name: str = Field(
        default="N/A",
        description="Name of the professional organization, e.g., 'IEEE, Association for Computing Machinery'. Please provide the full name of the organization."
    )
    position: str = Field(
        default="N/A",
        description="Role or position within the organization, e.g., 'Member, Vice President of Technology'. Please specify the role or position held, including any leadership titles."
    )
    date: str = Field(
        default="N/A",
        description="Duration of membership, e.g., 'October 2022 - Present' or 'October 2022 - March 2023'. Please use the 'Month Year' format for both start and end dates."
    )


class AffiliationSchema(BaseModel):
    affiliation: List[AffiliationDetails]


# class InterestSchema(BaseModel):
#     interest: List[InterestDetails]


class ProjectSchema(BaseModel):
    project: List[ProjectDetails]


class AwardSchema(BaseModel):
    award: List[AwardDetails]


class EducationItem(BaseModel):
    educationDetails: EducationDetails


class EducationSchema(BaseModel):
    education: List[EducationItem]


class SkillSchema(BaseModel):
    skills: List[SkillDetails]


class VolunteerSchema(BaseModel):
    volunteer: List[VolunteerDetails]
    
    
class PublicationSchema(BaseModel):
    publication: List[PublicationDetails]


class WorkExperienceSchema(BaseModel):
    work_experience: List[WorkExperienceDetails]


affiliation_parser = PydanticOutputParser(pydantic_object=AffiliationSchema)
personal_parser = PydanticOutputParser(pydantic_object=PersonalSchema)
interest_parser = PydanticOutputParser(pydantic_object=InterestDetails)
publication_parser = PydanticOutputParser(pydantic_object=PublicationSchema)
work_parser = PydanticOutputParser(pydantic_object=WorkExperienceSchema)
skill_parser = PydanticOutputParser(pydantic_object=SkillSchema)
award_parser = PydanticOutputParser(pydantic_object=AwardSchema)
project_parser = PydanticOutputParser(pydantic_object=ProjectSchema)
education_parser = PydanticOutputParser(pydantic_object=EducationSchema)
volunteer_parser = PydanticOutputParser(pydantic_object=VolunteerSchema)
