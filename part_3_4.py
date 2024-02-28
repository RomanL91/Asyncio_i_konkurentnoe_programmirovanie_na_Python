import selectors
import socket
from selectors import SelectorKey
from typing import List, Tuple

selector = selectors.DefaultSelector() # автоматический выбор реализации 
                                        # системы уведомлений в зависимости от ОС

server_socket = socket.socket() # создание сокета
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_address = ('127.0.0.1', 8000)
server_socket.setblocking(False) # не блокирующий сокет
server_socket.bind(server_address) # привязываем адресс
server_socket.listen()

selector.register(server_socket, selectors.EVENT_READ) # регистрируем сокет для получения уведомлений
                                                        # регистрация событий на чтение
while True:
    events: List[Tuple[SelectorKey, int]] = selector.select(timeout=1) 
    # Селекция - вторая концепция после Регистрации
    # функция select блокирующая функция, пока не произойдет событие
    # ей можно указать время timeout, по истечении которого
    # она вернет пустой список, иначе список сокетов для обработки
    # получается timeout ограничивает время блокировки - такое псевдо не блокирующее состояние

    if len(events) == 0:
        print('Событий нет, подожду еще!')
        # вышли по timeout и список events пуст
    
    for event, _ in events:
        # если список events не пуст, то при итерации
        event_socket = event.fileobj
        # в переменную event_socket через атрибут fileobj получим сокет, 
        # для которого произошло событие

        # далее определяем какой тип события это был
        if event_socket == server_socket:
            connection, address = server_socket.accept()
            connection.setblocking(False)
            print(f"Получен запрос на подключение от {address}")
            selector.register(connection, selectors.EVENT_READ)
        else:
            data = event_socket.recv(1024)
            print(f"Получены данные: {data}")
            event_socket.send(data)