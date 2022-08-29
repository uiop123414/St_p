import asyncio
import csv
import json
import random
import time

import aiohttp
import requests
from abstract_parser import abstract_parser
from currency_converter import CurrencyConverter
from service_progs import time_of_function
from bs4 import BeautifulSoup

ls_proxy = ["http://37.187.16.186:80",
            "http://211.150.65.29:80",
            "http://188.214.23.66:80"]


def find_id(path, weapon_name):
    with open("".join((path, "key_values.csv")), encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if weapon_name.lower() == row[1].lower():
                return row[0]


class buff163_parser(abstract_parser):
    def __init__(self, path=""):
        super().__init__()
        self.conn = aiohttp.TCPConnector(limit_per_host=100, limit=0, ttl_dns_cache=300)
        self.path = path
        self.session = aiohttp.ClientSession(connector=self.conn)
        self.cur_CNY_to_USD = CurrencyConverter(
            'http://www.ecb.int/stats/eurofxref/eurofxref-hist.zip').convert(1, "CNY", "USD")

    def get_buy_order_price(self, weapon_name):
        url = f"https://buff.163.com/goods/{find_id(self.path, weapon_name)}?from=market#tab=buying"
        html = requests.get(url)
        # print(html.text)
        soup = BeautifulSoup(html.text, "lxml")
        # print(soup.find("div", "detail-tab-cont").text)

    def get_url_buy_orders(self, weapon_name):
        return f"https://buff.163.com/goods/{find_id(self.path, weapon_name)}?from=market#tab=buying"

    def get_url(self, weapon_name):
        return f"https://buff.163.com/goods/{find_id(self.path, weapon_name)}?from=market#tab=selling"

    @time_of_function
    def get_lowest_price(self, weapon_name: str):
        url = f"https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id={find_id(self.path, weapon_name)}"
        r = requests.get(url)
        items = r.json()
        try:
            data = items["data"]['items'][0]
        except KeyError:
            return None
        price = float(data['price'])
        return price  # * self.cur_CNY_to_USD

    async def lowest_async_price(self, n, item_names, results):
        semaphore = asyncio.Semaphore(n)
        urls = [
            (f"https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id={find_id(self.path, weapon_name)}",
             weapon_name) for
            weapon_name in item_names]

        # heres the logic for the generator
        async def get(url):
            async with semaphore:
                async with self.session.get(url[0]) as response:
                    obj = json.loads(await response.read())
                    if obj['code'] == 'OK':
                        # results.append(
                        #     {url[1]: url[0].split('=')[-1], 'highest_buy_order': float(obj['highest_buy_order']) / 100,
                        #      'lowest_sell_order': min(float(x[0]) for x in obj['sell_order_graph'])})
                        results.append(
                            {"name": url[1],
                             'lowest_price': float(obj['data']['items'][0]['price']) * self.cur_CNY_to_USD})

        await asyncio.gather(*(get(url) for url in urls))
        # await self.session.close()
        return results

    async def get_highest_buy_order_async(self, n, item_names, results):
        semaphore = asyncio.Semaphore(n)
        urls = [
            (
            f"https://buff.163.com/api/market/goods/buy_order?game=csgo&goods_id={find_id(self.path, weapon_name)}&page_num=1&_=1658588669598"
            , weapon_name) for
            weapon_name in item_names]

        # heres the logic for the generator
        async def get(url):
            async with semaphore:
                async with self.session.get(url[0]) as response:
                    obj = json.loads(await response.read())
                    if obj['code'] == 'OK':
                        # results.append(
                        #     {url[1]: url[0].split('=')[-1], 'highest_buy_order': float(obj['highest_buy_order']) / 100,
                        #      'lowest_sell_order': min(float(x[0]) for x in obj['sell_order_graph'])})
                        results.append(
                            {"name": url[1],
                             'lowest_price': float(obj['data']['items'][0]['price']) * self.cur_CNY_to_USD})

        await asyncio.gather(*(get(url) for url in urls))
        # await self.session.close()
        return results

    async def get_list_lowest_prices_async(self, item_names: list):
        PARALLEL_REQUESTS = 100
        results = []

        self.session = aiohttp.ClientSession(connector=self.conn)
        return [{**result, "url": self.get_url(result['name'])} for result in
                await self.lowest_async_price(PARALLEL_REQUESTS, item_names=item_names,
                                              results=results)]

    @time_of_function
    def get_lowest_list_prices(self, item_names: list):
        PARALLEL_REQUESTS = 100
        results = []
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self.lowest_async_price(PARALLEL_REQUESTS, item_names=item_names,
                                    results=results))
        self.session = aiohttp.ClientSession(connector=self.conn)
        self.conn = aiohttp.ClientSession(connector=self.conn)
        return [{**result, "url": self.get_url(result['name'])} for result in results]

    async def get_list_highest_buy_orders_async(self, item_names: list):
        # https://buff.163.com/api/market/goods/buy_order?game=csgo&goods_id=45237&page_num=1&_=1658588669598
        PARALLEL_REQUESTS = 100
        results = []

        self.session = aiohttp.ClientSession(connector=self.conn)
        return [{**result, "url": self.get_url(result['name'])} for result in
                await self.get_highest_buy_order_async(PARALLEL_REQUESTS, item_names=item_names,
                                              results=results)]

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def get_auto_buy_price(self, weapon_name):
        id = find_id(self.path, weapon_name)
        print(id)
        url = f'https://buff.163.com/api/market/goods/buy_order?game=csgo&goods_id={id}&page_num=1&_=1657808768032'
        print(url)
        res = requests.get(url).json()

        print(res['data']['items'][0]['price'])

    def refresh_currency(self):
        self.cur_CNY_to_USD = CurrencyConverter('http://www.ecb.int/stats/eurofxref/eurofxref-hist.zip').convert(1,
                                                                                                                 "CNY",
                                                                                                                 "USD")

    def set_json_file(self):
        with open("".join((self.path, "key_values.csv")), encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=';')
            req = requests.get(
                "https://cs.money/skin_info?appId=730&id=26430858519&isBot=true&botInventory=true").json()
            print(req)

            url = f'https://inventories.cs.money/5.0/load_bots_inventory/730?name={"MP9 | Deadly Poison (Minimal Wear)"}&withStack= true'
            r = requests.get(url)
            items = r.json()

    def buy_item(self, name):
        pass

    def sell_item(self, name):
        pass


#
if __name__ == '__main__':
    # items = []
    # with open("json_items_more.txt", "r", encoding='utf-8') as f:
    #     for row in f:
    #         items.append(row)
    bf = buff163_parser()
    bf.get_auto_buy_price('AK-47 | Jaguar (Field-Tested)')
    item_names = ['AK-47 | Jaguar (Field-Tested)', 'M4A4 | The Emperor (Well-Worn)',
                  '★ Navaja Knife | Safari Mesh (Battle-Scarred)']
    item_names2 = ['AK-47 | Jaguar (Field-Tested)', 'M4A4 | The Emperor (Well-Worn)',
                   '★ Navaja Knife | Safari Mesh (Battle-Scarred)']
    event_loop = asyncio.get_event_loop()

    prices1 = asyncio.gather(bf.get_list_highest_buy_orders_async([item for item in item_names]))
    prices2 = asyncio.gather(bf.get_list_highest_buy_orders_async([item for item in item_names2]))

    all_groups = asyncio.gather(prices1, prices2)

    res = event_loop.run_until_complete(all_groups)
    print(*res, sep='\n')
    print('*' * 50)
# bf.set_json_file()
