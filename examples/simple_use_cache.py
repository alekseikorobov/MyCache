
# for work need install pip install -e .
from my_cache import CacheStor, TypeStorage

import os

cache_stor = CacheStor(db_file='cache/my.db',type_storage=TypeStorage.IN_DISK)

@cache_stor.cache(folder='cache/example')
def example(param1:str,param2:str = False,param3:str = False):
  print(f'{param1=},{param2=},{param3=}')
  return f'result - {param1=},{param2=},{param3=}'

result = example('param2',param3=True, param2=False)
print(result)