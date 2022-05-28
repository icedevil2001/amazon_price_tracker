#!/bin/env python 
from typing import Dict, List
import requests
from user_agent import generate_user_agent, generate_navigator
# from pprint import pprint
from bs4 import BeautifulSoup as bs 
import re 
from time import sleep
# import json 
# from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd 
import logging
import schedule
import click 


URLS = [
        "https://fanatec.com/us-en/racing-wheels-wheel-bases/racing-wheels/podium-racing-wheel-f1",
        "https://fanatec.com/us-en/racing-wheels-wheel-bases/racing-wheels/podium-racing-wheel-formula-for-xbox-pc",
        "https://fanatec.com/us-en/racing-wheels-wheel-bases/wheel-bases/podium-wheel-base-dd2",
        "https://fanatec.com/us-en/racing-wheels-wheel-bases/wheel-bases/gran-turismo-dd-pro-wheel-base-8-nm",
        "https://fanatec.com/us-en/pedals/clubsport-pedals-v3-inverted"
    ]



def load_url(fpath: str='urls.txt') -> set:
    URLS = set()
    with open(fpath) as fh:
        for i in fh:
            URLS.add(i.strip())
    if len(URLS) == 0:
        logging.DEBUG('No URL found!')
        raise ValueError(f'Please add url to track:\nexample:\npyton scaper.py tracker-url -a "https://fanatec.com/us-en/pedals/clubsport-pedals-v3-inverted"')
    # logging.DEBUG(f'Total {len(URLS)} loaded.')
    return URLS

def load_csv(fpath: str = 'tracker.csv') -> pd.DataFrame:
    """Load csv file"""
    if Path(fpath).exists():
        logging.debug('loading dataframe')
        return pd.read_csv(fpath, index_col=0)
    logging.debug('Loading empty dataframe')
    return pd.DataFrame(columns=['product','price', 'availability'], index=['uname'])

def write_csv(df: pd.DataFrame, fpath: str = 'tracker.csv'):
    """Save dataframe as csv"""
    logging.debug(f'Written to file: {fpath}')
    df.to_csv(fpath)

def setup_logging():
    pass

class URLObj:
    def __init__(self,url, page_source) -> None:
        self.url = url.strip()
        self.soup = self.soupup(page_source)
        self.uname = self.url_name()
    
    def soupup(self, page_source):
        return bs(page_source, 'html.parser')
    
    def url_name(self):
        return self.url.split('/')[-1]

class Scraper(URLObj):
    def __init__(self, url, page_source):
        # self.soup = soup
        URLObj.__init__(self, url, page_source)
        self.product = self.get_product()
        self.price = self.get_price()
        self.availability = self.get_availability()
        
    def get_product(self):
        product_obj =  self.soup.find('h1', class_="product--title fancy-underline")
        return product_obj.text.strip()

    def get_price(self):
        price_obj =  self.soup.find('span', class_="price--content content--default")
        return price_obj.text.strip().split()[0]

    def get_availability(self):
        buybox = self.soup.find('div', class_="buybox--info")
        delivery = buybox.find('div', class_="product--delivery")
        delivery_info = delivery.find("p", class_="delivery--information")
        status =  delivery_info.find('span', class_=re.compile("delivery--text.*?"))
        return status.text.strip()

    def __repr__(self) -> str:
        return f'(product = {self.product} price = {self.price}, availability = {self.availability})'
    
    def to_json(self):
        return  {
            self.url: 
                {
                    "product": self.product,
                    "price": self.price, 
                    "availability": self.availability}
        }
    def to_df(self):
        d = {
                    'uname': self.uname,
                    'url': self.url,
                    "product": self.product,
                    "price": self.price, 
                    "availability": self.availability
                    }

        return pd.DataFrame.from_records([d], 
                    index='uname',
                    )



def run_scraper():
    URLS = load_url()
    df = load_csv()
    data =[]

    s = requests.Session()
    generate_user_agent(os=('mac', 'linux'))
    header = generate_navigator()
    for url in URLS:
        sleep(2)
        r = s.get(url, headers = header)
        if r.status_code != 200:
            logging.DEBUG(f'ERROR with loading page. Status code {r.status_code}')
            continue
            # raise ValueError(f'Something went wrong! Error code {r.status_code}')
        product_status = False
        scrape = Scraper(url, r.text)
        if scrape.uname in df.index:
            avail = df.loc[scrape.uname,'availability']
            if scrape.availability != avail:
                product_status = True
                logging.info(f'{scrape.product} change in availability:  {scrape.availability}')
                ## Update the availability and price in DB
                df.loc[scrape.uname,'availability'] = scrape.availability
                df.loc[scrape.uname,'price'] = scrape.price
                ## SEND EMAIL 
                ## OR send a msg to discord 
            else:
                ## if the same continue because in database
                logging.debug(f'{scrape.product}, No change in availability')
                continue
        else:
            logging.debug(f'Tracking new product: {scrape.product}')
            data.append(scrape.to_df())

    if len(df)==0:
        write_csv(pd.concat(data))
    else:
        write_csv(pd.concat(data + [df]))
    logging.info('Checking completed!')

# @click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("scraper.log"),
                logging.StreamHandler()
            ]
        )
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else: 
        logging.getLogger().setLevel(logging.INFO)


@cli.command()
@click.option('--add', '-a', multiple=True)
def tracker_url(add):
    """
    Add the product url to trac
    \b
    example: 
    \b
    python scraper tracker-url -a url-1 -a url-2 -a url-n
    """
    with open('urls.txt', 'a') as fh:
        for i in add:
            fh.write(i.strip()+"\n")
@cli.command('scrape')
@click.option('--hour', '-x', default=6, type=int, help='run every X hour. [6]')
def lets_scrape(hour):
    """Scraper """
    
    logging.info(f'Will run every {hour} hours')

    ## Run every 6 hours
    schedule.every(hour).hour.do(run_scraper)
    ## examples:
    # schedule.every(int(hour)).seconds.do(run_scraper) 
    # schedule.every(3).minutes.do(run_scraper)
    # schedule.every(3).hours.do(run_scraper)
    # schedule.every(3).days.do(run_scraper)
    # schedule.every(3).weeks.do(run_scraper)
    
    ## Run job every day at specific HH:MM and next HH:MM:SS
    # schedule.every().day.at("10:30").do(run_scraper)
    # schedule.run_pending()

    while True:
        schedule.run_pending()
        sleep(1) ## this allow you kill the job 
        # break


if __name__ == "__main__":
    cli()