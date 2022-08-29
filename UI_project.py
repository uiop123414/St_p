import asyncio
import json
import tkinter
import webbrowser
from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog
from steam_parser import steam_parser
from buff163.buff163_parser import buff163_parser
from cs_money import cs_money_parser
from Swappgg.swapgg_parser import swapgg_parser
from market_cs_go.market_cs_go_parser import market_cs_go_parser
from Loot_farm.Loot_farm_parser import loot_farm_parser
from steam_parser import steam_parser_plus
from collections import defaultdict


class market_lowest:
    def __init__(self):
        self.steam = steam_parser.steam_parser()
        self.cs_money = cs_money_parser.csm_parser()
        self.Loot_farm = loot_farm_parser()
        self.swapgg = swapgg_parser("9f062b20-86d5-4317-a6b9-592d51db7610")
        self.market_cs_go = market_cs_go_parser("Tg55Ww91QLB9zU65AH2eer8YsiTqbBO")
        self.buff163 = buff163_parser("buff163/")

        self.func = {"buff163": self.buff163.get_lowest_price, "cs money": self.cs_money.get_lowest_price,
                     "Loot farm": self.Loot_farm.get_lowest_price
            , "market cs go": self.market_cs_go.get_lowest_price, "steam minimal price": self.steam.get_lowest_price
            , "steam permanent sale": self.steam.auto_buy, "swapgg": self.swapgg.get_lowest_price}

        self.url_func = {"buff163": self.buff163.get_url, "cs money": self.cs_money.get_url,
                         "Loot farm": self.Loot_farm.get_url
            , "market cs go": self.market_cs_go.get_url, "steam minimal price": self.steam.get_url,
                         "steam permanent sale": self.steam.get_url, "swapgg": self.swapgg.get_url}
        self.new_func = {"buff163": self.buff163.get_lowest_list_prices,
                         "cs money": self.cs_money.get_lowest_list_prices,
                         "Loot farm": self.Loot_farm.get_list_of_items
            , "steam minimal price": steam_parser_plus.get_lowest_sell_price
            , "steam permanent sale": steam_parser_plus.get_highest_buy_price}

        self.async_func = {
            "buff163 buy orders": self.buff163.get_list_highest_buy_orders_async,
            "buff163": self.buff163.get_list_lowest_prices_async,
            "steam minimal price": steam_parser_plus.get_lowest_sell_price_async
            , "steam permanent sale": steam_parser_plus.get_highest_buy_price_async
            , "market cs go": self.market_cs_go.get_lowest_list_price_async}

        with open("json_fee.json", 'r') as json_file:
            self.market_fee = json.load(json_file)

    def get_price(self, func_name1, item_name):
        return self.func[func_name1](item_name)

    def get_url(self, url_name, item_name):
        return self.url_func[url_name](item_name)


class market_window(tkinter.Tk):

    def __init__(self):
        super().__init__()
        self.event_loop = asyncio.get_event_loop()
        self.market_prices = market_lowest()

        self.markets = ["buff163 buy orders", "cs money", "Loot farm", "market cs go", "tradeit",
                        "steam minimal price", "steam permanent sale","buff163"]
        self.geometry('800x600')
        self.title("У нас было 2 пакетика ...")
        self.items = []

        self.value_inside1 = tkinter.StringVar(self)
        self.value_inside1.set("buff163")

        self.value_inside2 = tkinter.StringVar(self)
        self.value_inside2.set("cs money")

        self.dropdown_menus1 = self.create_dropdown_menus(self.value_inside1)
        self.dropdown_menus2 = self.create_dropdown_menus(self.value_inside2)

        self.btn = tkinter.Button(master=self, text='parse file', command=self.parse_button)
        self.btn1 = tkinter.Button(self, text="Get data", command=self.get_data)

        self.dropdown_menus1.place(x=0, y=0)
        self.btn.place(x=150, y=0)
        self.btn1.place(x=220, y=0)
        self.dropdown_menus2.place(x=300, y=0)

        self.Label_min_price = tkinter.Label(self, text="минимальная цена")
        self.Label_min_price.place(x=0, y=30)
        self.Label_max_price = tkinter.Label(self, text="Максимальная цена")
        self.Label_max_price.place(x=150, y=30)

        self.min_price_Entry = tkinter.Entry(self)
        self.min_price_Entry.place(x=0, y=50)
        self.max_price_Entry = tkinter.Entry(self)
        self.max_price_Entry.place(x=150, y=50)

        self.items_table = ttk.Treeview(self)
        self.create_table()
        self.items_table.pack(ipadx=0, ipady=600)
        self.items_table.place(x=0, y=200)

        self.items_table.bind('<ButtonRelease-1>', self.selectItem)

    def get_market_data(self):
        # print(self.value_inside1.get())
        # print(self.value_inside2.get())
        return self.value_inside1.get(), self.value_inside2.get()

    def selectItem(self, a):
        curItem = self.items_table.item(self.items_table.focus())
        md = self.get_market_data()
        webbrowser.open(self.market_prices.get_url(md[0], curItem['values'][0]), new=0)
        webbrowser.open(self.market_prices.get_url(md[1], curItem['values'][0]), new=0)

    def get_data(self):
        try:
            min_price = float(self.min_price_Entry.get())

        except (TypeError, ValueError):
            min_price = 0

        try:
            max_price = float(self.max_price_Entry.get())
        except (TypeError, ValueError):
            max_price = 10000
        if self.items:
            self.clear_table()
            self.insert_table(min_price, max_price)

    def subscribe(self):
        print(self.value_inside.get())

    def parse_button(self):
        file = filedialog.askopenfilename()
        with open(file, "r", encoding='utf-8') as f:
            for row in f:
                self.items.append(row)

    def create_dropdown_menus(self, v_in):
        return OptionMenu(self, v_in, *self.markets)

    def create_table(self):
        markets = self.get_market_data()
        self.items_table['columns'] = (
            'item_id', '1_market_price', '2_market_price', '1_to_2', '2_to_1')
        self.items_table.column("#0", width=0, stretch=NO)
        self.items_table.column("item_id", anchor=CENTER, width=160)
        self.items_table.column("1_market_price", anchor=CENTER, width=160)
        self.items_table.column("2_market_price", anchor=CENTER, width=160)
        self.items_table.column("1_to_2", anchor=CENTER, width=80)
        self.items_table.column("2_to_1", anchor=CENTER, width=80)

        self.items_table.heading("#0", text="", anchor=CENTER)
        self.items_table.heading("item_id", text="Name", anchor=CENTER)
        self.items_table.heading("1_market_price", text=markets[0], anchor=CENTER)
        self.items_table.heading("2_market_price", text=markets[1], anchor=CENTER)
        self.items_table.heading("1_to_2", text="1->2", anchor=CENTER)
        self.items_table.heading("2_to_1", text="2->1", anchor=CENTER)

    def insert_table(self, min_price, max_price):  ############################################

        markets = self.get_market_data()
        self.items_table.heading("1_market_price", text=markets[0], anchor=CENTER)  # Name of first market
        self.items_table.heading("2_market_price", text=markets[1], anchor=CENTER)

        self.clear_table()

        prices1 = asyncio.gather(
            self.market_prices.async_func[markets[0]]([item.replace('\n', '') for item in self.items]))
        prices2 = asyncio.gather(
            self.market_prices.async_func[markets[1]]([item.replace('\n', '') for item in self.items]))

        all_groups = asyncio.gather(prices1, prices2)  # async code getting prices

        res = self.event_loop.run_until_complete(all_groups)

        for price in res[0][0]:
            price["lowest_price_1"] = price.pop("lowest_price")
        for price in res[1][0]:
            price["lowest_price_2"] = price.pop("lowest_price")

        d = defaultdict(dict)
        for l in (res[0][0], res[1][0]):
            for elem in l:
                d[elem['name']].update(elem)
        prices3 = d.values()

        prices3 = sorted(prices3, key=lambda x: x['lowest_price_1'])
        for item, k in zip(prices3, range(len(prices3))):

            if max_price < item['lowest_price_2'] < min_price or max_price < max_price < item['lowest_price_1']:
                continue
            if item['lowest_price_2'] < min_price or max_price < item['lowest_price_1']:
                continue

            self.items_table.insert(parent='', index='end', iid=k, text='',
                                    values=(
                                        item['name'], '{:.2f}'.format(item['lowest_price_1']),
                                        '{:.2f}'.format(item['lowest_price_2'])
                                        ,
                                        '{:.2f}'.format(((item['lowest_price_2'] * (1 - self.market_prices.market_fee[
                                            markets[1]]) - item['lowest_price_1']) / item['lowest_price_1']) * 100),
                                        '{:.2f}'.format(((item['lowest_price_1'] * (1 - self.market_prices.market_fee[
                                            markets[0]]) - item['lowest_price_2']) / item['lowest_price_2']) * 100)))

    def create_table1(self):
        markets = self.get_market_data()
        self.items_table['columns'] = (
            'item_id', '1_market_price', '2_market_price', '1_to_2', '2_to_1')
        self.items_table.column("#0", width=0, stretch=NO)
        self.items_table.column("item_id", anchor=CENTER, width=160)
        self.items_table.column("1_market_price", anchor=CENTER, width=160)
        self.items_table.column("2_market_price", anchor=CENTER, width=160)
        self.items_table.column("1_to_2", anchor=CENTER, width=80)
        self.items_table.column("2_to_1", anchor=CENTER, width=80)

        self.items_table.heading("#0", text="", anchor=CENTER)
        self.items_table.heading("item_id", text="Name", anchor=CENTER)
        self.items_table.heading("1_market_price", text=markets[0], anchor=CENTER)
        self.items_table.heading("2_market_price", text=markets[1], anchor=CENTER)
        self.items_table.heading("1_to_2", text="1->2", anchor=CENTER)
        self.items_table.heading("2_to_1", text="2->1", anchor=CENTER)

    def clear_table(self):
        self.items_table.delete(*self.items_table.get_children())


def main():
    window = market_window()
    window.mainloop()


if __name__ == '__main__':
    main()
