import socket

# ===================================================================
# Листинг 3.2
# Чтение данных из сокета
# подключение одного клиента
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ('127.0.0.1', 8000)
server_socket.bind(server_address)
server_socket.listen()

connections = []

# try:
#     connection, client_address = server_socket.accept()
#     print(f'Получен запрос на подключение от {client_address}!')
#     buffer = b''

#     while buffer[-2:] != b'\r\n':
#         data = connection.recv(2)
#         if not data:
#             break
#         else:
#             print(f'Получены данные: {data}!')
#             buffer = buffer + data
#     print(f"Все данные: {buffer}")
#     connection.sendall(buffer) # эхо - отправим обратно клиенту
# finally:
#     server_socket.close()
# ===================================================================
try:
    while True:
        connection, client_address = server_socket.accept()
        print(f'Получен запрос на подключение от {client_address}!')
        connections.append(connection)
        
        for connection in connections:
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
finally:
    server_socket.close()

# Первый клиент работает и получает копии своих сообщений,
# как и положено, а вот второй не получает ничего. Связано это с тем,
# что по умолчанию сокеты блокирующие. Методы accept и recv бло-
# кируют выполнение программы, пока не получат данные. А значит,
# после того как первый клиент подключился, мы будем ждать,
# он отправит свое первое сообщение. А остальные клиенты в это вре-
# мя зависнут в ожидании следующей итерации цикла, которая не про-
# изойдет, пока не придут данные от первого клиента
