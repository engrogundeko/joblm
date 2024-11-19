from .queue_agent import AsyncQueueAgent
import asyncio
from schemas.model import ScrapeModel, DBModel, EmailModel, ResultModel
from jobspy import scrape_jobs
from datetime import datetime
from log import logger  # Import the configured logger


class ScraperQueue(AsyncQueueAgent):
    def __init__(self, log_queue, result_queue, db_queue, email_queue):
        super().__init__()
        self.result_queue = result_queue
        self.email_queue = email_queue
        self.log_queue = log_queue
        self.db_queue = db_queue
        logger.info("Initialized ScraperQueue with result, email, log, and db queues.")

    async def process_tasks(self):
        """Process scraping tasks."""
        while True:
            logger.info("Process Queue is waiting for event...")
            await self.event.wait()
            while not self.queue.empty():
                scraper_task = await self.queue.get()
                try:
                    logger.info(f"Processing scraping task: {scraper_task['id']}")
                    await self.handle_scraping_task(scraper_task)
                    logger.info(f"Scraping task completed: {scraper_task['id']}")
                except Exception as e:
                    logger.error(
                        f"Error processing scraping task {scraper_task['id']}: {e}"
                    )
                finally:
                    self.queue.task_done()
            self.event.clear()
            logger.info("No more tasks in queue; waiting for the next event.")

    async def handle_scraping_task(self, scraper_task):
        logger.info("Starting to handle a scraping task.")
        task = scraper_task["data"]
        task_id = scraper_task["id"]
        # Define the task parameters for scraping jobs
        task_parameters = {
            "site_name": ["indeed", "linkedin", "zip_recruiter", "google"],
            "search_term": task["search_term"],
            "location": task["location"],
            "results_wanted": task["results_wanted"],
            "hours_old": task["hours_old"],
            "country_indeed": task["country_indeed"],
            "linkedin_fetch_description": True,
            "is_remote": task["is_remote"],
            "google_search_term": task["google_search_term"],
        }
        # Scrape jobs in a non-blocking way
        jobs = None
        try:
            jobs = await asyncio.to_thread(scrape_jobs, **task_parameters)
            logger.info(
                f"Scraping completed with {len(jobs)} jobs found for search term: {task['search_term']}"
            )
        except Exception as e:
            logger.error(f"Error during job scraping for task {task_id}: {e}")
            # return  # Exit early if scraping fails

        # Create the ScrapeModel instance
        if jobs is not None:
            jobs = jobs.to_dict(orient="records")
            result_data = ResultModel(data=jobs, id=task_id)
            await self.result_queue.store_result(result_data.to_dict)
