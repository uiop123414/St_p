import csv
import sys
import os
import json
import asyncio
import webbrowser

import aiohttp
from service_progs import time_of_function


# Initialize connection pool


@time_of_function
async def get_prices(n, results, conn, urls):
    semaphore = asyncio.Semaphore(n)
    session = aiohttp.ClientSession(connector=conn)

    # heres the logic for the generator
    async def get(url):
        async with semaphore:
            async with session.get(url[0], ssl=False) as response:
                obj = json.loads(await response.read())
                if obj['success']:
                    # results.append(
                    #     {url[1]: url[0].split('=')[-1], 'highest_buy_order': float(obj['highest_buy_order']) / 100,
                    #      'lowest_sell_order': min(float(x[0]) for x in obj['sell_order_graph'])})
                    results.append(
                        {"name": url[1], "id": url[0].split('=')[-1],
                         'highest_buy_order': float(obj['highest_buy_order']) / 100,
                         'lowest_sell_order': float(obj['lowest_sell_order']) / 100 if (
                                 obj['lowest_sell_order'] is not None) else 0})

    await asyncio.gather(*(get(url) for url in urls))
    await session.close()


@time_of_function
def get_steam_prices(item_names):
    conn = aiohttp.TCPConnector(limit_per_host=100, limit=0, ttl_dns_cache=300)
    PARALLEL_REQUESTS = 100
    results = []

    ls = [(row[0], row[1]) for row in csv.reader(open('id_name.csv', encoding="utf-8"), delimiter=';')]
    urls = [(
        f"https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={i[0]}",
        i[1])
        for i in ls if i[1] in item_names]

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_prices(PARALLEL_REQUESTS, results, conn, urls))
    conn.close()

    # print(*results, sep='\n')
    return results


async def get_price_steam_async(item_names: list):
    conn = aiohttp.TCPConnector(limit_per_host=100, limit=0, ttl_dns_cache=300)
    PARALLEL_REQUESTS = 100
    semaphore = asyncio.Semaphore(PARALLEL_REQUESTS)
    session = aiohttp.ClientSession(connector=conn)
    results = []

    ls = [(row[0], row[1]) for row in csv.reader(open('id_name.csv', encoding="utf-8"), delimiter=';')]
    urls = [(
        f"https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={i[0]}",
        i[1])
        for i in ls if i[1] in item_names]

    async def get(url):
        async with semaphore:
            async with session.get(url[0]) as response:
                obj = json.loads(await response.read())
                if obj['success']:
                    # results.append(
                    #     {url[1]: url[0].split('=')[-1], 'highest_buy_order': float(obj['highest_buy_order']) / 100,
                    #      'lowest_sell_order': min(float(x[0]) for x in obj['sell_order_graph'])})
                    results.append(
                        {"name": url[1], "id": url[0].split('=')[-1],
                         'highest_buy_order': float(obj['highest_buy_order']) / 100,
                         'lowest_sell_order': float(obj['lowest_sell_order']) / 100 if (
                                 obj['lowest_sell_order'] is not None) else 0})

    await asyncio.gather(*(get(url) for url in urls))
    await session.close()
    # print(*results, sep='\n')
    return results


def get_lowest_sell_price(item_names):
    return [{"name": item['name'], "id": item['id'], 'lowest_price': item['lowest_sell_order']} for item in
            get_steam_prices(item_names)]


def get_highest_buy_price(item_names):
    return [{"name": item['name'], "id": item['id'], 'lowest_price': item['highest_buy_order']} for item in
            get_steam_prices(item_names)]


async def get_lowest_sell_price_async(item_names):
    return [{"name": item['name'], "id": item['id'], 'lowest_price': item['lowest_sell_order']} for item in
            await get_price_steam_async(item_names)]


async def get_highest_buy_price_async(item_names):
    return [{"name": item['name'], "id": item['id'], 'lowest_price': item['highest_buy_order']} for item in
            await get_price_steam_async(item_names)]


def id_name_file_create():
    with open('id_name.csv', 'r', encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            print(row[1])


if __name__ == '__main__':
    item_names = ['AK-47 | Jaguar (Field-Tested)', 'M4A4 | The Emperor (Well-Worn)',
                  '★ Navaja Knife | Safari Mesh (Battle-Scarred)']
    item_names2 = ['AK-47 | Jaguar (Field-Tested)', 'M4A4 | The Emperor (Well-Worn)',
                   '★ Navaja Knife | Safari Mesh (Battle-Scarred)']
    event_loop = asyncio.get_event_loop()

    prices1 = asyncio.gather(get_lowest_sell_price_async([item for item in item_names]))
    prices2 = asyncio.gather(get_highest_buy_price_async([item for item in item_names2]))

    all_groups = asyncio.gather(prices1, prices2)

    res = event_loop.run_until_complete(all_groups)
    print(*res[0], *res[1], sep='\n')
    print('*' * 50)
    # print([x for x in res if (x['highest_buy_order'] > x['lowest_sell_order'])])
    # webbrowser.open("https://steamcommunity.com/market/listings/730/" + str(
    #     *[list(x.keys())[0] for x in res if (x['highest_buy_order'] > x['lowest_sell_order'])]))
