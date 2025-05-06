import asyncio
from typing import Callable
from config import DB_PATH
import aiosqlite

class TaskExecutor:
    def __init__(self, queue):
        self.queue = queue
        self.db_path = DB_PATH[20:]

    def run_async_tasks(self):
        asyncio.run(self.process_queue())

    async def process_queue(self):
        async with aiosqlite.connect(self.db_path) as db:
            while True:
                try:
                    task = self.queue.get()

                    if task is None:
                        break

                    method, args, kwargs = task
                    try:
                        await method(db, *args, **kwargs)
                    except Exception as e:
                        raise e
                except KeyboardInterrupt:
                    raise e

    def enqueue_task(self, method: Callable, *args, **kwargs):
        self.queue.put((method, args, kwargs))

    def close(self, process):
        self.queue.put(None)
        process.join()