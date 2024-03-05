# 4.6 Точный контроль с по­мощью wait

# >>>>>>>>>> 4.6.1 Ожидание завершения всех задач


import asyncio, aiohttp, logging
from utils import fetch_status, async_timed

# ============================================================
# Здесь мы конкурентно выполняем два веб-запроса, передавая wait
# список задач. Предложение await wait вернет управление, когда все
# запросы завершатся, и мы получим два множества: завершившиеся
# задачи и еще работающие задачи. Множество done содержит все задачи, 
# которые завершились успешно или в результате исключения,
# а множество pending – еще не завершившиеся задачи. В данном случае 
# мы задали режим ALL_COMPLETED, поэтому множество pending будет 
# пустым, так как asyncio.wait не вернется, пока все не завершится.

@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        fetchers = \
            [asyncio.create_task(fetch_status(session, 'http://google.com')),
            asyncio.create_task(fetch_status(session, 'http://google.com'))]
        
        done, pending = await asyncio.wait(fetchers)

        print(f'Число завершившихся задач: {len(done)}')
        print(f'Число ожидающих задач: {len(pending)}')
        for done_task in done:
            result = await done_task
            print(result)

# ============================================================
# ============================================================
# Листинг 4.11 Обработка исключений при использовании wait

# Функция done_task.exception() проверяет, имело ли место исключение. 
# Если нет, то можно получить результат из done_task методом result. 
# Здесь также было бы безопасно написать result = await
# done_task, хотя при этом может возникнуть исключение, чего мы,
# возможно, не желаем. Если результат exception() не равен None, то
# в допускающем ожидание объекте возникло исключение и его можно
# обработать, как нам угодно.

@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        good_request = fetch_status(session, 'http://www.google.com')
        bad_request = fetch_status(session, 'python://bad')

        fetchers = [asyncio.create_task(good_request),
                    asyncio.create_task(bad_request)]
        
        done, pending = await asyncio.wait(fetchers)
       
        print(f'Число завершившихся задач: {len(done)}')
        print(f'Число ожидающих задач: {len(pending)}')
        
        for done_task in done:
            # result = await done_task возбудит исключение
            if done_task.exception() is None:
                print(done_task.result())
            else:
                logging.error("При выполнении запроса возникло исключение",
            exc_info=done_task.exception()) 

# ============================================================
# ============================================================
# >>>>>>>>>> 4.6.2 Наблюдение за исключениями

# Режим ALL_COMPLETED страдает всеми теми же недостатками, что
# и gather. Пока мы ждем завершения сопрограмм, может возникнуть
# сколько угодно исключений, но мы их не увидим, пока все задачи не
# завершатся. Это может стать проблемой, если после первого же исключения 
# следует снять все остальные выполняющиеся запросы.
# Кроме того, немедленная обработка ошибок желательна для повышения 
# отзывчивости приложения.
# Чтобы поддержать эти сценарии, wait имеет режим FIRST_EXCEPTION. 
# В этом случае мы получаем два разных поведения в зависимости от того, 
# возникает в какой-то задаче исключение или нет.
#      |
#      |----> Ни один допускающий ожидание объект не возбудил исключения.
#      |      Если ни в одной задаче не было исключений, то этот режим эквивалентен
#      |      ALL_COMPLETED. Мы дождемся завершения всех задач, после чего множество 
#      |      done будет содержать все задачи, а множество pending останется пустым.
#      |
#      |----> В одной или нескольких задачах возникло исключение
#             Если хотя бы в одной задаче возникло исключение, то wait немедленно
#             возвращается. Множество done будет содержать как задачи, завершившиеся 
#             успешно, так и те, в которых имело место исключение. Гарантируется,
#             что done будет содержать как минимум одну задачу – завершившуюся
#             ошибкой, но может содержать и какие-то успешно завершившиеся задачи. 
#             Множество pending может быть пустым, а может содержать задачи, 
#             которые продолжают выполняться. Мы можем использовать его для
#             управления выполняемыми задачами по своему усмотрению.

# Здесь мы отправляем один плохой запрос и два хороших, по 3 с каждый. 
# Ожидание завершения wait прекращается почти сразу, потому
# что плохой запрос тут же завершается с ошибкой. Затем мы в цикле
# обходим множество done. В данном случае оно будет содержать всего
# одну задачу, потому что первый запрос немедленно завершился в результате исключения. 
# Для нее мы идем по ветви, печатающей сведения об исключении.
# Множество pending содержит два элемента, поскольку у нас есть два
# запроса, исполняющихся примерно по 3 с, а первый запрос закончился почти сразу. 
# Мы не хотим, чтобы оставшиеся запросы продолжали выполняться, 
# поэтому прерываем их методом cancel.

@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        fetchers = \
            [asyncio.create_task(fetch_status(session, 'python://bad.com')),
            asyncio.create_task(fetch_status(session, 'http://www.google.com', delay=3)),
            asyncio.create_task(fetch_status(session, 'http://www.google.com', delay=3))]
        
        done, pending = await asyncio.wait(fetchers, return_when=asyncio.FIRST_EXCEPTION)

        print(f'Число завершившихся задач: {len(done)}')
        print(f'Число ожидающих задач: {len(pending)}')

        for done_task in done:
            if done_task.exception() is None:
                print(done_task.result())
            else:
                logging.error("При выполнении запроса возникло исключение",
                    exc_info=done_task.exception())
        
        for pending_task in pending:
            pending_task.cancel()
# ============================================================
# ============================================================
# >>>>>>>>>> 4.6.3 Обработка результатов по мере завершения

@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        url = 'http://www.google.com'
        fetchers = [asyncio.create_task(fetch_status(session, url)),
                    asyncio.create_task(fetch_status(session, url)),
                    asyncio.create_task(fetch_status(session, url))]
        
        done, pending = await asyncio.wait(fetchers, return_when=asyncio.FIRST_COMPLETED)

        print(f'Число завершившихся задач: {len(done)}')
        print(f'Число ожидающих задач: {len(pending)}')

        for done_task in done:
            print(await done_task)

# Описанный подход позволяет реагировать, как только завершится 
# первая задача. Но что, если мы хотим обработать и остальные результаты 
# по мере поступления, как при использовании as_completed?
# ============================================================
# ============================================================
# Предыдущий пример легко можно модифицировать, так чтобы задачи из множества 
# pending обрабатывались в цикле, пока там ничего не останется. 
# Тогда мы получим поведение, аналогичное as_completed,
# с тем дополнительным преимуществом, что на каждом шаге точно
# знаем, какие задачи завершились, а какие еще работают.
            
@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        url = 'http://www.google.com'
        pending = [asyncio.create_task(fetch_status(session, url)),
                    asyncio.create_task(fetch_status(session, url)),
                    asyncio.create_task(fetch_status(session, url))]
    
        while pending:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

            print(f'Число завершившихся задач: {len(done)}')
            print(f'Число ожидающих задач: {len(pending)}')

            for done_task in done:
                print(await done_task)

# Здесь мы создаем множество pending и инициализируем его задачами, 
# которые хотим выполнить. Цикл while выполняется, пока в pending остаются элементы, 
# и на каждой итерации мы вызываем wait для этого множества. 
# Получив результат от wait, мы обновляем множества done и pending, 
# а затем печатаем завершившиеся задачи.
# Получается поведение, похожее на as_completed, с тем отличием, что
# теперь мы лучше знаем, какие задачи завершились, а какие продолжают работать.
# ============================================================
# ============================================================
# 4.6.4 Обработка тайм-аутов
                
@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        url = 'http://google.com'
        
        fetchers = [asyncio.create_task(fetch_status(session, url)),
                    asyncio.create_task(fetch_status(session, url)),
                    asyncio.create_task(fetch_status(session, url, 10))]
        
        done, pending = await asyncio.wait(fetchers, timeout=3)
        
        print(f'Число завершившихся задач: {len(done)}')
        print(f'Число ожидающих задач: {len(pending)}')

        for done_task in done:
            result = await done_task
            print(result)

# Здесь wait вернет множества done и pending через 3 с. 
# В множестве done будет два быстрых запроса, поскольку они успевают завершиться
# за это время. А медленный запрос еще работает, поэтому окажется
# в множестве pending. Затем мы ждем задачи из done с по­мощью await
# и получаем возвращенные ими значения. При желании можно было
# бы снять задачу, находящуюся в pending.
# ============================================================


# переместить под блок кода, который хочешь запустить
if __name__ == "__main__":
    asyncio.run(main())


# к разбору далее
# 5 Неблокирующие драйверы баз данных
