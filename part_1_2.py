# Что такое ограниченность производительностью ввода-вывода и ограниченность 
# быстродействием процессора?

# листинг 1.1
import requests

response = requests.get(url='https://www.google.com') # веб-запрос ограничен производительностью ввода-вывода
items = response.headers.items()
headers = [f'{key}: {header}' for key, header in items] # обработка ответа ограниченна быстродействием процессора
formated_header = '\n'.join(headers) # конкатенация строк ограничена быстройдествием поцессора

with open('headers.txt', 'w') as file:
    file.write(formated_header) # запись на диск ограничена производительностью ввода-вывода