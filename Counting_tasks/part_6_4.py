# 6.4 Решение задачи с по­мощью MapReduce и asyncio

# В модели программирования MapReduce большой набор данных
# сначала разбивается на меньшие части. Затем мы можем решить задачу для 
# поднабора данных, а не для всего набора – это называется
# отображением (mapping), поскольку мы «отображаем» данные на частичный результат.
# После того как задачи для всех поднаборов решены, мы можем
# объединить результаты в окончательный ответ. Этот шаг называется 
# редукцией (reducing), потому что «редуцируем» (сводим) несколько ответов в один.

# ==================================================================
import functools
from typing import Dict


def map_frequency(text: str) -> Dict[str, int]:
    words = text.split(' ')
    frequencies = {}

    for word in words:
        if word in frequencies:
            frequencies[word] = frequencies[word] + 1
        else:
            frequencies[word] = 1
    return frequencies


def merge_dictionaries(
    first: Dict[str, int], second: Dict[str, int]
) -> Dict[str, int]:
    merged = first
    for key in second:
        if key in merged:
            merged[key] = merged[key] + second[key]
        else:
            merged[key] = second[key]
    return merged


if __name__ == "__main__":

    lines = [
        "I know what I know",
        "I know that I know",
        "I don't know much",
        "They don't know much"
    ]

    mapped_results = [map_frequency(line) for line in lines]
    
    for result in mapped_results:
        print(result)
        # {'I': 2, 'know': 2, 'what': 1}
        # {'I': 2, 'know': 2, 'that': 1}
        # {'I': 1, "don't": 1, 'know': 1, 'much': 1}
        # {'They': 1, "don't": 1, 'know': 1, 'much': 1}

    print(functools.reduce(merge_dictionaries, mapped_results))
    # {'I': 5, 'know': 6, 'what': 1, 'that': 1, "don't": 2, 'much': 2, 'They': 1}

# Разобравшись с основами технологии MapReduce на модельной задаче, 
# посмотрим, как применить ее к реальному набору данных, для
# которого библиотека multiprocessing может дать выигрыш в производительности.
# ==================================================================
# ==================================================================
# 6.4.2 Набор данных Google Books Ngram
# https://storage.googleapis.com/books/ngrams/books/googlebooks-eng-all-1gram-20120701-a.gz

# Нам нужен достаточно большой набор данных, чтобы продемонстрировать 
# все преимущества сочетания MapReduce с библиотекой multiprocessing. 
# Если набор данных слишком мал, то мы, скорее всего,
# увидим не преимущества, а падение производительности из-за накладных 
# расходов на управление процессами.
# Набор данных Google Books Ngram достаточен для наших целей.
# Чтобы понять, что это такое, сначала определим понятие n-граммы.
# n-граммой называется последовательность N слов заданного текста. 
# Во фразе «the fast dog» есть шесть n-грамм. Три 1-граммы, или
# униграммы, содержащие по одному слову (the, fast и dog), две 2-граммы, 
# или диграммы (the fast и fast dog), и одна 3-грамма, или триграмма (the fast dog).
# Набор данных Google Books Ngram состоит из n-грамм, взятых из
# 8 000 000 книг, начиная с 1500 года. Это более шести процентов от
# всех изданных в мире книг. Подсчитано, сколько раз каждая уникальная 
# n-грамма встречается в текстах, и результаты сгруппированы по
# годам. В этом наборе данных присутствуют n-граммы для n от 1 до 5,
# представленные в формате с табуляторами. Каждая строка набора
# содержит n-грамму, год ее появления, сколько раз она встречалась
# и в скольких книгах. Рассмотрим первые несколько строк набора униграмм 
# для слова aardvark:
# Aardvark 1822 2 1
# Aardvark 1824 3 1
# Aardvark 1827 10 7
# Это означает, что в 1822 году слово aardvark (трубкозуб) дважды
# встретилось в одной книге. А в 1827 году оно встретилось десять раз
# в семи книгах. В наборе данных есть гораздо больше строк для слова
# aardvark (например, в 2007 году оно встретилось 1200 раз), что доказывает 
# все более частое упоминание трубкозубов в литературе с течением времени.
# ==================================================================
# ==================================================================
# синхронный вариант
import time

def go():
    freqs = {}

    with open('Counting_tasks/googlebooks-eng-all-1gram-20120701-a', encoding='utf-8') as f:
        lines = f.readlines()
        start = time.time()

        for line in lines:
            data = line.split('\t')
            word = data[0]
            count = int(data[2])
            if word in freqs:
                freqs[word] = freqs[word] + count
            else:
                freqs[word] = count
        
        end = time.time()

        print(f'{end-start:.4f}')

# if __name__ == "__main__":
#     go()
    # 43.9746 на моем ПК
# ==================================================================
# Распараллеливание с по­мощью MapReduce и пула процессов
import asyncio
import concurrent.futures
import functools
import time
from typing import Dict, List


def partition(data: List, chunk_size: int):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def map_frequencies(chunk: List[str]) -> Dict[str, int]:
    counter = {}
    for line in chunk:
        word, _, count, _ = line.split('\t')
        if counter.get(word):
            counter[word] = counter[word] + int(count)
        else:
            counter[word] = int(count)
    return counter


def merge_dictionaries(first: Dict[str, int], second: Dict[str, int]) -> Dict[str, int]:
    merged = first
    for key in second:
        if key in merged:
            merged[key] = merged[key] + second[key]
        else:
            merged[key] = second[key]
    return merged


async def main(partition_size: int):
    with open('Counting_tasks/googlebooks-eng-all-1gram-20120701-a', encoding='utf-8') as f:
        contents = f.readlines()
        loop = asyncio.get_running_loop()
        tasks = []
        start = time.time()

        with concurrent.futures.ProcessPoolExecutor() as pool:
            for chunk in partition(contents, partition_size):
                tasks.append(loop.run_in_executor(pool, functools.partial(map_frequencies, chunk)))
            print('Задачи созданы')
            intermediate_results = await asyncio.gather(*tasks)
            final_result = functools.reduce(merge_dictionaries, intermediate_results)

            print(f"Aardvark встречается {final_result['Aardvark']} раз.")
            end = time.time()
            print(f'Время MapReduce: {(end - start):.4f} секунд')


if __name__ == "__main__":
    asyncio.run(main(partition_size=4))
                     
# Остается только один вопрос: как выбрать размер порции?
# Простого ответа на этот вопрос не существует. Есть эвристическое
# правило – сбалансированный подход1: порция не должна быть ни
# слишком большой, ни слишком маленькой. Маленькой она не должна
# быть потому, что созданные порции сериализуются (в формате pickle)
# и раздаются исполнителям, после чего исполнители десериализуют
# их. Процедура сериализации и десериализации может занимать много 
# времени, сводя на нет весь выигрыш, если производится слишком
# часто. Например, размер порции, равный 2, – заведомо неудачное решение, 
# потому что потребовалось бы почти 1 000 000 операций сериализации и десериализации.
# Но и слишком большая порция – тоже плохо, поскольку это не даст
# нам в полной мере задействовать возможности компьютера. 
# Например, если имеется 10 ядер, но всего две порции, то мы ничем не загружаем 
# восемь ядер, которые могли бы работать параллельно.


# далее к изучению:
# 6.5 Разделяемые данные и блокировки
