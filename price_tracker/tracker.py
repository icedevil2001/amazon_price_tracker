


from time import sleep
from requests_html import HTMLSession, HTMLResponse
from datetime import datetime as dt
# from bs4 import BeautifulSoup as bs
# from pprint import pprint
from price_tracker.database import (
    # WatchListTable, 
    db, TrackerTable, 
    PriceTable, 
    # WatchList
)
# import click 
import logging
# from discordhook import send_msg

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
        # self.html.render()
        self._render()

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

    def _render(self):
        for i in range(10):
            try:
                self.html.render()
                break_loop = True 
            except:
                break_loop = False 
            sleep(10)
            if break_loop:
                break 

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
    
