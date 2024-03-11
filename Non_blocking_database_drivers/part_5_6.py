# 5.6 Управление транзакциями в asyncpg
# 
# Транзакции – ключевая концепция во многих базах данных, обладающих 
# свойствами ACID (атомарность, согласованность, изолированность, долговечность). 
# Транзакция включает одну или несколько SQL-команд, выполняемых как неделимое целое. 
# Если при выполнении этих команд не возникло ошибки, то транзакция фиксируется в базе
# данных, так что изменения становятся постоянными. Если же ошибки были, 
# то транзакция откатывается и база данных выглядит так,
# будто ни одна из команд не выполнялась. В случае нашей базы данных о товарах 
# необходимость в откате набора обновлений может возникнуть, если мы попытаемся 
# вставить дубликат марки или нарушим установленное ограничение целостности.
# 
# Рассмотрим, как создать транзакцию и выполнить две простые команды
# insert для добавления двух марок.

import asyncio, asyncpg, logging

# ==================================================================
# Создание транзакции

async def main():
    connection = await asyncpg.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        database='products',
        password='password'
    )

    async with connection.transaction():
        await connection.execute("INSERT INTO brand " "VALUES(DEFAULT, 'brand_1')")
        await connection.execute("INSERT INTO brand " "VALUES(DEFAULT, 'brand_2')")

    query = """SELECT brand_name FROM brand WHERE brand_name LIKE 'brand%'"""

    brands = await connection.fetch(query)
    print(brands) # [<Record brand_name='brand_1'>, <Record brand_name='brand_2'>]

    await connection.close()

# Тут отработает все и никаких ошибок получено не будет.
# ==================================================================
# Давайте убедимся, что при врзникновении ошибки, транзакция
# не применятся и ничего не сохраняется в БД.

async def main():
    connection = await asyncpg.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        database='products',
        password='password'
    )
    try:
        async with connection.transaction():
            insert_brand = "INSERT INTO brand VALUES(9999, 'big_brand')"
            await connection.execute(insert_brand)
            await connection.execute(insert_brand) # пытаемся вставить с одним и тем же ID
    except Exception:
        logging.exception('Ошибка при выполнении транзакции')
    finally:
        query = """SELECT brand_name FROM brand WHERE brand_name LIKE 'big_%'"""
        brands = await connection.fetch(query)
        print(f'Результат запроса: {brands}')
        await connection.close()

# Вывод
# ERROR:root:Ошибка при выполнении транзакции
# Traceback (most recent call last):
#   File "----", line 58, in main
#     await connection.execute(insert_brand) # пытаемся вставить с одним и тем же ID
#   File "----",, line 350, in execute
#     result = await self._protocol.query(query, timeout)
#   File "asyncpg/protocol/protocol.pyx", line 374, in query
# asyncpg.exceptions.UniqueViolationError: duplicate key value violates unique constraint "brand_pkey"
# DETAIL:  Key (brand_id)=(9999) already exists.
# Результат запроса: []

# Возникло исключение, потому что мы пытались вставить
# дубликат ключа, а затем мы видим, что результат команды select
# пуст, т. е. мы успешно откатили транзакцию.
# ==================================================================


# if __name__ == "__main__":
#     asyncio.run(main())
        

# Далее к разбору 5.6.1 Вложенные транзакции
        

# ==================================================================
# 5.6.1 Вложенные транзакции
        
# Аsyncpg поддерживает также вложенные транзакции благодаря имеющемуся в 
# Postgres механизму точек сохранения, которые определяются 
# командой SAVEPOINT. Если определена точка сохранения, то мы
# можем откатиться к ней, т. е. все запросы, выполненные после точки
# сохранения, откатываются, а те, что были до нее, – нет.


async def main():
    connection = await asyncpg.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        database='products',
        password='password'
    )
    
    async with connection.transaction():
        
        await connection.execute("INSERT INTO brand VALUES(DEFAULT, 'my_new_brand')")
        
        try:
            async with connection.transaction():
                # ошибка дубликата ключа
                await connection.execute("INSERT INTO product_color VALUES(1, 'black')")
        except Exception as ex:
            logging.warning('Ошибка при вставке цвета товара игнорируется', exc_info=ex)
        
        await connection.close()

# тут вышло добиться поведения, что при возникновении ошибки мы сохраним первую вставку.
# ==================================================================
# ==================================================================
# 5.6.2 Ручное управление транзакциями
        

from asyncpg.transaction import Transaction


async def main():
    connection = await asyncpg.connect(
        host='127.0.0.1',
            port=5432,
            user='postgres',
            database='products',
            password='password'
    )
    
    transaction: Transaction = connection.transaction() # экземпляр транзакции
    await transaction.start() # начало транзакции
    
    try:
        await connection.execute("INSERT INTO brand " "VALUES(DEFAULT, 'brand_1')")
        await connection.execute("INSERT INTO brand " "VALUES(DEFAULT, 'brand_2')")
    except asyncpg.PostgresError:
        print('Ошибка, транзакция откатывается!')
        await transaction.rollback()
    else:
        print('Ошибки нет, транзакция фиксируется!')
        await transaction.commit()
    
    query = """SELECT brand_name FROM brand WHERE brand_name LIKE 'brand%'"""
    brands = await connection.fetch(query)
    print(brands)
    await connection.close()


# if __name__ == "__main__":
#     asyncio.run(main())
# ==================================================================

# Далее к разбору 
# 5.7 Асинхронные генераторы и потоковая
# обработка результирующих наборов
