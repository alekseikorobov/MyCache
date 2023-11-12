import hashlib
import json
from enum import Enum
import os
import time
import asyncio
import aiofiles
import aiofiles.os
import random
import aiojobs
import pickle

class my_persistent_cache:

  def __init__(self,db_file = None, is_debug_log=False):
    self.db_file = db_file
    self.is_debug_log = is_debug_log
    
    

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






  def generate_hash(self,*args,**kwargs)->tuple[str,str]:
    '''
    функция создает хэш из параметров, возвращает str аргументов и хеш
    '''
    all_args = [args,kwargs]
    arg_string = json.dumps(all_args, sort_keys=True)
    arg_string_e = arg_string.encode()
    hash_string = hashlib.sha256(arg_string_e).hexdigest()
    return arg_string,hash_string
  



