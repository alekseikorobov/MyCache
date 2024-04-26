import asyncio
from functools import wraps
from asyncio.queues import Queue

def async_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Создаем очередь
        queue = Queue()
        
        # Асинхронная функция для получения элементов из очереди
        async def process_queue():
            print('start process_queue')
            while True:
                print('await')
                item = await queue.get()
                print('get from queue')
                # Обрабатываем полученный элемент
        print('start')
        # Запускаем функцию для получения элементов из очереди в отдельном потоке
        asyncio.create_task(process_queue())

        # Вызываем асинхронную функцию
        result = await func(queue, *args, **kwargs)
        
        # Возвращаем результат
        return result

    return wrapper

# Пример использования декоратора
@async_decorator
async def my_async_function(queue, *args, **kwargs):
    # Позднее добавляем элементы в очередь
    await queue.put('item1')
    await queue.put('item2')

    # Делаем что-то еще
    # ...

    # Ожидаем окончания обработки всех элементов
    await queue.join()

    # Возвращаем результат
    return 'success'


# Запускаем пример
async def main():
    result = await my_async_function()
    print(result)

# запуск цикла событий asyncio
asyncio.run(main())