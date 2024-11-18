from .queue_agent import AsyncQueueAgent


class LogQueue(AsyncQueueAgent):
    def __init__(self, result_queue):
        super().__init__()
        self.results = result_queue

    async def process_tasks(self):
        while True:
            print("Log Queue is waiting for event...")
            await self.event.wait()
            while not self.queue.empty():
                log_task = await self.queue.get()
                self.queue.task_done()
            self.event.clear()

    async def handle_log_task(self): ...
