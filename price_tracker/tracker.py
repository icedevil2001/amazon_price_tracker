


from time import sleep
from requests_html import HTMLSession, HTMLResponse
from datetime import datetime as dt
# from bs4 import BeautifulSoup as bs
from pprint import pprint
from database import (
    WatchListTable, 
    db, TrackerTable, 
    PriceTable, WatchList
)
import click 
import logging
from discordhook import send_msg

logger = logging.getLogger(__name__) 

BASE_URL = 'https://www.amazon.com/dp/{}'

HEADER = {
    'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36'
}

class AmazonPrice:
    def __init__(self, html: HTMLResponse, amazon_url: str):
        self.html =  html
        self.url = amazon_url
        self.dt = dt.now()
        self.html.render()

    @property
    def price(self):
        return float(self.html.xpath('//*[@id="corePrice_feature_div"]/div/span/span[1]',first=True).text.strip()[1:])

    @property
    def title(self):
        return self.html.xpath('//*[@id="productTitle"]', first=True).text.strip()
   
    @property
    def asin(self):
        result = self.html.xpath('//*[@id="deliveryBlockSelectAsin"]',first=True)
        return result.attrs['value']

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(\ntitle = {self.title}\nprice = {self.price}\n)'

    def product_info_dict(self):
        return {
            'asin': self.asin,
            "url": self.url,
            'title': self.title,
        }
    
    def price_info_dict(self):
        return {
            "datetime": self.dt,
            'price': self.price,
            'asin_id': self.asin,
            }

    def target_price(self, target_price):
        return  target_price >= self.price

    def price_diff(self, target_price):
        return 1 - (target_price/self.price)

    def _query(self):
        return db.query(TrackerTable).filter(TrackerTable.asin == self.asin)

    def add(self):
        """Add price target"""
        product = self._query().first()
        if product is None:
            product = TrackerTable(**self.product_info_dict())
        # product.prices.append(**self.price_info_dict())
            db.add(product)
        db.add(PriceTable(**self.price_info_dict()))
        db.commit()
    
    def delete(self):
        """Delete record"""
        self._query().delete()

    def update_price(self, price):
        """Update price target"""
        self._query().update({'targetprice': price})
        db.commit()
    


# @click.group()
# def cli():
#     pass

# @cli.command()
# @click.argument('asin')
# @click.argument('price')
# @click.option('--update','-u', is_flag=True, help='Update price target')
# @click.option('--add', '-a', is_flag=True, help='Add to target price target')
# @click.option('--delete', '-d', is_flag=True, help='Delete price target')
# def Watch_list(asin, price,update, add, delete):
#     """Watch list"""
#     watch = WatchList(asin, price)
#     if update:
#         watch.update_price()
#     if add:
#         watch.add()
#     if delete:
#         watch.delete()


# @cli.command()
# @click.option('--hour')
# def run_watcher(hour= None):

#     session = HTMLSession()
#     items = db.query(WatchListTable).all()
#     if len(items) ==0:
#         raise ValueError('Please add the watch list first')
#     for watch in items:
#         amz_url = (BASE_URL.format(watch.asin))
#         r = session.get(amz_url)
#         if r.status_code != 200:
#             print(f'ERROR {r.status_code}')
#             continue
#         # r.html.render()
#         sleep(1)
#         am = AmazonPrice(r.html, amz_url) 
#         # print(am.price_info_dict())
#         am.add()
#         if am.target_price(watch.targetprice):
#             send_msg(
#                 title = 'Price below target',
#                 description = f'{am.title}\n\n**Price: {am.price}**',
#                 url = am.url
#             )


# if __name__ == "__main__":
#     cli()

# session = HTMLSession()
# for url in URLS:
#     sleep(2)
#     r = session.get(url)
#     if r.status_code != 200:
#         print(r.status_code)
#     amazon = AmazonPrice(r.html)
#     pprint(amazon.product_info_dict())
#     add_price(db, amazon)
#     # tracker = Tracker(**amazon)



