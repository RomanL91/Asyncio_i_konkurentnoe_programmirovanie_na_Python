# 5.2 Подключение к базе данных Postgres
# 
# Пример подключения к базе данных от имени пользователя по 
# умолчанию.
# Подключаемся, методом get_server_version достаем информацию
# о версии сервера, принтим эту инфу и закрываем подключение.
# База пустая и для дайнейшей работы с ней создадим схему.


import asyncio, asyncpg


async def main():
    connection = await asyncpg.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        database='postgres',
        password='password'
    )
    
    version = connection.get_server_version()
    print(f'Подключено! Версия Postgres равна {version}')
    # Подключено! Версия Postgres равна ServerVersion(major=15, minor=0, micro=4, releaselevel='final', serial=0)
    
    await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
