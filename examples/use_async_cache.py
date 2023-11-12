import asyncio
import random
from my_cache import my_persistent_cache
#предварительно очищаем кэш
# if os.path.isfile('cache/my.db'):
#   os.remove('cache/my.db')
# for file in os.listdir('cache/example'):
#   os.remove('cache/example/'+file)

cache_stor = my_persistent_cache(db_file='cache/my.db',is_debug_log=True)

@cache_stor.async_cache(folder='cache/example')
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
  ]

  resluts = await asyncio.gather(*tasks)

  # после завершения основного цикла, ожидаем когда завершится
  # цикл кеша, чтобы успел всё записать на диск прежде чем выйти из программы 
  await cache_stor.join()

  print('all done ')

if __name__ == '__main__':
  asyncio.run(main())