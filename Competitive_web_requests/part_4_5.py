# 4.5 Обработка результатов по мере поступления


# Хотя во многих случаях функция asyncio.gather нас устраивает, у нее
# есть недостаток – необходимость дождаться завершения всех допускающих 
# ожидания объектов, прежде чем станет возможен доступ
# к результатам. Это проблема, если требуется обрабатывать результаты
# в темпе их получения.
# А также в случае, когда одни объекты завершаются быстро, 
# а другие медленно, потому что gather будет ждать завершения всех.

# Для решения этой проблемы asyncio предлагает функцию as_completed.

# Создадим 3 соспрограммы. Две из них завершатся через 1 сек, а 3 - через 10 сек. 
# Передаем эти сопрограммы функции as_completed. 
# Полное время выполнения  так же как и gather не умсеньшилось, а этого и не может быть.
# Но результаты теперь доступны по мере их готовности.
# За этим правда стоит один минус, если при gather мы получали детермированный
# списковый вывод результатов и ошибок, то теперь этого не будет. Зато при получении
# результата сразу после выполнения выигрываем дополгительное время на его 
# обработку и освобождаем мощности. Исходя из этого обработку исключений мы будем делать
# так же более оперативно.


import asyncio, aiohttp

from utils import fetch_status, async_timed


@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        fetchers = [fetch_status(session, 'http://www.google.com', 1),
                    fetch_status(session, 'http://www.google.com', 1),
                    fetch_status(session, 'http://www.google.com', 10)]
        for finished_task in asyncio.as_completed(fetchers):
            print(await finished_task)


# if __name__ == "__main__":
    # asyncio.run(main())


# 4.5.1 Тайм-ауты в сочетании с as_completed
            
# Любой веб-запрос может занять много времени. Возможно, сервер
# испытывает высокую нагрузку, а возможно, сеть медленная. Выше мы
# видели, как задать тайм-аут для отдельного запроса, но что, если это
# нужно сделать для группы запросов? Функция as_completed предоставляет 
# такую возможность с по­мощью необязательного параметра
# timeout, равного величине тайм-аута в секундах.


@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        fetchers = [fetch_status(session, 'http://google.com', 1),
                    fetch_status(session, 'http://google.com', 10),
                    fetch_status(session, 'http://google.com', 10)]
        
        for done_task in asyncio.as_completed(fetchers, timeout=4):
            try:
                result = await done_task
                print(result)
            except asyncio.TimeoutError:
                print('Произошел тайм-аут!')

        for task in asyncio.tasks.all_tasks():
            print(task)



if __name__ == "__main__":
    asyncio.run(main())


# к разбору далее
# 4.6 Точный контроль с по­мощью wait
