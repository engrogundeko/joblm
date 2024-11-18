import asyncio


class AsyncQueueAgent:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.event = asyncio.Event()

    async def enqueue_task(self, task):
        await self.queue.put(task)
        self.event.set()

    async def process_tasks(self):
        raise NotImplementedError("Subclasses must implement process_tasks")




# # Example usage
# async def main():
#     queue_manager = AsyncQueueManager()

#     # Enqueue tasks
#     await queue_manager.enqueue("1", "email", "Send welcome email")
#     await queue_manager.enqueue("2", "db", "Update user record")
#     await queue_manager.enqueue("3", "log", "Error in sending email")

#     # Run the queue manager
#     asyncio.create_task(queue_manager.run_all())

#     # Wait and retrieve results by id
#     email_result = await queue_manager.result_queue.get_result_by_id("1")
#     print(f"Result for email task 1: {email_result}")

# asyncio.run(main())
