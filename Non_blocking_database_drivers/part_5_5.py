# Вставка данных в базу.
import asyncio, asyncpg

from typing import List, Tuple, Union

from random import randint, sample

from utils import async_timed

# ==================================================================
# Вставка случайный марок

# Построчно прочитаем файл с 1000 словами
def load_common_words() -> List[str]:
    with open('common_words.txt') as common_words:
        return common_words.readlines()


# Сгенерируем список кортежей из 100 случайный марок (слов из файла)
def generate_brand_names(words: List[str]) -> List[Tuple[Union[str, ]]]:
    return [(words[index].strip(),) for index in sample(range(100), 100)]


async def insert_brands(common_words, connection) -> int:
    brands = generate_brand_names(common_words)
    insert_brands = "INSERT INTO brand VALUES(DEFAULT, $1)"
    return await connection.executemany(insert_brands, brands)

# За кулисами executemany в цикле обходит список марок и генерирует 
# по одной команде INSERT для каждой марки. Затем она выполняет
# сразу все эти команды. Заодно этот метод параметризации предохраняет 
# нас от атак внедрением SQL, поскольку входные данные надлежащим 
# образом экранируются. По завершении мы будем иметь в системе 
# 100 марок со случайными названиями.


async def main():
    common_words = load_common_words()              # читаем файл
    connection = await asyncpg.connect(             # устанавливаем соединение с БД
        host='127.0.0.1',
        port=5432,
        user='postgres',
        database='products',
        password='password'
    )
    await insert_brands(common_words, connection)   # Производим вставку


# if __name__ == "__main__":
#     asyncio.run(main())
# ==================================================================
# ==================================================================
# По аналогии вставим и другие данные в БД.

def gen_products(common_words: List[str], 
                 brand_id_start: int, 
                 brand_id_end: int, 
                 products_to_create: int) -> List[Tuple[str, int]]:
    products = []
    for _ in range(products_to_create):
        description = [common_words[index] for index in sample(range(1000), 10)]
        brand_id = randint(brand_id_start, brand_id_end)
        products.append((" ".join(description), brand_id))
    return products


def gen_skus(product_id_start: int, product_id_end: int, skus_to_create: int) -> List[Tuple[int, int, int]]:
    skus = []
    for _ in range(skus_to_create):
        product_id = randint(product_id_start, product_id_end)
        size_id = randint(1, 3)
        color_id = randint(1, 2)
        skus.append((product_id, size_id, color_id))
    return skus


async def main():
    common_words = load_common_words()
    connection = await asyncpg.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        database='products',
        password='password'
    )
    product_tuples = gen_products(
        common_words,
        brand_id_start=1,
        brand_id_end=100,
        products_to_create=1000
    )
    await connection.executemany(
        "INSERT INTO product VALUES(DEFAULT, $1, $2)",
        product_tuples
    )
    sku_tuples = gen_skus(
        product_id_start=1,
        product_id_end=1000,
        skus_to_create=100000
    )
    await connection.executemany(
        "INSERT INTO sku VALUES(DEFAULT, $1, $2, $3)",
        sku_tuples
    )
    await connection.close()


# if __name__ == "__main__":
#     asyncio.run(main())

# В результате выполнения этой программы мы получим базу данных, 
# содержащую 1000 товаров и 100 000 SKU. Вся процедура может
# занять несколько секунд, точное время зависит от машины. Теперь,
# написав запрос с несколькими соединениями, мы сможем запросить
# все имеющиеся SKU для конкретного товара. Для product id 100 этот
# запрос выглядит так:

product_query = \
    """
    SELECT
    p.product_id,
    p.product_name,
    p.brand_id,
    s.sku_id,
    pc.product_color_name,
    ps.product_size_name
    FROM product as p
    JOIN sku as s on s.product_id = p.product_id
    JOIN product_color as pc on pc.product_color_id = s.product_color_id
    JOIN product_size as ps on ps.product_size_id = s.product_size_id
    WHERE p.product_id = 100"""

# Что если данный запросы (connection.execute(product_query)) - несколько   
# штук поместить в список и применить функцию asyncio.gather, указав одно подключение?
# Получим ошибку, так как не можем использовать одно подключение сразу для нескольких
# запросов. В SQL одному подключению к базе соответствует один сокет.
# Другими словами, нужно сделать несколько соединений, задействовав несколько
# сокетов и раздавать им запросы.
# ==================================================================

# Далее мы будем создавать пул подключений к БД для конкуретного выполнения запросов. 

# ==================================================================
# 5.5.2 Создание пула подключений для конкурентного выполнения запросов
# 
# Немного пояснения.
# Представим что такое пул - это коробка с подключениями. У коробки может
# быть размер и соотвественно подключений она может хранить ограниченного 
# колличество. Представим теперь в виде коробочки с карандашами, где
# коробочка - все тот же пул, а карандаши - подключения к БД.
# Мы сидим рисуем, берем один карандаш, используем его, после как закончили
# с ним возращаем его в коробочку, берем другой, используем его и так далее.
# Думаю пример с карандашами довольно хорошо описывает суть. 
# Это пример все же синхронного использования пула подключений.
# Для бельшей наглядности представляем дальше, что в нашей коробке всего два
# карандаша, а нас (художников) за столом сидят трое. Первый берет
# карандаш - рисует, воторой берет карандаш (последний) - рисует, но а что
# там с третим - ему то придется подождать. Из этого примера художники
# как бы сопрограммы, которые взяли подключения, проделывают свои операции 
# с БД, затем вернут подключения в пул, где другие сопрограммы возьмут 
# их для своего использования.
# 
# Пулы asyncpg являются асинхронными контекстными менеджерами, 
# т. е. для создания пула нужно использовать конструкцию async with.
# 
# После того как пул создан, мы можем захватывать соединения
# с по­мощью сопрограммы acquire. Она приостанавливается, до тех
# пор пока в пуле не появится свободное подключение. Затем это подключение 
# можно использовать для выполнения SQL-запроса. Захват
# соединения также является асинхронным контекстным менеджером, 
# который возвращает соединение в пул после использования,
# так что и в этом случае нужна конструкция async with.

async def query_product(pool):
    async with pool.acquire() as connection:
        return await connection.fetchrow(product_query)


async def main():
    async with asyncpg.create_pool(     # создаем пул подключений
        host='127.0.0.1',
        port=5432,
        user='postgres',
        password='password',
        database='products',
        min_size=6,
        max_size=6
    ) as pool:
        # запускаем 2 сопрограммы на выполнение
        await asyncio.gather(query_product(pool), query_product(pool))


# if __name__ == "__main__":
#     asyncio.run(main())
# ==================================================================
# ==================================================================
# сравним время выполнения синхронного и асинхронного подхода.

async def query_product(pool):
    async with pool.acquire() as connection:
        return await connection.fetchrow(product_query)


@async_timed()
async def query_products_synchronously(pool, queries):
    return [await query_product(pool) for _ in range(queries)]


@async_timed()
async def query_products_concurrently(pool, queries):
    queries = [query_product(pool) for _ in range(queries)]
    return await asyncio.gather(*queries)


async def main():
    async with asyncpg.create_pool(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        password='password',
        database='products',
        min_size=6,
        max_size=6
    ) as pool:
        await query_products_synchronously(pool, 10000)
        await query_products_concurrently(pool, 10000)


# if __name__ == "__main__":
    # asyncio.run(main())


# Вывод
# выполняется <function query_products_synchronously at 0x7fb62c7184c0> с аргументами (<asyncpg.pool.Pool object at 0x7fb62c713530>, 10000) {}
# <function query_products_synchronously at 0x7fb62c7184c0> завершилась за 3.4284 с
# 
# выполняется <function query_products_concurrently at 0x7fb62c7185e0> с аргументами (<asyncpg.pool.Pool object at 0x7fb62c713530>, 10000) {}
# <function query_products_concurrently at 0x7fb62c7185e0> завершилась за 1.2668 с

# ==================================================================
