# Вставка данных в базу.
import asyncio, asyncpg

from typing import List, Tuple, Union

from random import randint, sample

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
