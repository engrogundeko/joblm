import asyncio
from .queue_agent import AsyncQueueAgent
from log import logger

class ResultQueue(AsyncQueueAgent):
    def __init__(self):
        super().__init__()
        self.results = {}  # Dictionary to store results by task id
        self.result_events = {}  # Dictionary to store events for each task id
        logger.info("ResultQueue initialized.")

    async def store_result(self, result):
        """Store the result and set the event associated with this result's id."""
        task_id = result["id"]
        self.results[task_id] = result
        logger.info(f"Result stored for task {task_id}.")

        # Set the event to indicate result is ready
        if task_id in self.result_events:
            self.result_events[task_id].set()
        else:
            self.result_events[task_id] = asyncio.Event()
            self.result_events[task_id].set()
            logger.info(f"Event set for task {task_id}.")

    async def get_result_by_id(self, task_id):
        """Wait for the result by id if it is not yet ready, get it, and remove it."""
        if task_id not in self.result_events:
            self.result_events[task_id] = asyncio.Event()

        await self.result_events[task_id].wait()

        if task_id not in self.results:
            logger.error(f"Result for task {task_id} not found.")
            raise ValueError(f"Result for task {task_id} not found.")
        
        # Get the result and remove it from storage
        result = self.results.pop(task_id)  # Using pop() instead of get()
        del self.result_events[task_id]  # Clean up the event
        logger.info(f"Result retrieved and removed for task {task_id}.")
        
        return result

    async def process_tasks(self):
        while True:
            logger.info("Result Queue is waiting for event...")
            await self.event.wait()
            tasks_processed = 0

            while not self.queue.empty():
                result_task = await self.queue.get()
                try:
                    logger.info(f"Processing task {result_task['id']} with data: {result_task['data']}")
                    self.queue.task_done()
                    tasks_processed += 1
                except Exception as e:
                    logger.error(f"Error processing task {result_task['id']}: {e}")
                finally:
                    self.queue.task_done()

            # Log tasks processed count
            if tasks_processed > 0:
                logger.info(f"Processed {tasks_processed} tasks.")
            self.event.clear()
