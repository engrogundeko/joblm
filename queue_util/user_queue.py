import asyncio
from schemas.model import DBModel, EmailModel
from config import Config
from app_write import AppwriteClient
from .queue_agent import AsyncQueueAgent
# from parser.cv_parser import cv_parser
from log import logger  # Importing the custom logger
from crea_user import create_user_with_cv


class UserQueue(AsyncQueueAgent):
    def __init__(self, result_queue, db_queue, email_queue):
        super().__init__()
        self.result_queue = result_queue
        self.db_queue = db_queue
        self.email_queue = email_queue

    async def process_tasks(self):
        while True:
            logger.info(
                "User Queue is waiting for event..."
            )  # Log when waiting for tasks
            await self.event.wait()
            while not self.queue.empty():
                task = await self.queue.get()
                try:
                    logger.info(f"Event received: {task}")  # Log when task is received
                    await self.handle_parsing(task["task"]) 
                except Exception as e:
                    logger.error(
                        f"Error processing task {task}: {e}"
                    )  # Log any error that occurs
                finally:
                    self.queue.task_done()
            self.event.clear()

    async def handle_parsing(self, task):
        try:
            email = task["email"]
            file_path = task["file_path"]
            await create_user_with_cv(email, file_path)
        except Exception as e:
            logger.error(
                f"Error during CV parsing for user{e}"
            )  # Log error during parsing
            return {
                "status": "error",
                "error": str(e),
            }  # Return error status in case of failure
