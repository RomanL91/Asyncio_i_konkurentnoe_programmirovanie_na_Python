import asyncio, aiohttp

from utils import fetch_status, async_timed


# 4.4.1 Обработка исключений при использовании gather

@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        urls = ['https://google.com', 'python://example.com']
        tasks = [fetch_status(session, url) for url in urls]
        status_codes = await asyncio.gather(*tasks, return_exceptions=True)
        print(status_codes)


# Функция gather имеет несколько недостатков. Первый мы уже упоминали – не так 
# просто отменить задачи, если одна из них возбудила
# исключение. Представьте, что мы отправляем запросы одному серверу, 
# и если хотя бы один завершится неудачно, например из-за превышения 
# лимита на частоту запросов, то остальные постигнет та же
# участь. В таком случае хотелось бы отменить запросы, чтобы освободить 
# ресурсы, но это нелегко, потому что наши сопрограммы обернуты 
# задачами и работают в фоновом режиме.
# Второй недостаток – необходимость дождаться завершения всех
# сопрограмм, прежде чем можно будет приступить к обработке результатов. 
# Если мы хотим обрабатывать результаты по мере поступления, 
# то возникает проблема. Например, если один запрос выполняется 100 мс, 
# а другой 20 с, то придется ждать, ничего не делая, 20 с,
# прежде чем мы сможем обработать результаты первого запроса.
# Аsyncio предлагает API, позволяющие решить обе проблемы. 
# Сначала посмотрим, как обрабатывать результаты по мере поступления.


if __name__ == "__main__":
    asyncio.run(main())
