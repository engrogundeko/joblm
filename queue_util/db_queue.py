import asyncio
from .queue_agent import AsyncQueueAgent
from repository import repository
# from pymongo import InsertOne, UpdateOne, DeleteOne
from scrape.service import scrape_service
from log import logger
from asyncio import Queue


class DBQueue(AsyncQueueAgent):
    def __init__(self, result_queue):
        super().__init__()
        self.batch = 1000
        self.queue = Queue(maxsize=self.batch)
        self.result_queue = result_queue

    async def process_tasks(self):
        while True:
            logger.info("DB Queue is waiting for event...")
            await self.event.wait()
            tasks = []
            while not self.queue.empty():
                db_task = await self.queue.get()
                logger.info(f"Database task received: {db_task["id"]}")
                tasks.append(db_task)

                # Process batch if we've accumulated 1000 tasks

                if len(tasks) == self.batch:
                    try:
                        await self.handle_database_task(tasks)
                        logger.info(f"Processed a batch of {self.batch} tasks.")
                    except Exception as e:
                        logger.error(f"Error processing batch of database tasks: {e}")
                    finally:
                        # Mark tasks as done in the queue
                        for _ in tasks:
                            self.queue.task_done()
                        tasks.clear()  # Clear tasks for the next batch

            # Process any remaining tasks after the loop
            if tasks:
                try:
                    await self.handle_database_task(tasks)
                    logger.info(f"Processed remaining batch of {len(tasks)} tasks.")
                except Exception as e:
                    print(e)
                    logger.error(f"Error processing remaining database tasks: {e}")
                finally:
                    for _ in tasks:
                        self.queue.task_done()

            # Clear the event after processing the tasks
            self.event.clear()

    async def handle_database_task(self, tasks):
        logger.info(f"Processing {len(tasks)} database tasks.")

        # Dictionary to group operations by collection
        db_tasks = {}

        # Prepare the tasks for bulk operation by collection
        for task in tasks:
            data = task["task"]
            collection_name = data["collection_name"]
            operation_type = data["operation_type"]
            operation_data = data["data"]

            if collection_name not in db_tasks:
                db_tasks[collection_name] = {"name": collection_name, "operations": []}

            # Append the correct operation based on operation type
            if operation_type == "insert":
                db_tasks[collection_name]["operations"].append({
                    "operation_type": "insert",
                    "data": operation_data
                })
            elif operation_type == "update":
                db_tasks[collection_name]["operations"].append({
                    "operation_type": "update",
                    "document_id": operation_data.get("document_id"),
                    "data": operation_data
                })
            elif operation_type == "delete":
                db_tasks[collection_name]["operations"].append({
                    "operation_type": "delete",
                    "document_id": operation_data.get("document_id")
                })

        # Execute the bulk write operation for each collection
        for collection in db_tasks.values():
            if collection["operations"]:
                try:
                    await asyncio.to_thread(
                        scrape_service.bulk_write,
                        collection["name"],
                        collection["operations"],
                    )
                    # await repository.bulk_write(
                    #     collection["name"], collection["operations"]
                    # )
                    logger.info(
                        f"Bulk write successful for collection {collection['name']}."
                    )
                except Exception as e:
                    logger.error(
                        f"Error in bulk write for collection {collection['name']}: {e}"
                    )

        logger.info("All tasks saved to database.")
        return tasks
