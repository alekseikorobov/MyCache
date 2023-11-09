#%%
import hashlib
import json
from enum import Enum
import os

class TypeStorage(Enum):
  IN_MEMORY = 0
  IN_DISK = 1

class my_cache:

  def __init__(self, type_storage=TypeStorage.IN_MEMORY,db_file = None, is_debug_log=False):
    self.type_storage = type_storage
    self.db_file = db_file
    self.is_debug_log = is_debug_log
    self.__mem_storage = {}

    all_func_for_storage = {
      TypeStorage.IN_DISK:self.__get_or_run_with_store_disk,
      TypeStorage.IN_MEMORY:self.__get_or_run_with_store_memory,
    }

    self.__func_storage = all_func_for_storage[self.type_storage]

    if self.type_storage == TypeStorage.IN_DISK:
      if self.db_file is None or self.db_file == '':
        raise(Exception('if type TypeStorage.IN_DISK then db_file is cannot be empty!'))
      if os.path.isfile(self.db_file):
        if self.is_debug_log: print(f'read from {self.db_file}')
        with open(self.db_file,'r',encoding='UTF-8') as f:
          for line in f.readlines():
            line = line.rstrip('\n')
            sep = line.find('\t')
            full_path = line[0:sep]
            arg_string = line[sep+1:]
            if self.is_debug_log: print(f'{arg_string=}')
            self.__mem_storage[full_path] = arg_string
        if self.is_debug_log: print(f'not keys {len(self.__mem_storage)}')
      else:
        if not os.path.isdir(os.path.dirname(self.db_file)):
          os.makedirs(os.path.dirname(self.db_file))

  def __generate_hash(self,*args,**kwargs):
    all_args = {
      'args':args,
      'kwargs':kwargs,
    }
    arg_string = json.dumps(all_args, sort_keys=True)
    arg_string_e = arg_string.encode()
    hash_string = hashlib.sha256(arg_string_e).hexdigest()
    return arg_string,hash_string
  
  def __get_or_run_with_store_disk(self, folder, hash_string, arg_string, func,*args,**kwargs):
    full_path = os.path.join(folder, hash_string)
    if full_path in self.__mem_storage:
      if not os.path.isfile(full_path):
        raise(Exception(f'not found file by path {full_path}'))
      result = None
      with open(full_path,'r',encoding='UTF-8') as f:
        result = f.read()
      if self.is_debug_log: print(f'read from cache {full_path}')
      return result
    else:
      result = func(*args,**kwargs)
      self.__mem_storage[full_path] = arg_string
      if self.is_debug_log: print(f'save to {full_path}')
      
      if not os.path.isdir(os.path.dirname(full_path)):
         os.makedirs(os.path.dirname(full_path))

      with open(full_path,'w',encoding='UTF-8') as f:
        f.write(result)
      if self.is_debug_log: print(f'update {self.db_file}')
      with open(self.db_file,'a',encoding='UTF-8') as f:
        f.write(f'{full_path}\t{arg_string}\n')
      return result

  def __get_or_run_with_store_memory(self,folder, hash_string, arg_string,func,*args,**kwargs):
    if hash_string in self.__mem_storage:
      return self.__mem_storage[hash_string]
    else:
      result = func(*args,**kwargs)
      self.__mem_storage[hash_string] = result
      return result

  def cache(self,folder):
    def wrap_function(func):
      def wrapper(*args,**kwargs):
        arg_string, hash_string = self.__generate_hash(*args,**kwargs)
        if self.is_debug_log: print(self.type_storage)
        return self.__func_storage(folder, hash_string, arg_string,func,*args,**kwargs)
      return wrapper
    return wrap_function

if __name__ == '__main__':
  cache_stor = my_cache(db_file='cache\\my.db',type_storage=TypeStorage.IN_DISK)

  @cache_stor.cache(folder='cache\\example')
  def example(param1:str,param2:str = False,param3:str = False):
    print(f'{param1=},{param2=},{param3=}')
    return f'{param1=},{param2=},{param3=}'

  example('param1',param3=True, param2=False)
