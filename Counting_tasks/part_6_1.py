# 6.1 Введение в библиотеку multiprocessing
# 
# В главе 1 мы познакомились с глобальной блокировкой интерпретатора. 
# Она препятствует параллельному выполнению нескольких
# участков байт-кода. Это означает, что для любых задач, кроме вводавывода 
# и еще нескольких мелких исключений, многопоточность не
# дает никакого выигрыша в производительности, – в отличие от таких
# языков, как Java и C++. Кажется, что мы уперлись в тупик, и для распараллеливания 
# счетных задач Python не предлагает никакого решения, 
# но на самом деле решение есть – библиотека multiprocessing.
# Вместо запуска потоков для распараллеливания работы родительский 
# процесс будет запускать дочерние процессы. В каждом дочернем 
# процессе работает отдельный интерпретатор Python со своей GIL.
# В предположении, что код выполняется на машине с несколькими
# процессорными ядрами, это означает, что можно эффективно распараллелить 
# счетные задачи. И даже если процессов больше, чем ядер,
# механизм вытесняющей многозадачности, встроенный в операционную 
# систему, позволит выполнять задачи конкурентно. Такая конфигурация 
# является конкурентной и параллельной.


import time

from multiprocessing import Process, Pool

from concurrent.futures import ProcessPoolExecutor


# ===============================================================================
# Листинг 6.1 Два параллельных процесса

def count(count_to: int) -> int:
    start = time.time()
    counter = 0
    while counter < count_to:
        counter = counter + 1
    end = time.time()
    print(f'Закончен подсчет до {count_to} за время {end-start}')
    return counter


# if __name__ == "__main__":
#     start_time = time.time()

#     to_one_hundred_million = Process(target=count, args=(100000000,))
#     to_two_hundred_million = Process(target=count, args=(200000000,))

#     to_one_hundred_million.start()
#     to_two_hundred_million.start()

#     to_one_hundred_million.join()
#     to_two_hundred_million.join()
    
#     end_time = time.time()
    
#     print(f'Полное время работы {end_time-start_time}')
# ===============================================================================
# ===============================================================================
# 6.2 Использование пулов процессов

# Пул процессов напоминает пул подключений, который мы видели
# в главе 5. Разница в том, что мы создаем не набор подключений к базе
# данных, а набор Python-процессов, который можно использовать для
# параллельного выполнения функций. Если в процессе требуется выполнить 
# какую-то счетную функцию, то мы просим пул потоков посодействовать. 
# За кулисами он выполняет функцию в доступном процессе и возвращает ее значение.


def say_hello(name: str) -> str:
    return f'Привет, {name}'


# if __name__ == "__main__":
#     with Pool() as process_pool:
#         hi_jeff = process_pool.apply(say_hello, args=('Jeff',))
#         hi_john = process_pool.apply(say_hello, args=('John',))
#         print(hi_jeff)
#         print(hi_john)


# Работать-то работает, но есть проблема. Метод apply блокирует выполнение, 
# пока функция не завершится. Это значит, что если бы каждое обращение 
# к say_hello занимало 10 с, то программа работала бы
# примерно 20 с, потому что выполнение последовательное и все усилия 
# сделать ее параллельной пошли насмарку. Эту проблему можно
# решить, воспользовавшись методом пула процессов apply_async.
# ===============================================================================
# ===============================================================================
# 6.2.1 Асинхронное получение результатов
        

def say_hello(name: str) -> str:
    return f'Привет, {name}'


# if __name__ == "__main__":
#     with Pool() as process_pool:
#         hi_jeff = process_pool.apply_async(say_hello, args=('Jeff',))
#         hi_john = process_pool.apply_async(say_hello, args=('John',))
#         print(hi_jeff.get())
#         print(hi_john.get())


# В случае использования apply_async оба вызова say_hello начинают 
# работать в отдельных процессах. Затем, когда мы вызываем метод
# get, родительский процесс блокируется, пока каждый дочерний не
# вернет значение. Конкурентное выполнение мы обеспечили, но что,
# если hi_jeff занимает 10 с, а hi_john только одну? В таком случае, 
# поскольку мы вызвали метод get объекта hi_jeff первым, программа
# зависнет на 10 с, прежде чем напечатать приветствие Джону, хотя готово 
# оно было уже через 1 с. Если мы хотим реагировать сразу после
# получения результата, то следует признать, что проблема осталась. На
# самом деле нам нужно что-то типа функции as_completed из библиотеки asyncio. 
# Далее мы увидим, как использовать исполнителей пула
# процессов в сочетании с asyncio, чтобы решить эту проблему.
# ===============================================================================
# ===============================================================================
# 6.3 Использование исполнителей пула процессов в сочетании с asyncio    

# Мы видели, как использовать пулы процессов для конкурентного выполнения 
# счетных операций. Такие пулы хороши для простых случаев, 
# но Python предлагает абстракцию поверх пула процессов в модуле
# concurrent.futures. Это модуль содержит исполнители для процессов 
# и потоков, которые можно использовать как самостоятельно, так
# и в сочетании с asyncio. Начнем с рассмотрения основ класса Process-
# PoolExecutor, похожего на ProcessPool. Затем посмотрим, как связать
# его с asyncio, чтобы можно было использовать всю мощь функций API,
# в частности gather.


def count(count_to: int) -> int:
    start = time.time()
    counter = 0
    while counter < count_to:
        counter = counter + 1
    end = time.time()
    print(f'Закончен подсчет до {count_to} за время {end - start}')
    return counter


# if __name__ == "__main__":
#     with ProcessPoolExecutor() as process_pool:
#         numbers = [1, 3, 5, 22, 100000000]
#         for result in process_pool.map(count, numbers):
#             print(result)


# Закончен подсчет до 1 за время 9.5367431640625e-07
# Закончен подсчет до 3 за время 9.5367431640625e-07
# Закончен подсчет до 5 за время 9.5367431640625e-07
# Закончен подсчет до 22 за время 1.6689300537109375e-06
# 1
# 3
# 5
# 22
# Закончен подсчет до 100000000 за время 3.771929979324341
# 100000000
            
# Хотя кажется, что программа работает так же, как asyncio.as_completed, 
# на самом деле порядок итераций детерминирован и определяется тем, 
# в каком порядке следуют числа в списке numbers. Это значит,
# что если бы первым числом было 100000000, то пришлось бы ждать
# завершения соответствующего вызова, и только потом появилась бы
# возможность напечатать другие результаты, хотя они и были вычислены 
# раньше. То есть эта техника не такая отзывчивая, как функция asyncio.as_completed.
# ===============================================================================
# ===============================================================================
# 6.3.2 Исполнители пула процессов в сочетании с циклом событий

# Познакомившись с тем, как работают исполнители пула процессов,
# посмотрим, как включить их в цикл событий asyncio. Это позволит
# нам использовать такие рассмотренные в главе 4 функции API, как
# gather и as_completed, для управления несколькими процессами.

# Исполнитель пула процессов для работы с asyncio создается так же,
# как было описано выше, т. е. в контекстном менеджере. Имея пул, мы
# можем использовать специальный метод цикла событий asyncio –
# run_in_executor. Этот метод принимает выполняемый объект и исполнитель 
# (пула процессов или пула потоков), после чего исполняет
# этот объект внутри пула и возвращает допускающий ожидание объект, 
# который можно использовать в предложении await или передать
# какой-нибудь функции API, например gather.
# Давайте еще раз реализуем предыдущий пример, теперь с исполнителем 
# пула процессов. Мы подадим исполнителю несколько задач
# подсчета и будем ждать их завершения с по­мощью gather. Метод run_in_executor 
# принимает только вызываемый объект и не позволяет
# задать аргументы функции. Эту трудность мы обойдем, воспользовавшись 
# частичным применением функции, чтобы сконструировать
# обращения к count, не нуждающиеся в аргументах.
# Что такое частичное применение функции?
# Механизм частичного применения функции реализован в модуле functools. 
# Идея в том, чтобы взять функцию, принимающую некоторые аргументы, 
# и преобразовать ее в другую функцию, принимающую меньше аргументов. 
# Некоторые аргументы при этом «замораживаются». Например,
# наша функция count принимает один аргумент. Мы можем преобразовать
# ее в функцию без аргументов, воспользовавшись функцией functools.
# partial и указав в качестве ее аргумента то значение, с которым мы
# хотим вызвать count. Если требуется вызвать count(42), но при этом не
# передавать никаких аргументов, то можно определить call_with_42 =
# functools.partial(count, 42), а затем просто вызвать call_with_42().


import asyncio
from asyncio.events import AbstractEventLoop
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import List


def count(count_to: int) -> int:
    counter = 0
    while counter < count_to:
        counter = counter + 1
    return counter


# Вариант запуска через gather
# и будем ожидать пока самая долгая счетная задача завершится
# получим детерминированный результат
async def main_gather():
    with ProcessPoolExecutor() as process_pool:
        loop: AbstractEventLoop = asyncio.get_running_loop()
        nums = [1000, 1, 3, 5, 22, 100000000]
        calls: List[partial[int]] = [partial(count, num) for num in nums]
        call_coros = []

        for call in calls:
            call_coros.append(loop.run_in_executor(process_pool, call))

        results = await asyncio.gather(*call_coros)

        for result in results:
            print(result)


# Вариант запуска через as_completed
# результат не детерминированный, зато предоставляется
# по мере готовности
async def main_as_completed():
    with ProcessPoolExecutor() as process_pool:
        loop: AbstractEventLoop = asyncio.get_running_loop()
        nums = [1000000, 1, 3, 5, 22, 100000000]
        calls: List[partial[int]] = [partial(count, num) for num in nums]
        call_coros = []

        for call in calls:
            call_coros.append(loop.run_in_executor(process_pool, call))


        for finished_task in asyncio.as_completed(call_coros):
            print(await finished_task)



if __name__ == "__main__":
    asyncio.run(main_as_completed())
# ===============================================================================

# Далее к изучению 
# 6.4 Решение задачи с по­мощью MapReduce и asyncio