from typing import List


class Scholarship(BaseModel):
    content: str
    application_link: str

class Schola4Dev(BaseModel):
    link: str
    title: str

class ListScholar4Dev(BaseModel):
    scholarships: List[Schola4Dev]

