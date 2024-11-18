import asyncio
from schemas.model import DBModel, EmailModel
from config import Config
from .queue_agent import AsyncQueueAgent
from parser import cv_parser
from log import logger  # Importing the custom logger


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
                    result = await self.handle_parsing(task["task"])
                    logger.info(
                        f"Parsing result: {result}"
                    )  # Log the result of parsing
                    await self.result_queue.store_result(result)  # Store result by id
                    logger.info(
                        f"Stored result for task {task['task']['id']}"
                    )  # Log when result is stored
                except Exception as e:
                    logger.error(
                        f"Error processing task {task}: {e}"
                    )  # Log any error that occurs
                finally:
                    self.queue.task_done()
            self.event.clear()

    async def handle_parsing(self, task):
        try:
            file_path = task["path"]
            user = task["user_name"]
            logger.info(
                f"Parsing CV for user {user} from file {file_path}"
            )  # Log parsing attempt

            # Perform CV parsing
            cv_md = await asyncio.to_thread(cv_parser.parse_cv, file_path)
            logger.info(
                f"Parsing completed for user {user}"
            )  # Log after parsing is done

            # Prepare data for database and email queues
            db_data = DBModel(
                collection_name=Config.user_collection,
                operation_type="insert",
                data={"username": user, "email": task["email"], "cv": cv_md},
            )
            await self.db_queue.enqueue_task(db_data.to_dict)
            logger.info(
                f"Database task enqueued for user {user}"
            )  # Log database task enqueue

            email_data = EmailModel(
                operation_type="user", data={"username": user, "cv": cv_md}
            )

            await self.email_queue.enqueue_task(email_data.to_dict)
            logger.info(
                f"Email task enqueued for user {user}"
            )  # Log email task enqueue

            return {"status": "success", "user": user, "cv": cv_md}
        except Exception as e:
            logger.error(
                f"Error during CV parsing for user {task['user_name']}: {e}"
            )  # Log error during parsing
            return {
                "status": "error",
                "error": str(e),
            }  # Return error status in case of failure
