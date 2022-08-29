import asyncio
import json
from threading import Thread
from service_progs import time_of_function
import aiohttp
import requests
from abstract_parser import abstract_parser
from bs4 import BeautifulSoup


async def lowest_async_price(n, conn, item_names, results):
    semaphore = asyncio.Semaphore(n)
    session = aiohttp.ClientSession(connector=conn)
    urls = [f'https://inventories.cs.money/5.0/load_bots_inventory/730?name={weapon_name}' for
            weapon_name in item_names]

    # heres the logic for the generator
    async def get(url):
        async with semaphore:
            async with session.get(url) as response:
                print(response.status)
                assert response.status == 200
                obj = json.loads(await response.read())

                results.append(
                    {"name": obj['items'][0]['fullName'],
                     'lowest_price': obj['items'][0]['price']})

    await asyncio.gather(*(get(url) for url in urls))
    await session.close()


class csm_parser(abstract_parser):

    def __init__(self):
        self.conn = aiohttp.TCPConnector(limit_per_host=100, limit=0, ttl_dns_cache=300)
        super().__init__()

    # @time_of_function
    def get_lowest_price2(self, item_name):
        url = "".join(("https://cs.money/ru/csgo/trade/?search=", item_name, "%29&sort=price&order=asc"))
        html = requests.get(url)
        soup = BeautifulSoup(html.text, "lxml")
        s = soup.find('script', id="__NEXT_DATA__")
        return json.loads(s.text)['props']['pageProps']['botInitData']['skinsInfo']['skins'][0]['price']

    def get_price_my_stuff(self, item_name):
        url = "https://cs.money/skin_info?appId=730&id=10123582496&isBot=false&botInventory=false"

    # @time_of_function
    def get_lowest_price(self, item_name):
        url = f'https://inventories.cs.money/5.0/load_bots_inventory/730?name={item_name}&withStack= true'
        items = requests.get(url).json()['items']
        return min(items, key=lambda x: x['price'])['price']

    @time_of_function
    def get_lowest_list_prices(self, item_names: list):
        PARALLEL_REQUESTS = 100
        results = []
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            lowest_async_price(PARALLEL_REQUESTS, conn=self.conn, item_names=item_names,
                               results=results))
        return results

    def buy_item(self, item_name):
        pass

    def get_url(self, item_name):
        return "".join(("https://cs.money/ru/csgo/trade/?search=", item_name, "%29&sort=price&order=asc"))

    def sell_item(self, item_name):
        pass

    def balance_account(self):
        pass


def main(name):
    c = csm_parser()
    item_names = ['AK-47 | Jaguar (Field-Tested)', 'M4A4 | The Emperor (Well-Worn)',
                  '★ Navaja Knife | Safari Mesh (Battle-Scarred)', "MP7 | Armor Core (Factory New)",
                  "M249 | Spectre (Factory New)"]
    print(*c.get_lowest_list_prices(item_names), sep='\n')


if __name__ == '__main__':
    name = "MP7 | Armor Core (Factory New)"
    name = "SG 553 | Triarch (Field-Tested)"
    main(name)
