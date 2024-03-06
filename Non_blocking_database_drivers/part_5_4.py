# 5.4 Выполнение запросов с помощью asyncpg

# К этому моменту мы должны создать БД 
# sudo -u postgres psql -c "CREATE TABLE products;".

import asyncio, asyncpg

from asyncpg import Record

from typing import List

from part_5_3 import * 

# ==================================================================
# Пример подключения, создания таблиц и вставки
async def main():
    connection = await asyncpg.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        database='products',
        password='password'
    )

    statements = [
        CREATE_BRAND_TABLE,             # CREATE TABLE
        CREATE_PRODUCT_TABLE,           # CREATE TABLE
        CREATE_PRODUCT_COLOR_TABLE,     # CREATE TABLE
        CREATE_PRODUCT_SIZE_TABLE,      # CREATE TABLE
        CREATE_SKU_TABLE,               # CREATE TABLE
        SIZE_INSERT,                 # INSERT 0 1
        COLOR_INSERT                 # INSERT 0 1
    ]

    print('Создается база данных product...')

    for statement in statements:
        status = await connection.execute(statement)
        print(status)
    
    print('База данных product создана!')
    await connection.close()

# В этом примере мы ожидаем завершения каждой SQL-команды 
# с по­мощью await в цикле for, поэтому команды INSERT будут
# выполнены синхронно. Поскольку одни таблицы зависят от других,
# мы не можем выполнять эти команды конкурентно.
    
# if __name__ == "__main__":
#     asyncio.run(main())
# ==================================================================
# ==================================================================
# Пример вставки (записи) и получения (чтения)
async def main():
    connection = await asyncpg.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        database='products',
        password='password'
    )
    # Вставка
    await connection.execute("INSERT INTO brand VALUES(DEFAULT, 'Levis')")
    await connection.execute("INSERT INTO brand VALUES(DEFAULT, 'Seven')")
    # Получения всех марок из brand
    # Каждый результат представлен объектом asyncpg Record. 
    # Эти объекты похожи на словари: они позволяют обращаться к данным,
    # передавая имя столбца в качестве индекса.
    brand_query = 'SELECT brand_id, brand_name FROM brand'
    results: List[Record] = await connection.fetch(brand_query)

    for brand in results:
        print(f'id: {brand["brand_id"]}, name: {brand["brand_name"]}')
    await connection.close()

# В этом примере все возвращенные запросом данные помещены
# в список. Если бы мы хотели выбрать одну запись, то вызвали бы
# функцию connection.fetchrow(). По умолчанию все результаты запроса 
# загружаются в память, поэтому пока нет разницы в производительности 
# между fetchrow и fetch. Ниже в этой главе мы узнаем,
# как обрабатывать результирующие наборы потоком с по­мощью курсоров. 
# Тогда в память загружается только небольшое подмножество
# результатов; это полезно, если запрос может возвращать очень много данных.
    
# В этом примере запросы выполняются один за другим, поэтому
# синхронный драйвер базы данных показал бы такую же производительность. 
# Но поскольку теперь мы возвращаем сопрограммы, ничто
# не мешает использовать изученные в главе 4 методы asyncio API для
# конкурентного выполнения запросов.

# ==================================================================

# if __name__ == "__main__":
#     asyncio.run(main())

# Далее к разбору
# 5.5 Конкурентное выполнение запросов с помощью пулов подключений
