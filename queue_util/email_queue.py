import asyncio
import logging
from .queue_agent import AsyncQueueAgent
from utils.email_utils import send_job_email
from agent.agent import user_chain, to_dict
from schemas.model import EmailModel
from log import logger  # Importing the custom logger


class EmailQueue(AsyncQueueAgent):
    def __init__(self, result_queue):
        super().__init__()
        self.result_queue = result_queue

    async def process_tasks(self):
        while True:
            logger.info(
                "Email Queue is waiting for event..."
            )  # Log when the queue is waiting for tasks
            await self.event.wait()
            while not self.queue.empty():
                email_task: EmailModel = await self.queue.get()
                logger.info(
                    f"Email Task Received: {email_task}"
                )  # Log the received email task

                try:
                    await asyncio.sleep(600)  # Simulate processing time
                    task = email_task
                    if task.operation_type == "user":
                        logger.info(
                            "Handling new user task."
                        )  # Log the operation type being handled
                        
                        await self.handle_new_user(task.data)
                    elif task.operation_type == "scrape":
                        logger.info(
                            "Handling scrape task."
                        )  # Log the operation type being handled
                        await self.handle_scrape(task.data)
                except Exception as e:
                    logger.error(
                        f"Error processing email task: {e}"
                    )  # Log any error that occurs
                    # Optionally, you can enqueue this error to a log queue
                    # await self.log_queue.enqueue_task(f"Email Error: {str(e)}")
                finally:
                    self.queue.task_done()
            self.event.clear()

    async def handle_scrape(self, task: dict):
        data = task["data"]
        job_list = data["job_list"]
        to_email = job_list.pop("email")
        try:
            await asyncio.to_thread(
                send_job_email, to_email, job_list
            )
            await asyncio.sleep(600)
        except Exception as e:
            print(str(e))

    async def handle_new_user(self, tk):
        logger.info(
            "Handling new user registration."
        )  # Log when handling new user task
        task = tk["task"]
        data = task["data"]
        dt = {
            "username": data["username"],
            "cv_markdown": data["cv"],
            "email": data["email"],
        }

        try:
            # Process the user data and invoke the chain
            result = await asyncio.to_thread(user_chain.invoke, dt)
            result = to_dict(result)

            # Send the result via email
            await self.send(result["message"])
            logger.info(
                f"User registration message sent to {data['email']}"
            )  # Log the email sent
        except Exception as e:
            logger.error(
                f"Error processing user task: {e}"
            )  # Log error if the user task fails            )  # Log error if email fails
