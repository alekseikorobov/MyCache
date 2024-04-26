"""
A corrected version of the program in following stackoverflow question:
https://stackoverflow.com/questions/51775413/python-asyncio-run-coroutine-threadsafe-never-running-coroutine
"""

import asyncio
from threading import Thread
from contextlib import contextmanager
import time

@contextmanager
def background_thread_loop():
    def run_forever(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    loop = asyncio.new_event_loop()
    try:
        thread = Thread(target=run_forever, args=(loop,),daemon=True)
        thread.start()
        yield loop
    finally:
        print('end background_thread_loop')
        loop.call_soon_threadsafe(loop.stop)
        thread.join()
        print('done background_thread_loop')


class Foo:


    # Synchronous methods

    def _run_async(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        future.result()

    def __init__(self, loop):
        self.is_run = False
        self._loop = loop
        self._run_async(self._init())

    def put(self, item):
        return self._run_async(self._put(item))

    def join(self):
        return self._run_async(self._join())

    # Async methods

    async def _init(self):
        self._queue = asyncio.Queue()
        self.is_run = True
        self._consumer_task = self._loop.create_task(self._consumer())

    async def _consumer(self):
        while self.is_run:
            message = await self._queue.get()
            if message == "END OF QUEUE":
                break
            print(f"Processing {message!r}...")

    async def _join(self):
        return await self._consumer_task

    async def _put(self, item):
        return await self._queue.put(item)


def main():
    with background_thread_loop() as loop:
        f = Foo(loop)
        time.sleep(2)
        f.put("This is a message")
        time.sleep(2)
        f.put("END OF QUEUE")
        time.sleep(2)
        print('end main')
        f.join()
    print('done main')

if __name__ == "__main__":
    main()