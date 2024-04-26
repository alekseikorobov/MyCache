import hashlib
import json
from enum import Enum
import pandas as pd
import os
import time
import asyncio
import aiofiles
import aiofiles.os
import random
from asyncio import AbstractEventLoop
from threading import Thread
import aiojobs

class my_persistent_cache:

  def __init__(self,db_file = None, is_debug_log=False):
    self.db_file = db_file
    self.is_debug_log = is_debug_log
    
    # кеш для временного хранения данных, до тех пор пока эти данные не записали в файл,
    # после записи в файл, очищаем словарь по хешу
    self.__mem_storage_data = {}

    # кеш для хранения хеша, чтобы понимать существует ли файл с таким ключом или нет (чтобы лишний раз не проверять на диске)
    self.__mem_storage_meta = {}

    if self.db_file is None or self.db_file == '':
      raise(Exception('parameter db_file is cannot be empty!'))

    if os.path.isfile(self.db_file):
      self.my_log(f'read from {self.db_file}')
      with open(self.db_file,'r',encoding='UTF-8') as f:
        for line in f.readlines():
          line = line.rstrip('\n')
          full_path,arg_string = line.split('\t')
          self.my_log(f'{full_path} - {arg_string=}')
          self.__mem_storage_meta[full_path] = arg_string
      self.my_log(f'not keys {len(self.__mem_storage_meta)}')
    else:
      if not os.path.isdir(os.path.dirname(self.db_file)):
        os.makedirs(os.path.dirname(self.db_file))

    # словарь блокировок для каждого хеша, 
    # нужен для того чтобы при работе с одним и тем же хешом не произошла повторная обработка, пока не завершена первая
    self.dict_lock = {}
    self.scheduler = None
    self.job = None

  def start_scheduler(self):
    if self.scheduler is None:
      self.scheduler = aiojobs.Scheduler()

  async def join(self):
    if self.job is not None:
      await self.job.wait()
    if self.scheduler is not None:
      await self.scheduler.close()


  def __generate_hash(self,*args,**kwargs)->tuple[str,str]:
    '''
    функция создает хэш из параметров, возвращает str аргументов и хеш
    '''
    all_args = {
      'args':args,
      'kwargs':kwargs,
    }
    arg_string = json.dumps(all_args, sort_keys=True)
    arg_string_e = arg_string.encode()
    hash_string = hashlib.sha256(arg_string_e).hexdigest()
    return arg_string,hash_string
  
  async def __save_data_to_disk(self, folder, arg_string, hash_string, result):
    # делаем запись данных
    
    self.my_log('start __save_data_to_disk')
      
    full_path = os.path.join(folder, hash_string)

    self.my_log(f'check {full_path}')
    #делаем блокировку пока работаем с определенным хешом
    async with self.dict_lock.get(full_path, asyncio.Lock()):
      if not await aiofiles.os.path.isdir(os.path.dirname(full_path)):
        await aiofiles.os.makedirs(os.path.dirname(full_path))

      self.my_log(f'create {full_path}')
      async with aiofiles.open(full_path,'w',encoding='UTF-8') as f:
        await f.write(result)

      #[предположим что запись на диск это долгая операция]
      #await asyncio.sleep(3)
      
      self.my_log(f'update {self.db_file}')
      async with aiofiles.open(self.db_file,'a',encoding='UTF-8') as f:
        await f.write(f'{full_path}\t{arg_string}\n')

      # очищаем словарь с данными из памяти (далеее чтение должно происходить только из файла)
      if full_path in self.__mem_storage_data:
        del self.__mem_storage_data[full_path]

      #сохраняем информацию о том что уже записали в файл, дальше будем проверять по этому ключу, чтобы читать с диска
      self.__mem_storage_meta[full_path] = arg_string

  def my_log(self,message):
    if self.is_debug_log:
      task_name = ''
      try:
        task = asyncio.current_task()
        task_name = task.get_name()
      except RuntimeError:
        pass
      print(f'{task_name}: {message}')

  def async_cache(self, folder):
    def wrap_function(func):
      async def wrapper(*args, **kwargs):
          self.start_scheduler()
          self.my_log('start async_cache')

          arg_string, hash_string = self.__generate_hash(*args,**kwargs)
          self.my_log(f'{hash_string=}')

          full_path = os.path.join(folder, hash_string)
          
          if full_path not in self.dict_lock:
            self.my_log('create lock')
            #создаем блокировку для уникального хеша
            self.dict_lock[full_path] = asyncio.Lock()

          self.my_log(f'{self.dict_lock=}')
          #ставим блокировку, пока пытаемся прочитать данные в памяти и если нет, то записываем на диск
          async with self.dict_lock[full_path]:
            self.my_log(f'{self.__mem_storage_data=}')
            # если данные уже лежат в памяти, тогда берем из памяти (в случае если еще не успели записать на диск), функцию не вызываем
            if full_path in self.__mem_storage_data:
              return self.__mem_storage_data[full_path]

            self.my_log(f'{self.__mem_storage_meta=}')
            # если данные уже лежат на диске, тогда читаем с диска, функцию не вызываем
            if full_path in self.__mem_storage_meta:
              if not await aiofiles.os.path.isfile(full_path):
                raise(Exception(f'not found file by path {full_path}'))

              async with aiofiles.open(full_path,'r',encoding='UTF-8') as f:
                result = await f.read()
              self.my_log(f'read from cache: {full_path}, len result data: {len(result)}')
              return result

            if not asyncio.iscoroutinefunction(func):
                raise(Exception(f'function {func.__name__} must be mark as async'))
            
            # иначе вызываем функцию

            coroutin_func = func(*args, **kwargs)
            result = await coroutin_func            
            # до тех пор пока результат функции не записали на диск держим в памяти
            self.__mem_storage_data[full_path] = result
            
            coroutin_save = self.__save_data_to_disk(folder,arg_string, hash_string, result)

            self.job = await self.scheduler.spawn(coroutin_save)

          return result
      return wrapper
    return wrap_function

#предварительно очищаем кэш
# if os.path.isfile('cache\\my.db'):
#   os.remove('cache\\my.db')
# for file in os.listdir('cache\\example'):
#   os.remove('cache\\example\\'+file)

cache_stor = my_persistent_cache(db_file='cache\\my.db',is_debug_log=True)

@cache_stor.async_cache(folder='cache\\example')
async def example(param1:str,param2:str = False,param3:str = False):
  print(f'nested {param1=},{param2=},{param3=}')
  sleep = random.choice([1,2,3])
  print(f'start sleep - {sleep}')
  await asyncio.sleep(sleep)
  return f'{param1=},{param2=},{param3=}'

async def main():
  tasks = [
      example('param1',param3=True, param2=False),
      example('param1',param3=True, param2=False),
      example('param2',param3=True, param2=False),
      example('param3',param3=True, param2=False),
      example('param1',param3=True, param2=False),
      example('param1',param3=True, param2=False),
      example('param1',param3=True, param2=False),
      example('param2',param3=True, param2=False),
      example('param3',param3=True, param2=False),
      example('param1',param3=True, param2=False),
  ]

  resluts = await asyncio.gather(*tasks)

  await cache_stor.join()

  print('all done ')

if __name__ == '__main__':
  asyncio.run(main())
