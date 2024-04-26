
import time
import functools

class MyDec:
  
  def __init__(self,param1:str=''):
    print(f'__init__ {param1=}')
    self.param1 = param1

  def __call__(self,f):
    print(f'_call__ {self.param1=}')
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        print(f'wrapper {self.param1=}')
        return self.decorator(f, *args, **kwargs)
    return wrapper

  def decorator(self, f, *args, **kwargs):
    print('start decorator')
    time.sleep(1)
    f()
    print('end decorator')

@MyDec(param1='param1')
def example():
  print('example')

@MyDec(param1='param2')
def example1():
  print('example1')

def main():
  example()
  example()
  example()
  example1()
  example1()

main()