import socket, asyncio, aiohttp

from types import TracebackType
from typing import Optional, Type
from aiohttp import ClientSession

from utils import async_timed, delay

# ===================================================
# 4.2 Асинхронные контекстные менеджеры
class ConnectedSocket:
    def __init__(self, server_socket):
        self._connection = None
        self._server_socket = server_socket

    
    async def __aenter__(self):
        print('Вход в контекстный менеджер, ожидание подключения')
        loop = asyncio.get_event_loop()
        connection, address = await loop.sock_accept(self._server_socket)
        self._connection = connection
        print('Подключение подтверждено')
        return self._connection

    
    async def __aexit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]):
        print('Выход из контекстного менеджера')
        self._connection.close()
        print('Подключение закрыто')


async def main():
    loop = asyncio.get_event_loop()
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = ('127.0.0.1', 8000)
    server_socket.setblocking(False)
    server_socket.bind(server_address)
    server_socket.listen()

    async with ConnectedSocket(server_socket) as connection:
        data = await loop.sock_recv(connection, 1024)
        print(data)


# if __name__ == "__main__":
    # asyncio.run(main())
# ===================================================
# ===================================================
# Отправка веб-запроса с по­мощью aiohttp
@async_timed()
async def fetch_status(session: ClientSession, url: str) -> int:
    async with session.get(url) as result:
        return result.status


@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        url = 'https://www.google.com'
        status = await fetch_status(session, url)
        print(f'Состояние для {url} было равно {status}')


# if __name__ == "__main__":
    # asyncio.run(main())
# Простой пример запроса.
# В нем не использована вся сила конкурентности,
# выполнен всего один запрос.
# ===================================================
# ===================================================
# Использование спискового включения для конкурентного выполнения задач
@async_timed()
async def main() -> None:
    delay_times = [3, 2, 3]
    tasks = [asyncio.create_task(delay(seconds)) for seconds in delay_times]
    [await task for task in tasks]


# if __name__ == "__main__":
#     asyncio.run(main())
# Почему бы и нет?! Иногда такой подход будет оптимальным, если 
# не нунжно отслеживать очередность запущенных задач и получение результатов.
# Про что я? Например, вторая задача отрабатывает быстрее и мы хотим получить
# доступ к ее результату как можно скорее, но будем ждать пока не поучим 
# выполнение всех задач и потом может найдем результат. 
    # И самое важное! Если первая задача словит исключение - то другие 
# уже не выполнятся.
# ===================================================
# ===================================================
# Конкурентное выполнение запросов с по­мощью gather
@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        urls = ['http://google.com' for _ in range(100)] # off SSL (http) =)
        requests = [fetch_status(session, url) for url in urls]
        status_codes = await asyncio.gather(*requests)
        print(status_codes)


if __name__ == "__main__":
    asyncio.run(main())
# это пример 100 запросов.
# создан список из url-ов, затем создан список сопрограмм, затем 
# передали gather для выполнения.
# Стоит отметить, что порядок поступления результатов для переданных 
# объектов, допускающих ожидание, не детерминирован. Например, если
#  передать gather сопрограммы a и b именно в таком
# порядке, то b может завершиться раньше, чем a. Но приятная особенность
# gather заключается в том, что, независимо от порядка завершения 
# допускающих ожидание объектов, результаты гарантированно будут возвращены 
# в том порядке, в каком объекты передавались.
# ===================================================

# к разбору далее
# 4.4.1 Обработка исключений при использовании gather
