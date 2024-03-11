# 5.7 Асинхронные генераторы и потоковая
# обработка результирующих наборов
# 
# Кратко и своими словами обозначу проблему:
# у реализации fetch по умолчанию в asynpg есть один недостаток - 
# она загружает все возвращенные по запросу данные в память.
# Что если данных слишком много?!
# Можно использовать же LIMIT при запросе?! - другими словами
# отправлять один и тот же запрос по сети несколько раз. Для большинства
# приложений - это норма, но что если нам нужно получать данные
# потоком, что могло бы снизить потребление памяти со стороны приложения 
# и снизить нагрузку на БД.
# Postgres поддерживает потоковую обработку результатов запроса
# с по­мощью курсоров. Курсор можно рассматривать как указатель на
# текущую позицию в результирующем наборе. Получая один результат
# из потокового запроса, мы продвигаем курсор на следующую позицию и т. д., 
# пока результаты не будут исчерпаны.


import asyncio, asyncpg, logging

from utils import delay, async_timed


# ==================================================================
# Листинг 5.14 Простой асинхронный генератор


async def positive_integers_async(until: int):
    for integer in range(1, until):
        await delay(integer)
        yield integer


@async_timed()
async def main():
    async_generator = positive_integers_async(3)
    print(type(async_generator))
    async for number in async_generator:
        print(f'Получено число {number}')

# ==================================================================
# ==================================================================
# Здесь распечатываются все имеющиеся товары.   
# Хотя в таблице хранится 1000 товаров, в память загружается лишь небольшая порция.
# Данная порция по умолчанию была равно 50 записей, чтобы уменьшить затраты
# на сетевой трафик, это значение можно изменить, задав параметр prefetch.
        

async def main():
    connection = await asyncpg.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        database='products',
        password='password'
    )
    query = 'SELECT product_id, product_name FROM product'
    async with connection.transaction():
        async for product in connection.cursor(query):   
            print(product)
    
    await connection.close()    

# ==================================================================
# ==================================================================
# Листинг 5.16 Перемещение по курсору и выборка записей
    

async def main():
    connection = await asyncpg.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        database='products',
        password='password'
    )

    async with connection.transaction():
        query = 'SELECT product_id, product_name from product'
        cursor = await connection.cursor(query) # курсор для запроса
        await cursor.forward(500) # сдвигаем на 500 записей
        products = await cursor.fetch(100) # получаем следующие 100 записей
        
        for product in products:
            print(product)
    
    await connection.close()

# ==================================================================
# ==================================================================
# Листинг 5.17 Получение заданного числа элементов с по­мощью асинхронного генератора
    
# Но что, если нам только и нужно, что выбрать фиксированное число 
# элементов с предвыборкой, но при этом использовать цикл async
# for? Можно было бы добавить в цикл async for счетчик и выходить из
# цикла после получения некоторого числа элементов, но такой подход
# не приспособлен для повторного использования. Если такие действия
# производятся в программе часто, то лучше написать свой собственный 
# асинхронный генератор, который мы назовем take. Он будет
# принимать асинхронный генератор и число элементов. Покажем, как
# это делается, на примере выборки первых пяти элементов из резуль тирующего набора.

async def take(generator, to_take: int):
    item_count = 0
    async for item in generator:
        if item_count > to_take - 1:
            return
        item_count = item_count + 1
        yield item


async def main():
    connection = await asyncpg.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        database='products',
        password='password'
    )

    async with connection.transaction():
        
        query = 'SELECT product_id, product_name from product'
        product_generator = connection.cursor(query)
        
        async for product in take(product_generator, 5):
            print(product)
        
        print('Получены первые пять товаров!')

    await connection.close()

# Наш асинхронный генератор take хранит число уже отданных элементов 
# в переменной item_count. В цикле async_for он отдает нам
# запи­си с по­мощью предложения yield и, как только будет отдано
# item_count элементов, выполняет return и тем самым завершает работу. 
# А в сопрограмме main можно использовать take в цикле async for, как обычно.
# ==================================================================
# ==================================================================
# if __name__ == "__main__":
    # asyncio.run(main())
# Раскоментировать и подставить в нужный блок.
# ==================================================================
