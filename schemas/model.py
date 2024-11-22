from datetime import datetime, date
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict


# @dataclass
# class Model:
#     id: str = datetime.now().strftime("%H:%M:%S")
#     task_type: str  # Removed Literal; it's now sufficient to just define this field


#     def __call__(self, *args, **kwds) -> Dict:
#         return asdict(self)
@dataclass
class UserModel:
    email: str
    file_path: str
    id: str = datetime.now().strftime("%H:%M:%S")
    task_type: str = "user"

    @property
    def to_dict(self):
        return {
            "id": self.id,
            "task_type": self.task_type,
            "task": {"email": self.email, "file_path": self.file_path},
        }


@dataclass
class ScrapeModel:
    id: str = datetime.now().strftime("%H:%M:%S")
    task_type: str = "scrape"
    data: Optional[Dict] = None

    @property
    def to_dict(self):
        return asdict(self)


@dataclass
class DBModel:
    collection_name: str
    operation_type: str
    data: Dict
    id: str = datetime.now().strftime("%H:%M:%S")
    task_type: str = "db"
    is_vector: bool = False

    @property
    def to_dict(self, *args, **kwds):
        return {
            "id": self.id,
            "task_type": self.task_type,
            "task": {
                "data": self.data,
                "operation_type": self.operation_type,
                "collection_name": self.collection_name,
            },
        }


@dataclass
class EmailModel:
    data: Dict
    operation_type: str
    id: str = datetime.now().strftime("%H:%M:%S")
    task_type: str = "email"

    @property
    def to_dict(self, *args, **kwds):
        return {
            "id": self.id,
            "task_type": self.task_type,
            "task": {
                "data": self.data,
                "operation_type": self.operation_type,
            },
        }


@dataclass
class Job:
    site: str
    job_url: str
    title: str
    company: str
    location: str
    date_posted: str
    job_type: str
    salary_source: str
    interval: str
    min_amount: str
    max_amount: str
    is_remote: str
    listing_type: str
    job_level: str
    job_function: str
    job_url_direct: str
    emails: str
    description: str
    currency: str
    company_logo: str
    company_addresses: str
    company_num_employees: str
    company_revenue: str
    company_description: str
    company_industry: str
    company_url: str
    company_url_direct: str

    def __post_init__(self):
        if isinstance(self.date_posted, date):
            date_str = self.date_posted.strftime("%d/%m/%Y")
            self.date_posted = date_str

        if isinstance(self.date_posted, str):
            return self.date_posted

    @property
    def to_dict(self):
        return asdict(self)
       


@dataclass
class ResultModel:
    id: str
    data: Dict
    task_type: str = "result"

    @property
    def to_dict(self, *args, **kwds):
        return {
            "id": self.id,
            "task_type": self.task_type,
            "task": {
                "data": self.data,
            },
        }


@dataclass
class ScraperTaskModel:
    site_name: List[str]
    search_term: str
    location: str
    results_wanted: int
    hours_old: int
    country_indeed: str
    linkedin_fetch_description: bool = True
    id: str = datetime.now().strftime("%H:%M:%S")
    is_remote: bool = False
    google_search_term: Optional[str] = None

    @property
    def to_dict(self) -> dict:
        return asdict(self)
