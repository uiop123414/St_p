import csv
import json

import requests
from steam_market import steam_market
from abstract_parser import abstract_parser
import re
from bs4 import BeautifulSoup
from steampy import client
from threading import Thread
from service_progs import time_of_function


def get_id(s):
    id = None
    for script in s.find_all('script'):
        id_regex = re.search('Market_LoadOrderSpread\(([ 0-9]+)\)', script.text)
        if id_regex:
            id = id_regex.groups()[0].strip()
            break
    return id


class steam_parser(abstract_parser):

    def __init__(self, api_key: str = "1"):
        super().__init__()
        self.api_key = api_key
        self.account_st = client.SteamClient(self.api_key)
        # print(help(client.SteamClient))
        self.url_steam = "https://steamcommunity.com/market/listings/730/"

        # self.st_market = market.SteamMarket(market.Session())
        # super().__init__()

    # @time_of_function
    def get_lowest_price(self, item_name):
        url = "".join(("https://steamcommunity.com/market/priceoverview/?appid=730&market_hash_name=", item_name))
        # print(url)
        try:
            req = requests.get(url).json()
            return float(req['lowest_price'][1:])
        except KeyError:
            return None

    @time_of_function
    def auto_buy(self, item_name):
        html = requests.get("".join((self.url_steam, item_name))).text
        soup = BeautifulSoup(html, 'lxml')

        id = get_id(soup)
        if id:
            id_url = f"https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={id}&two_factor=0"
            # print(id_url)
            html = requests.get(id_url).json()
            html = html['buy_order_summary']
            soup = BeautifulSoup(html, 'lxml')

            return float(soup.select_one('span:last-child').text[1:])
        else:
            print("Could not get ID")

    # @time_of_function
    def get_lowest_price_new(self, item_name):
        return min(steam_market.get_csgo_item(item_name, count=self.get_count_of_items(item_name)).listings,
                   key=lambda x: x.price).price / 100

    def get_count_of_items(self, item_name):
        url = f"https://steamcommunity.com/market/listings/730/{item_name}"
        html = requests.get(url).text
        soup = BeautifulSoup(html, "lxml")
        num = soup.find("span", id='searchResults_total')
        return num.text

    def buy_item(self, item_name):
        pass

    def get_url(self, item_name):
        return f"https://steamcommunity.com/market/listings/730/{item_name}"

    def sell_item(self, item_name):
        pass

    def balance_account(self):
        pass

    @time_of_function
    def fun(self):
        url = "https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid=175880271"
        req = requests.get(url).json()
        print('highest_buy_order ', float(req['highest_buy_order']) / 100, ' lowest_sell_order ',
              float(req['lowest_sell_order']) / 100)

    @time_of_function
    def set_file(self):
        with open("key_values.csv", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=';')
            key = 0
            for row in reader:
                html = requests.get("".join((self.url_steam, row[1]))).text
                soup = BeautifulSoup(html, 'lxml')
                id = get_id(soup)
                if id is None:
                    raise ValueError
                with open('id_name.csv', 'a', newline='\n', encoding='utf-8') as csv_file:
                    writer = csv.writer(csv_file, delimiter=';')
                    writer.writerow((id, row[1]))
                    print(key)
                    key += 1


def main(item_name):
    st = steam_parser()
    th1 = Thread(target=st.get_permanent_sale_price, args=(item_name,))
    th1.start()
    th2 = Thread(target=st.get_lowest_price, args=(item_name,))
    th2.start()


def main1(item_name):  # 76100851D76E17F90FA82E87A4D39327
    # 35CFB4CA13123ED0EC2FB1F8ADEDE8A1
    print(steam_parser(api_key="35CFB4CA13123ED0EC2FB1F8ADEDE8A1").get_lowest_price(item_name))
    print(steam_parser(api_key="35CFB4CA13123ED0EC2FB1F8ADEDE8A1").auto_buy(item_name))


def main2():
    """For setting id-name file steam"""
    steam_parser(api_key="35CFB4CA13123ED0EC2FB1F8ADEDE8A1").set_file()


# 35CFB4CA13123ED0EC2FB1F8ADEDE8A1
if __name__ == '__main__':
    # name = "P250 | Red Rock (Battle-Scarred)"
    name = "SSG 08 | Blood in the Water (Minimal Wear)"
    # main(name)
    # main1(name)
    main2()
