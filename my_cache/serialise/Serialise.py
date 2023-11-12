import pickle
import json
import hashlib
from abc import ABC,abstractmethod
class Serialise(ABC):
  #@abstractmethod
  def encode(self,*args,**kwargs)->tuple[str,str]:
    raise(NotImplementedError())
    return None,None


class SerialiseJson(Serialise):
  def encode(self,*args,**kwargs)->tuple[str,str]:    
    all_args = {'args':args,'kwargs':kwargs,}
    arg_string = json.dumps(all_args, sort_keys=True)
    arg_string_e = arg_string.encode()
    hash_string = hashlib.sha256(arg_string_e).hexdigest()
    return arg_string,hash_string

class SerialiseBin(Serialise):
  def encode(self,*args,**kwargs)->tuple[str,str]:    
    '''
    функция создает хэш из параметров, возвращает str аргументов и хеш
    '''
    all_args = [args,kwargs]
    serialized_data = pickle.dumps(all_args,)
    hash_string = hashlib.sha256(serialized_data).hexdigest()
    arg_string = ''    
    return arg_string, hash_string