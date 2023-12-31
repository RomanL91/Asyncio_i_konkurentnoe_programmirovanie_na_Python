# И сопрограммы, и задачи можно исползовать в выражениях await. 
# Так что же между ними общего? Чтобы ответить на этот вопрос, нужно 
# знать о типах future и awaitable.
# 
# 2.5.1 Введение в будущие объекты
    # =============================================================================
    # Листинг 2.14 Основы будущих объектов
# from asyncio import Future

# my_future = Future() # создали объект
# print(f'my_future готов? {my_future.done()}') # так как результата done() вернет False

# my_future.set_result(42) # установили значение (через set_exception - установим исключение)
# print(f'my_future готов? {my_future.done()}') # True
# print(f'Какой результат хранится в my_future? {my_future.result()}')   # теперь можно и посмотреть результат, 
                                                                    # без возбуждения исключения InvalidState.
    # =============================================================================


# Будущие объекты также можно использовать в выражениях await.
# Это означает «я посплю, пока в будущем объекте не будет установлено значение, 
# с которым я могу работать, а когда оно появится, разбуди меня и дай возможность его обработать».


    # =============================================================================
    # Листинг 2.15 Ожидание будущего объекта
from asyncio import Future
import asyncio


def make_request() -> Future:
    future = Future() # объект будущего
    asyncio.create_task(set_future_value(future)) # создание задачи асинхронно установить значение в объект будущего
    return future 


async def set_future_value(future) -> None:
    await asyncio.sleep(1) # ждем 1 сек, прежде чем установим значение
    future.set_result(42) # устанавливаем значение


async def main():
    future = make_request()
    print(f'Будущий объект готов? {future.done()}')
    value = await future # приостановим main, пока не будет установлено значение
    print(f'Будущий объект готов? {future.done()}')
    print(value)

asyncio.run(main())

# Пример, где типа из HTTP запроса делаем объект Future в функции make_request(). 
# Future - будет возращено немедленно, то есть функция сразу отдаст результат, тем самым
# она отдаст управление дальше. А потом ее исполним в удобный момент при помощи await,
# получим значение и обработаем. Пока так.
    # =============================================================================


# к разбору далее
# 2.6
# Измерение времени выполнения
# сопрограммы с по­мощью декораторов