
from asyncio import AbstractEventLoop
from threading import Thread
import asyncio
import aiofiles
import aiofiles.os
import os

class Test:
  def __init__(self,loop:AbstractEventLoop):
    self._loop = loop 
    self.is_debug_log = True
    self.queue = asyncio.Queue() #loop=self._loop
    self.future = asyncio.run_coroutine_threadsafe(self._make_requests(), self._loop)

  def my_log(self,message):
    if self.is_debug_log:
      task_name = ''
      try:
        task = asyncio.current_task()
        task_name = task.get_name()
      except RuntimeError:
        pass
      print(f'{task_name!r}: {message!r}')

  def join(self):
    #self.future.result()
    pass

  async def _from_queue(self,item):

    self.my_log(f'get item {item}')
    full_path = __file__
    # if not await aiofiles.os.path.isdir(os.path.dirname(full_path),loop=self._loop):
    #   await aiofiles.os.makedirs(os.path.dirname(full_path),loop=self._loop)

    # async with aiofiles.open(full_path,'r',encoding='UTF-8',loop=self._loop) as f:
    #   data = await f.read()
    #   self.my_log(data[0:10])

  async def insert_to_queue(self,item):
    await self.queue.put(item)

  async def _make_requests(self):
    self.my_log('start _make_requests')
    await asyncio.sleep(1)
    
    item = await self.queue.get()
    await asyncio.sleep(5)
    self.my_log(f'get item {item}')
    #распаковываем данные:
    folder, arg_string, hash_string, result = item

    await self._from_queue(item)
    

    self.my_log('stop _make_requests')

  

class ThreadedEventLoop(Thread):
 def __init__(self, loop: AbstractEventLoop):
  super().__init__()
  self._loop = loop
  self.daemon = True
 def run(self):
  self._loop.run_forever()
loop = asyncio.new_event_loop()
asyncio_thread = ThreadedEventLoop(loop)
asyncio_thread.start()

t = Test(loop)

async def example():
  t.my_log('start example')
  await asyncio.sleep(1)
  await t.insert_to_queue('test queue')
  t.my_log('stop example')

async def main():
  tasks = [
      example()
  ]

  resluts = await asyncio.gather(*tasks)

  #await t.queue.join()

asyncio.run(main())