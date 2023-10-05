# Измерение времени выполнения сопрограммы с по­мощью декораторов.

    # Листинг 2.16 Декоратор для хронометража сопрограмм

import asyncio
import functools
import time
from typing import Callable, Any


def async_timed():
    def wrapper(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            print(f'выполняется {func} с аргументами {args} {kwargs}')
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                end = time.time()
                total = end - start
                print(f'{func} завершилась за {total:.4f} с')
        return wrapped
    return wrapper


@async_timed()
async def delay(delay_seconds: int) -> int:
    print(f'засыпаю на {delay_seconds} с')
    await asyncio.sleep(delay_seconds)
    print(f'сон в течение {delay_seconds} с закончился')
    return delay_seconds


@async_timed()
async def main():
    task_one = asyncio.create_task(delay(2))
    task_two = asyncio.create_task(delay(3))
    await task_one
    await task_two


asyncio.run(main())


# Как видим, два вызова delay работали примерно 2 и 3 с соответственно, что в 
# сумме составляет 5 с. Заметим, однако, что сопрограмма main работала всего 3 с, 
# поскольку ожидание производилось конкурентно.


# к разбору далее
# 2.7
# Ловушки сопрограмм и задач
