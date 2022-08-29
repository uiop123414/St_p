import asyncio
import json

import aiohttp
import requests
from abstract_parser import abstract_parser


class swapgg_parser(abstract_parser):
    def __init__(self, api_key=""):
        self.session = requests.session()
        self.api_key = api_key
        url_ath = "https://market-api.swap.gg/v1/user/balance"
        if not requests.get(url=url_ath, headers={'Authorization': self.api_key}).json()[
                   'status'] == 'OK':
            raise Exception('Fail connection')
        super().__init__()

    def get_balance(self):
        url = "https://market-api.swap.gg/v1/user/balance"
        return \
            requests.get(url=url, headers={'Authorization': self.api_key}).json()['result'][
                'balance']

    def get_lowest_prices_and_url(self, item_names: list):
        url = 'https://market-api.swap.gg/v1/pricing/lowest?appId=730'
        res = self.session.get(url).json()
        items_ls = []
        # print(res['time'])
        if res['status'] == 'OK':
            for key, item in res['result'].items():
                print(key)
                if key in item_names:
                    items_ls.append({'price': item['price'] / 100, 'url': item['link']})
        return items_ls

    def get_lowest_price(self, item_names):
        return [item['price'] for item in self.get_lowest_prices_and_url(item_names)]

    def buy_item(self, name, price, quantity=1):
        url = "https://market-api.swap.gg/v1/buyorders"
        res = requests.get(url, headers={'Authorization': self.api_key, "Content-type": 'application/json'},
                           data={"items": [{"appId": "730", "marketName": name, "price": price, "quantity": quantity}]})
        if res.json()['status'] == 'OK':
            return True
        return False

    def sell_item(self, name):
        pass


# 1 657 485 900 669
def main(item_names):
    api_key = "9f062b20-86d5-4317-a6b9-592d51db7610"
    sw = swapgg_parser(api_key)
    print(sw.get_lowest_prices_and_url(item_names=item_names))


if __name__ == '__main__':
    name = ["★ Specialist Gloves | Emerald Web", "AK-47 | Neon Revolution (Minimal Wear)",
            'AK-47 | X-Ray (Battle-Scarred)']
    main(name)
