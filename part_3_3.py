# Листинг 3.4 Создание неблокирующего сокета

import socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('127.0.0.1', 8000))
server_socket.listen()
server_socket.setblocking(False)


connections = []
try:
    while True:
        try:
            connection, client_address = server_socket.accept()
            connection.setblocking(False)
            print(f'Получен запрос на подключение от {client_address}!')
            connections.append(connection)
        except BlockingIOError:
            pass
        
        for connection in connections:
            try:
                buffer = b''
                while buffer[-2:] != b'\r\n':
                    data = connection.recv(2)
                    if not data:
                        break
                    else:
                        print(f'Получены данные: {data}!')
                        buffer = buffer + data
                print(f"Все данные: {buffer}")
                connection.send(buffer)
            except BlockingIOError:
                pass
finally:
    server_socket.close()


# Описанный подход работает, но обходится дорого. 
# Первый недостаток – качество кода. Перехват исключений всякий раз, как не ока-
# зывается данных, приводит к многословному и чреватому ошибками коду. 
# Второй – потребление ресурсов. Запустив эту программу на
# ноутбуке, вы уже через несколько секунд услышите, что вентилятор
# начал работать громче. Это приложение постоянно потребляет почти 100 % 
# процессорного времени поскольку мы выполняем итерации цикла и получаем 
# исключения настолько быстро, насколько позволяет операционная система. 
# В результате в рабочей нагрузке преобладает потребление процессора.
    
# к разбору далее
# 3.4
# Использование модуля selectors для построения цикла событий сокетов
