# Работа с блокирующими сокетами
import socket

# Листинг 3.1 Запуск сервера и прослушивание порта для подключения
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #тип адреса и протокол (имя хоста с портом и TCP протокол)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #позволит повторно использовать номер порта
server_address = ('127.0.0.1', 8000) #задаем адресс сокета
server_socket.bind(server_address) 
server_socket.listen()
connection, client_address = server_socket.accept() #дожидаемся подключения и выделяем клиенту адресс (блокирующая операция)
print(f'Получен запрос на подключение от {client_address}!')

# команда telnet localhost 8000 используем для подключения
