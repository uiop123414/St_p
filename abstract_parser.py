
class abstract_parser:
    def __init__(self):
        pass

    def get_lowest_price(self, name):
        pass

    def buy_item(self, name):
        pass

    def sell_item(self, name):
        pass

    def get_url(self, item_name):
        pass

    def balance_account(self):
        pass

    def is_overstock(self ,item_name):
        pass

    def quantity_7d(self, item_name):
        pass

    def sale_on_week(self ,item_name):
        pass

    def auto_buy(self ,item_name):
        pass

    def get_class_name(self):
        return self.__class__