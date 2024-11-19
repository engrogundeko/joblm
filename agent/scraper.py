from asyncio import to_thread, sleep

from pydantic import ValidationError

from log import logger
from .llm import GeminiLLM
from config import Config
from .agent import job_extract_prompt
from .schema import job_extract_parser
from .agent import job_chain, to_dict
from vector_database import vector_db
from queue_util.manager_queue import queue_manager
from schemas.model import ScrapeModel, DBModel, Job, EmailModel

# from scrape.service import ScraperService
from asyncio_throttle import Throttler


class ScraperAgent:
    def __init__(self) -> None:
        self.gemini_llm = GeminiLLM()
        self.scrape_batch = 10
        # Allow a maximum of 4500 calls per day => ~3 calls per minute
        self.llm_throttler = Throttler(rate_limit=3, period=60)
        # Allow a maximum of 15 calls per minute
        self.job_throttler = Throttler(rate_limit=15, period=60)

    async def to_dict(self, arg):
        return to_dict(arg)

    def _get_job_text(self, job: Job):
        return f"{job.to_dict}"

    async def process_job_info(self, resume_text: str, email: str):
        try:
            # Initialize jobs list
            jobs = []
            
            # Get job data
            job = await job_chain.ainvoke({"resume_text": resume_text})
            job_task = await self.to_dict(job)
            task = ScrapeModel(data=job_task["jobschema"])
            task_id = task.id
            task_job = task.to_dict
            
            # Enqueue task
            await queue_manager.enqueue(task_job)
            
            # Get results
            results = await queue_manager.result_queue.get_result_by_id(task_id)
            if results and "task" in results:
                re_task = results["task"]
                jobs = re_task.get("data", [])

            # Process jobs in batches
            if jobs:
                job_batch = []
                for job_data in jobs:
                    if isinstance(job_data, dict):
                        job_data.pop("id", None)  # Remove id if exists
                        job = Job(**job_data)
                        job_batch.append((job, email))

                    # Process batch when it reaches size
                    if len(job_batch) >= self.scrape_batch:
                        await self._extract_job_batch(job_batch)
                        job_batch = []  # Clear batch

                # Process remaining jobs
                if job_batch:
                    await self._extract_job_batch(job_batch)

            return len(jobs)  # Return number of jobs processed

        except Exception as e:
            logger.error(f"Error in process_job_info: {str(e)}")
            raise

    def _format_db_data(self, job_data):
        return {
            "job_title": str(job_data.get("job_title", ""))[:255],
            "job_description": str(job_data.get("job_description", ""))[:65535],
            "required_skills": "|".join(
                str(skill) for skill in job_data.get("required_skills", [])
            )[:65535],
            "responsibilities": "|".join(
                str(resp) for resp in job_data.get("responsibilities", [])
            )[:65535],
            "qualifications": "|".join(
                str(qual) for qual in job_data.get("qualifications", [])
            )[:65535],
            "location": str(job_data.get("location", ""))[:255],
            "salary_range": str(job_data.get("salary_range", ""))[:255],
            "company_info": str(job_data.get("company_info", ""))[:65535],
            "keywords": "|".join(
                str(keyword) for keyword in job_data.get("keywords", [])
            )[:65535],
            "email": str(job_data.get("email", ""))[:255],
        }

    async def _extract_job_batch(self, job_batch: list[tuple[Job, str]]):
        """Process a batch of jobs at once"""
        try:
            db_batch = []
            email_batch = []
            vector_batch = []
            for job_data, email in job_batch:
                async with self.job_throttler:
                    job_url = job_data.job_url
                    print(job_url)
                    job_text = self._get_job_text(job_data)
                    job_extract = await self.get_llm()
                try:
                    job_extract = await job_extract.ainvoke({"job_text": job_text})
                except ValidationError as e:
                    logger.error(f"Validation error for job: {e}")
                    continue

                job_extract = await self.to_dict(job_extract)
                job_result = job_extract["jobextractschema"]

                # Prepare database entry
                job_data_dict = job_result.copy()
                job_data_dict["email"] = email
                job_data_url = job_data_dict.copy()
                job_data_url["job_url"] = job_url
                db_data = DBModel(
                    collection_name=Config.job_collection,
                    operation_type="insert",
                    data=self._format_db_data(job_data_dict),
                )
                email_batch.append((job_data_url))
                db_batch.append(db_data.to_dict)

                # Prepare vector entry
                vector_data = self._get_vector_data(job_result)
                vector_batch.append(vector_data)
            # Batch operations outside the throttled section
            # Process batches
            if db_batch:
                for db in db_batch:
                    await queue_manager.enqueue(db)

            if email_batch:
                email_data = EmailModel(data=email_batch, operation_type="scrape")
                await queue_manager.enqueue(email_data.to_dict)

            if vector_batch:
                await vector_db.upsert(data=vector_batch, namespace="job")

            logger.info(f"Processed batch of {len(job_batch)} jobs")

        except Exception as e:
            logger.error(f"Error in _extract_job_batch: {e}")

    def _get_vector_data(self, job_result: dict):
        data = f"""
            Job Title: {job_result["job_title"]}
            Job Description: {job_result["job_description"]}
            Responsibilities: {', '.join(job_result["responsibilities"])}
            Qualifications: {', '.join(job_result["qualifications"])}
            Salary Range: {job_result["salary_range"]}
            Company Info: {job_result["company_info"]}
            """

        metadata = {
            "location": job_result["location"],
            "qualifications": ", ".join(job_result["qualifications"]),
            "required_skills": ", ".join(job_result["required_skills"]),
            "salary_range": job_result["salary_range"],
            "keywords": ", ".join(job_result["keywords"]),
        }

        return data, metadata

    async def get_llm(self):
        try:
            # Use throttler to limit LLM API calls
            async with self.llm_throttler:
                llm = await self.gemini_llm.get_llm()
                return job_extract_prompt | llm | job_extract_parser
        except Exception as e:
            logger.error(f"Error in get_llm: {e}")
            # Wait for 20 hours if quota is exceeded, then retry
            await sleep(20 * 60 * 60)
            return await self.get_llm()
