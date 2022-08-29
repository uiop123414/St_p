import signal
import sys
import asyncio
import aiohttp
import json

loop = asyncio.get_event_loop()
client = aiohttp.ClientSession(loop=loop)


async def get_json(url, client):
    async with client.get(url) as response:
        assert response.status == 200
        return await response.read()


async def get_lowest_price(item_name):
    url = f'https://inventories.cs.money/5.0/load_bots_inventory/730?name={item_name}'
    print(url)
    items = await get_json(url, client)
    items = json.loads(items.decode("utf-8"))
    for item in items['items']:
        print(item['price'])
    print("Over")


def signal_handler(signal, frame):
    loop.stop()
    client.close()
    sys.exit(0)


name = "P250 | Red Rock (Battle-Scarred)"
asyncio.ensure_future(get_lowest_price(name))
loop.run_forever()
signal.signal(signal.SIGINT, signal_handler)
loop.close()
