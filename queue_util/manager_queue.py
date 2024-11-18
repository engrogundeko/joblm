import asyncio
from .db_queue import DBQueue
from .log_queue import LogQueue
from .result_queue import ResultQueue
from .user_queue import UserQueue
from .email_queue import EmailQueue
from .scraper_queue import ScraperQueue
from discover.scrape import DiscoverHubScraper
from schemas.model import DBModel
from log import logger


class AsyncQueueManager:
    def __init__(self):
        self.result_queue = ResultQueue()
        self.email_queue = EmailQueue(self.result_queue)
        self.log_queue = LogQueue(self.email_queue)
        self.db_queue = DBQueue(self.result_queue)
        self.scraper_queue = ScraperQueue(
            self.log_queue, self.result_queue, self.db_queue, self.email_queue
        )
        self.user_queue = UserQueue(
            self.result_queue,
            self.db_queue,
            self.email_queue,
        )
        self.scrape_discover_hub = DiscoverHubScraper()
        logger.info("Initialized AsyncQueueManager with all queues.")

    async def enqueue(self, task):
        task_type = task["task_type"]
        task_id = task["id"]

        if task_type == "email":
            await self.email_queue.enqueue_task(task)
            logger.info(f"Task {task_id} enqueued to EmailQueue.")
        elif task_type == "db":
            await self.db_queue.enqueue_task(task)
            logger.info(f"Task {task_id} enqueued to DBQueue.")
        elif task_type == "log":
            await self.log_queue.enqueue_task(task)
            logger.info(f"Task {task_id} enqueued to LogQueue.")
        elif task_type == "scrape":
            await self.scraper_queue.enqueue_task(task)
            logger.info(f"Task {task_id} enqueued to ScraperQueue.")
        elif task_type == "user":
            await self.user_queue.enqueue_task(task)
            logger.info(f"Task {task_id} enqueued to UserQueue.")
        else:
            logger.warning(f"Task type {task_type} not recognized.")

    async def scrape_discover(self):
        logger.info("Starting DiscoverHub scraping task.")
        contents = await self.scrape_discover_hub.parse()
        logger.info("DiscoverHub scraping task completed.")
        for content in contents:
            model = DBModel(
                collection_name="job", operation_type="insert", data=content
            )
            task_data = model.to_dict
            await queue_manager.enqueue(task_data)

    async def run_all(self):
        logger.info("Starting all queue tasks.")
        await asyncio.gather(
            self.email_queue.process_tasks(),
            self.db_queue.process_tasks(),
            self.log_queue.process_tasks(),
            self.result_queue.process_tasks(),
            self.user_queue.process_tasks(),
            self.scraper_queue.process_tasks(),
        )
        logger.info("All queue tasks have started.")


queue_manager = AsyncQueueManager()
