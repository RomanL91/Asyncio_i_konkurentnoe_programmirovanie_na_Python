# 6.5 Разделяемые данные и блокировки
# 
# В главе 1 мы говорили о том, что каждый процесс имеет собственную
# память, изолированную от памяти других процессов. Спрашивается,
# что делать, если нужно организовать общую память для хранения
# разделяемой несколькими процессами информации о состоянии?
# Библиотека multiprocessing поддерживает так называемые объекты
# разделяемой памяти. Это блок памяти, выделенный так, что к нему
# могут обращаться разные процессы.

# ==================================================================

from multiprocessing import Process, Value, Array


def increment_value(shared_int: Value): # type: ignore
    shared_int.value = shared_int.value + 1


def increment_array(shared_array: Array): # type: ignore
    for index, integer in enumerate(shared_array):
        shared_array[index] = integer + 1


# if __name__ == '__main__':
#     integer = Value('i', 0)
#     integer_array = Array('i', [0, 0])

#     procs = [Process(target=increment_value, args=(integer,)),
#     Process(target=increment_array, args=(integer_array,))]

#     [p.start() for p in procs]
#     [p.join() for p in procs]
    
#     print(integer.value)
#     print(integer_array[:])

# ==================================================================
# ==================================================================
# Пример гонки
        
def increment_value(shared_int: Value): # type: ignore
    shared_int.value = shared_int.value + 1


# if __name__ == '__main__':
#     for _ in range(100):
#         integer = Value('i', 0)
#         procs = [Process(target=increment_value, args=(integer,)),
#                 Process(target=increment_value, args=(integer,))]

#         [p.start() for p in procs]
#         [p.join() for p in procs]

#         print(integer.value)
#         assert(integer.value == 2)


# 1
# Traceback (most recent call last):
#   File "/////////part_6_5.py", line 69, in <module>
#     assert(integer.value == 2)
# AssertionError
# ==================================================================
# ==================================================================

# Избежать гонки можно, синхронизировав доступ к тем разделяемым
# данным, которые мы собираемся модифицировать. Что под этим понимается? 
# Это значит, что мы управляем доступом к разделяемым
# данным таким образом, чтобы все операции финишировали в осмысленном порядке. 
# Если возможна ничья между какими-то двумя операциями, то мы явно блокируем 
# вторую до завершения первой, гарантируя тем самым, что операции финишируют так, как нужно.

# Один из механизмов для синхронизации доступа к разделяемым
# данным называется блокировкой, или мьютексом (от mutual exclusion –
# взаимное исключение). Он позволяет одному процессу заблокировать
# участок кода, т. е. запретить всем остальным его выполнение. Заблокированный 
# участок обычно называют критической секцией. Если один
# процесс выполняет код в критической секции, а второй пытаемся выполнить 
# тот же код, то второму придется подождать (арбитр не пускает его), 
# пока первый закончит работу и выйдет из критической секции.

# Блокировки поддерживают две основные операции: захват и освобождение. 
# Гарантируется, что процесс, захвативший блокировку, –
# единственный, кто может выполнять код в критической секции. Закончив 
# выполнение кода, требующего синхронизации доступа, мы
# освобождаем блокировку. Это дает возможность другим процессам
# захватить блокировку и выполнить код в критической секции. Если
# процесс попытается выполнить код в секции, заблокированной другим процессом, 
# то будет приостановлен, пока этот другой процесс не освободит блокировку.


# Попытка Процесса 2 прочитать разделяемые данные блокируется, пока
# Процесс 1 не освободит блокировку
    
# При выполнении этой программы мы всегда будем получать значение 2. 
# Гонка устранена! Заметим, что блокировки являются контекстными менеджерами, 
# и, чтобы сделать код чище, мы могли быиспользовать в функции increment_value 
# блок with. Тогда захвати осво­бождение блокировки будут производиться автоматически:
    
def increment_value(shared_int: Value): # type: ignore
    # shared_int.get_lock().acquire()
    # shared_int.value = shared_int.value + 1
    # shared_int.get_lock().release()
    with shared_int.get_lock():
        shared_int.value = shared_int.value + 1 


# if __name__ == '__main__':
#     for _ in range(100):
#         integer = Value('i', 0)
#         procs = [Process(target=increment_value, args=(integer,)),
#                 Process(target=increment_value, args=(integer,))]

#     [p.start() for p in procs]
#     [p.join() for p in procs]

#     print(integer.value)
#     assert (integer.value == 2)

# Обратите внимание, что мы принудительно преобразовали конкурентный код в 
# последовательный, сведя на нет преимущества распараллеливания. 
# Это важное наблюдение, поскольку проливает свет на недостаток 
# синхронизации и разделяемые данные вообще. Чтобы избежать гонки, код в 
# критических секциях обязан выполняться последовательно. 
# Это может отрицательно сказаться на производительности многопроцессного кода. 
# Поэтому нужно внимательно следить за тем, чтобы защищать блокировкой только то, 
# что абсолютно необходимо, и не мешать остальному коду выполняться конкурентно.
# Столкнувшись с состоянием гонки, не нужно идти по легкому пути
# и защищать блокировкой все вообще. Проблему-то вы решите, но,
# скорее всего, производительность сильно пострадает.

# ==================================================================
# ==================================================================

# 6.5.3 Разделение данных в пулах процессов
    
# Только что мы видели, как разделить данные между двумя процессами, 
# а как применить эти знания к пулу процессов? Процессы в пуле
# мы не создаем вручную, что вызывает проблемы при разделении данных.

# Чтобы решить проблему, мы должны поместить разделяемый
# счетчик в глобальную переменную и каким-то образом дать знать об
# этом процессам-исполнителям. Для этого предназначены инициализаторы 
# пула процессов – специальные функции, которые вызываются
# в момент запуска каждого процесса в пуле. С их помощью мы можем
# создать ссылку на разделяемую память, выделенную родительским
# процессом. Инициализатор можно передать пулу процессов в момент
# его создания. Продемонстрируем это на простом примере инкрементирования счетчика.


from concurrent.futures import ProcessPoolExecutor
import asyncio
from multiprocessing import Value


shared_counter: Value # type: ignore


def init(counter: Value): # type: ignore
    global shared_counter
    shared_counter = counter


def increment():
    with shared_counter.get_lock():
        shared_counter.value += 1


async def main():
    counter = Value('d', 0)
    with ProcessPoolExecutor(initializer=init, initargs=(counter,)) as pool:
        await asyncio.get_running_loop().run_in_executor(pool, increment)
        print(counter.value)


# if __name__ == "__main__":
#     asyncio.run(main())

# ==================================================================
# ==================================================================

from concurrent.futures import ProcessPoolExecutor
import functools
import asyncio
from multiprocessing import Value
from typing import List, Dict
from part_6_4 import partition, merge_dictionaries


map_progress: Value # type: ignore


def init(progress: Value): # type: ignore
    global map_progress
    map_progress = progress


def map_frequencies(chunk: List[str]) -> Dict[str, int]:
    counter = {}
    for line in chunk:
        word, _, count, _ = line.split('\t')
        if counter.get(word):
            counter[word] = counter[word] + int(count)
        else:
            counter[word] = int(count)

    with map_progress.get_lock():
        map_progress.value += 1
    
    return counter


async def progress_reporter(total_partitions: int):
    while map_progress.value < total_partitions:
        print(f'Завершено операций отображения: {map_progress.value}/{total_partitions}')

        await asyncio.sleep(1)


async def main(partiton_size: int):
    global map_progress

    with open('googlebooks-eng-all-1gram-20120701-a', encoding='utf-8') as f:
        contents = f.readlines()
        loop = asyncio.get_running_loop()
        tasks = []
        map_progress = Value('i', 0)

        with ProcessPoolExecutor(initializer=init, initargs=(map_progress,)) as pool:
            total_partitions = len(contents) // partiton_size
            reporter = asyncio.create_task(progress_reporter(total_partitions))

            for chunk in partition(contents, partiton_size):
                tasks.append(loop.run_in_executor(pool, functools.partial(map_frequencies, chunk)))

        counters = await asyncio.gather(*tasks)
        await reporter
        final_result = functools.reduce(merge_dictionaries, counters)
        print(f"Aardvark встречается {final_result['Aardvark']} раз.")

# if __name__ == "__main__":
#     asyncio.run(main(partiton_size=60000))



# далее к изучению:
# 6.6Несколько процессов и несколько циклов событий
