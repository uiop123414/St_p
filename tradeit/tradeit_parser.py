import re
from bs4 import BeautifulSoup
import requests


def main():
    url = "https://tradeback.io/ru/comparison#{%22app%22:2,%22services%22:[%22steamcommunity.com%22,%22cs.money%22],%22updated%22:[],%22categories%22:[[%22normal%22],[%22normal%22]],%22hold_time_range%22:[8,8],%22price%22:[[],[]],%22count%22:[[],[]],%22profit%22:[[],[]]}"
    req = requests.get(url)
    print(req.text)


if __name__ == '__main__':
    main()
