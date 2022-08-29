import asyncio
import json

import aiohttp
import requests
from abstract_parser import abstract_parser
from service_progs import time_of_function


class loot_farm_parser(abstract_parser):
    def __init__(self):
        super(loot_farm_parser, self).__init__()

        self.conn = aiohttp.TCPConnector(limit_per_host=100, limit=0, ttl_dns_cache=300)
        self.quality = {
            "Field-Tested)": "FT",
            "Factory New)": "FN",
            "Minimal Wear)": "MW",
            "Battle-Scared)": "BS"
        }

    # @time_of_function
    # def get_lowest_price(self, item_name):
    #     """:return only price"""
    #     url = "https://loot.farm/fullprice.json"
    #     res = requests.get(url)
    #     for item in res.json():
    #         if item_name in item['name']:
    #             return item['price'] / 100

    def get_list_of_items(self, item_names):
        url = "https://loot.farm/fullprice.json"

        res = requests.get(url).json()
        print(res[0])
        result = []
        for item_name in item_names:
            result.append(list(filter(lambda x: x['name'] == item_name, res)))
        print(*result,sep='\n')

    def get_url(self, item_name):
        return "https://loot.farm"

    async def get_lowest_price(self, item_names):
        PARALLEL_REQUESTS = 100
        semaphore = asyncio.Semaphore(PARALLEL_REQUESTS)
        session = aiohttp.ClientSession(connector=self.conn)
        url = "https://loot.farm/botsInventory_730.json"
        results = []

        # heres the logic for the generator
        async def get(name, quality):
            async with semaphore:
                async with session.get(url) as response:
                    obj = json.loads(await response.read())
                    for key, value in obj['result'].items():
                        if value['n'] == name and value['e'] == self.quality[quality]:
                            results.append(
                                {"name": value['n'],
                                 "lowest_price": value['p'] / 100,
                                 "key": key})

        await asyncio.gather(
            *(get(name, quality) for name, quality in (item_name.split(' (') for item_name in item_names)))
        await session.close()
        return results

    def get_lowest_price1(self, item_names: list):
        url = "https://loot.farm/botsInventory_730.json"

        req = requests.get(url).json()
        for key, value in req['result'].items():
            if value['n'] in item_names:
                print("key = ", key, " name ", value['n'], " price", value['p'] / 100, " quality", value['e'])

    @time_of_function
    def get_list_lowest_price(self, item_names: list):
        event_loop = asyncio.get_event_loop()
        task = asyncio.gather(self.get_lowest_price(item_names))
        res = event_loop.run_until_complete(task)
        return res


def main(item_name):
    print(loot_farm_parser().get_lowest_price([item_name]))
    print(loot_farm_parser().get_list_of_items(item_name))
    print(loot_farm_parser().get_url(item_name))


if __name__ == '__main__':
    item_names = ['M4A4 | Bullet Rain (Minimal Wear)', 'AWP | Fade (Factory New)',
                  'AK-47 | Fire Serpent (Minimal Wear)', 'Karambit | Doppler (Factory New)']
    lt =loot_farm_parser()
    lt.get_list_of_items(item_names)
    print(*lt.get_list_lowest_price(item_names),sep='\n')