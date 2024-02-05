# 2.8 Ручное управление циклом событий.

import asyncio


# =========================================================
# Листинг 2.21
# Создание цикла событий вручную

# async def main():
    # await asyncio.sleep(1)
# 
# loop = asyncio.new_event_loop()
# 
# try:
    # loop.run_until_complete(main())
# finally:
    # loop.close()
# =========================================================
# Листинг 2.22
# Получение доступа к циклу событий

def call_later():
    print("Меня вызовут в ближайшем будущем!")


async def main():
    loop = asyncio.get_running_loop()
    loop.call_soon(call_later) # выполнение функции на следующей итерации цикла событий
    print('sleep 3 sec')
    await asyncio.sleep(3)

asyncio.run(main())

