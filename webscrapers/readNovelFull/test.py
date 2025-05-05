import aiohttp
import asyncio

async def save_page(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)

url = 'https://readnovelfull.com/ajax/chapter-archive?novelId=1622'
url = 'https://readnovelfull.com/second-world.html#tab-chapters-title'
filename = 'saved.html'
asyncio.run(save_page(url, filename))

