import asyncio
import json
import re

import aiohttp
import requests
from abstract_parser import abstract_parser
from bs4 import BeautifulSoup


def get_id(item_name):
    url = "https://steamcommunity.com/market/listings/730/"
    html = requests.get("".join((url, item_name))).text
    s = BeautifulSoup(html, 'lxml')
    id = None
    for script in s.find_all('script'):
        id_regex = re.search('Market_LoadOrderSpread\(([ 0-9]+)\)', script.text)
        if id_regex:
            id = id_regex.groups()[0].strip()
            break
    return id


class market_cs_go_parser(abstract_parser):

    def __init__(self, api_key=""):
        super().__init__()
        self.conn = aiohttp.TCPConnector(limit_per_host=100, limit=0, ttl_dns_cache=300)
        self.api_key = api_key
        self.url_item = "https://market.csgo.com/api/v2/prices/class_instance/USD.json"
        if not requests.get(f"https://market.csgo.com/api/v2/get-ws-auth?key={api_key}").json()['success']:
            raise ConnectionError("Fail connection")

    def get_all_data(self, item_name):
        url = f"https://market.csgo.com/api/v2/search-item-by-hash-name-specific?key={self.api_key}&hash_name={item_name}"
        return requests.get(url).json()

    async def get_lowest_list_price_async(self, item_names):
        """
                :param item_names : list :
                :return:dictionary with id and price of item
        """

        urls = [
            (
                f"https://market.csgo.com/api/v2/search-item-by-hash-name-specific?key={self.api_key}&hash_name={item_name}"
                , item_name)
            for item_name in item_names]
        PARALLEL_REQUESTS = 100
        semaphore = asyncio.Semaphore(PARALLEL_REQUESTS)
        session = aiohttp.ClientSession(connector=self.conn)
        results = []

        # heres the logic for the generator
        async def get(url):
            async with semaphore:
                async with session.get(url[0]) as response:
                    obj = json.loads(await response.read())
                    if obj['success']:
                        results.append(
                            {"name": url[1],
                             "lowest_price": obj['data'][0]['price'] / 100})

        await asyncio.gather(*(get(url) for url in urls))
        # await session.close()
        return results

    def buy_item_with_name(self, item_name, price):
        if requests.get(
                f"https://market.csgo.com/api/v2/buy?key={self.api_key}&hash_name={item_name}&price={price}") \
                .json()['success']:
            return True
        else:
            return False

    def buy_item_with_id(self, id, price):
        if requests.get(f"https://market.csgo.com/api/v2/buy?key={self.api_key}&id={id}&price={price}").json()[
            'success']:
            return True
        else:
            return False

    def set_but_order(self, item_name, price, count=1):
        url = f"https://market.csgo.com/api/v2/set-order?key={self.api_key}&{item_name}&count={count}&price={price}"
        if requests.get(url).json()['success']:
            return True
        else:
            return False

    def get_url(self, item_name):
        url = f"https://market.csgo.com/api/v2/prices/class_instance/USD.json"
        items_json = requests.get(url).json()
        for key, value in items_json['items'].items():
            if value['market_hash_name'] == item_name:
                return f"https://market.csgo.com/item/{key.replace('_', '-')}-{item_name}&sd=asc"

    def sell_item(self, id="", price=1):
        url = f"https://market.csgo.com/api/v2/add-to-sale?key={self.api_key}&id={id}&price={price}&cur=USD"
        requests.get(url)

    def balance_account(self):
        url = f"https://market.csgo.com/api/v2/get-money?key={self.api_key}"
        res = requests.get(url).json()
        if res['success']:
            return res['money']
        else:
            return -1

    def get_orders_log(self):
        url = f"https://market.csgo.com/api/v2/get-orders-log?key={self.api_key}&page=0"
        res = requests.get(url).json()
        if res['success']:
            return res['orders']
        else:
            return -1

    def auto_buy(self, item_names):
        """price of permanent sale"""
        url = f"https://market.csgo.com/api/v2/prices/class_instance/USD.json"
        items_json = requests.get(url).json()
        res = []
        for value in items_json['items'].values():
            if value['market_hash_name'] in item_names:
                res.append({"lowest price": value['buy_order'], "name": value['market_hash_name']})

    def quantity_7d(self, item_name):
        url = f"https://market.csgo.com/api/v2/prices/class_instance/USD.json"
        items_json = requests.get(url).json()
        for value in items_json['items'].values():
            if value['market_hash_name'] == item_name:
                return value['popularity_7d']


def main(item_name):
    mcg = market_cs_go_parser("Tg55Ww91QLB9zU65AH2eer8YsiTqbBO")
    item_names = ['AK-47 | Jaguar (Field-Tested)', 'M4A4 | The Emperor (Well-Worn)',
                  '★ Navaja Knife | Safari Mesh (Battle-Scarred)']
    item_names2 = ['AK-47 | Jaguar (Field-Tested)', 'M4A4 | The Emperor (Well-Worn)',
                   '★ Navaja Knife | Safari Mesh (Battle-Scarred)']
    event_loop = asyncio.get_event_loop()
    prices1 = asyncio.gather(mcg.get_lowest_list_price_async(item_names))
    prices2 = asyncio.gather(mcg.get_lowest_list_price_async(item_names2))
    groups = asyncio.gather(prices1, prices2)
    res = event_loop.run_until_complete(groups)
    print(*res[0], *res[1], sep='\n')


if __name__ == '__main__':
    name = "P250 | Red Rock (Battle-Scarred)"
    name1 = 'SSG 08 | Blood in the Water (Minimal Wear)'
    main(name1)
    # main(name1)
