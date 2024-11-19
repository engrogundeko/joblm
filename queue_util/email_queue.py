import asyncio
from typing import List
from .queue_agent import AsyncQueueAgent
from utils.email_utils import send_job_email
from agent.agent import user_chain, to_dict
from schemas.model import EmailModel
from log import logger


class EmailQueue(AsyncQueueAgent):
    def __init__(self, result_queue):
        super().__init__()
        self.result_queue = result_queue

    async def process_tasks(self):
        while True:
            logger.info("Email Queue is waiting for event...")
            await self.event.wait()
            
            while not self.queue.empty():
                try:
                    email_task = await self.queue.get()
                    
                    # Safely access the task data
                    if isinstance(email_task, dict):
                        task_data = email_task.get('task', {})
                        operation_type = task_data.get('operation_type')
                        data = task_data.get('data', {})
                        
                        logger.info(f"Processing email task: {operation_type}")
                        
                        if operation_type == "user":
                            await self.handle_new_user(data)
                        elif operation_type == "scrape":
                            await self.handle_scrape(data)
                        else:
                            logger.warning(f"Unknown operation type: {operation_type}")
                    else:
                        logger.error(f"Invalid email task format: {email_task}")
                    
                except Exception as e:
                    logger.error(f"Error processing email task: {str(e)}")
                finally:
                    self.queue.task_done()
            
            self.event.clear()

    async def handle_scrape(self, tasks: List[dict]):
        try:
            dt = {}
            for job_list in tasks:
                email = job_list.pop("email")
                if email not in dt:
                    dt[email] = {"email": email, "job_list": []}
                dt[email]["job_list"].append(job_list)
            # data = task.get('data', {})
            # job_list = data.get('job_list', {})
            # to_email = job_list.pop('email', None)

            for email, data in dt.items():
                logger.info(f"Sending job email to: {email}")
                await asyncio.to_thread(send_job_email, email, data["job_list"])
                logger.info(f"Job email sent successfully to: {email}")
                asyncio.sleep(600)

        except Exception as e:
            logger.error(f"Error in handle_scrape: {str(e)}")
            raise

    async def handle_new_user(self, task_data: dict):
        try:
            logger.info("Processing new user registration")
            
            # Extract user data safely
            task = task_data.get('task', {})
            data = task.get('data', {})
            
            user_data = {
                "username": data.get('username'),
                "cv_markdown": data.get('cv'),
                "email": data.get('email')
            }

            # Validate required fields
            if not all(user_data.values()):
                missing_fields = [k for k, v in user_data.items() if not v]
                logger.error(f"Missing required fields: {missing_fields}")
                return

            # Process user data
            logger.info(f"Invoking user chain for: {user_data['email']}")
            result = await asyncio.to_thread(user_chain.invoke, user_data)
            result_dict = to_dict(result)

            # Send email
            if message := result_dict.get('message'):
                await self.send(message)
                logger.info(f"Registration email sent to: {user_data['email']}")
            else:
                logger.error("No message found in result")

        except Exception as e:
            logger.error(f"Error in handle_new_user: {str(e)}")
            raise

    async def send(self, message: str):
        try:
            # Implement your email sending logic here
            logger.info("Sending email message")
            # await send_email(message)
            logger.info("Email sent successfully")
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise
