from typing import List


class Config:
    job_collection = "jobs"
    user_collection = "users"
    collections: List[str] = ["jobs", "users"]
