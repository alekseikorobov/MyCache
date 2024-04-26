# MyCache
Декоратор для автоматического кеширования данных

### Установка
```sh
pip install -e git+https://github.com/alekseikorobov/MyCache.git
```

### Пример использования:
```python
from my_cache import CacheStor, TypeStorage

cache_stor = CacheStor(db_file='cache/my.db',type_storage=TypeStorage.IN_DISK)

@cache_stor.cache(folder='cache/example')
def example(param1:str,param2:str = False,param3:str = False):
  print(f'{param1=},{param2=},{param3=}')
  return f'result - {param1=},{param2=},{param3=}'

result = example('param2',param3=True, param2=False)
print(result)
```
в этом примере создается переменная ``cache_stor`` типа ``CacheStor``, допускаются следующие аргументы:
* ``db_file:str`` - общая база для хранения всего списка кешированных данных, необходима для того чтобы не делать проверку каждый раз существует ли файл на диске или нет. 
* ``type_storage:Enum`` - поддерживается два типа:
  * TypeStorage.IN_MEMORY - хранение данных только в памяти
  * TypeStorage.IN_DISK - хранение данных на диске
* ``is_debug_log:bool`` - вывод дебаг лога
* ``serialiser:Serialise`` - тип сереализация параметров метода. Сереализатор должен возвращать уникальный хеш для параметров. Поддерживает любые типы данных параметров. Должен наследоваться от типа ``Serialise``, реализованы следующие сереализации:
    * SerialiseBin - бинарная сереализация с использованием pickle - **используется по умолчанию**
    * SerialiseJson - json сереализация, удобно использовать, если потом по db_file нужно определить по каким параметрам записан кеш

переменная cache_stor, должна быть singleton по отношению ко всей программе

Далее на функцию ``example`` навешивается декоратор ``@cache_stor.cache`` который предварительно вызывается с параметром:
* ``folder:str`` - путь для хранения закешированных данных результата метода. После того как метод отработает, при вызове повторно этот метод, данные будут взяты из кеша. Время жизни кеша не предусмотрено.



Пример асинхронного кеширования:
```python
import asyncio
from my_cache import CacheStor

cache_stor = CacheStor(db_file='cache/my.db')

@cache_stor.cache_async(folder='cache/example')
async def example(param1:str,param2:str = False,param3:str = False):
  print(f'nested {param1=},{param2=},{param3=}')    
  await asyncio.sleep(1)
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

```

декоратор ``@cache_stor.cache_async`` записывает данные всегда в файл (не хранит в памяти)
Запись в файл происходит в отедельном потоке не зависимом от основного.
Можно использовать только для асинхронных методов



