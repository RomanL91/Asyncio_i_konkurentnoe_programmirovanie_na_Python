import asyncio, signal, socket, logging

from typing import Set, List

from asyncio import AbstractEventLoop

from part_2_3 import delay

# ===================================================
# 3.6.1 Прослушивание сигналов
# Пример добавление обработчика сигнала, снимающего все задачи
def cancel_tasks():
    print('Получен сигнал SIGINT!')
    tasks: Set[asyncio.Task] = asyncio.all_tasks()
    print(f'Снимается {len(tasks)} задач.')
    [task.cancel() for task in tasks]


async def main():
    loop: AbstractEventLoop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, cancel_tasks)
    await delay(10)


# if __name__ == "__main__":
#     asyncio.run(main())

# Запустив это приложение, мы увидим, что сопрограмма delay начинает 
# работать сразу и ждет 10 с. Если в течение этих 10 с нажать
# CTRL+C, то мы увидим сообщение «Получен сигнал SIGINT!», а вслед
# за ним сообщение о том, что снимаются все задачи. Кроме того, мы
# увидим, что в asyncio.run(main()) возбуждено исключение CancelledError, 
# поскольку мы сняли задачу.
# ===================================================

# ===================================================
# 3.6.2 Ожидание завершения начатых задач
async def echo(connection: socket, loop: AbstractEventLoop) -> None:
    try:
        while data := await loop.sock_recv(connection, 1024):
            print('got data!')
            if data == b'boom\r\n':
                raise Exception("Неожиданная ошибка сети")
            await loop.sock_sendall(connection, data)
    except Exception as ex:
        logging.exception(ex)
    finally:
        connection.close()

echo_tasks = []


async def connection_listener(server_socket, loop):
    while True:
        connection, address = await loop.sock_accept(server_socket)
        connection.setblocking(False)
        print(f"Получено сообщение от {address}")
        echo_task = asyncio.create_task(echo(connection, loop))
        echo_tasks.append(echo_task)


class GracefulExit(SystemExit):
    pass


def shutdown():
    raise GracefulExit()


async def close_echo_tasks(echo_tasks: List[asyncio.Task]):
    waiters = [asyncio.wait_for(task, 2) for task in echo_tasks]
    for task in waiters:
        try:   
            await task
        except asyncio.exceptions.TimeoutError:
            # Здесь мы ожидаем истечения тайм-аута
            print('[==INFO==] Ждёмс завершения')
            pass


async def main():
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = ('127.0.0.1', 8000)
    server_socket.setblocking(False)
    server_socket.bind(server_address)
    server_socket.listen()
    for signame in {'SIGINT', 'SIGTERM'}:
        loop.add_signal_handler(getattr(signal, signame), shutdown)
    await connection_listener(server_socket, loop)

loop = asyncio.new_event_loop()

try:
    loop.run_until_complete(main())
except GracefulExit:
    loop.run_until_complete(close_echo_tasks(echo_tasks))
finally:
    loop.close()


if __name__ == "__main__":
    asyncio.run(main())
# От себя.
# Этим примером достигнуто следующее поведние программы: 
# теперь сервер ждет по 2 секунды от каждого соединения,
# давая задачам echo завершится, а затем остановится сам.
# Из недостатков, что мы перехватываем только TimeoutError,
# а ошибки могут быть и другие, которые мы запишем, но 
# проигнорируем другие исключения. И еще останавливая задачу 
# echo не останавливается прослушиватель задач, в буквальном смысле
# если сервер работает и к нему подключен клиент, остановими сервер
# идет таймер 2 секунд и если за это время подсоединится еще один 
# клиент - магии завершения в 2 секунды для последнего 
# клиентв не произойдет.
# ===================================================
