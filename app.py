from email.policy import default
import click 
from price_tracker.tracker import AmazonPrice, BASE_URL
from requests_html import HTMLSession, HTMLResponse
from price_tracker.discordhook import send_msg
from time import sleep
import schedule
from price_tracker.database import (
    WatchList, 
    WatchListTable, 
    db, TrackerTable, 
    PriceTable
)


def amazon_price_scraper():

    session = HTMLSession()
    items = db.query(WatchListTable).all()
    if len(items) ==0:
        raise ValueError('Please add the watch list first')
    for watch in items:
        amz_url = (BASE_URL.format(watch.asin))
        r = session.get(amz_url)
        if r.status_code != 200:
            print(f'ERROR {r.status_code}')
            continue
        sleep(1)
        am = AmazonPrice(r.html, amz_url) 
        am.add()
        if am.target_price(watch.targetprice):
            send_msg(
                title = 'Price below target',
                description = f'{am.title}\n\n**Price: {am.price}**',
                url = am.url
            )

@click.group()
def cli():
    pass

@cli.command()
@click.argument('asin')
@click.argument('price')
@click.option('--update','-u', is_flag=True, help='Update price target')
@click.option('--add', '-a', is_flag=True, help='Add to target price target')
@click.option('--delete', '-d', is_flag=True, help='Delete price target')
@click.option('--show', '-s', is_flag=True, help='List db')
def watch_list(asin, price,update, add, delete, show):
    """Watch list"""
    watch = WatchList(asin, price)
    if update:
        watch.update_price()
    if add:
        watch.add()
    if delete:
        watch.delete()
    if show:
        results  = (
            db
            .query(TrackerTable)
            .join(WatchListTable)
            .filter(TrackerTable.asin == WatchListTable.asin)  
            # .all()      
        )

        for rec in results:
            # print(dir(rec))
            # title =  rec.tracker.title
            # print(f'Title:\t{title}')
            for k,v in rec.__dict__.items():
                if "_sa_instance_state" == k: continue
                
                print(f'{k}:\t{v}')
            print('='* 20)  


@cli.command()
@click.option('--interval', '-i', type=int, default=12, help = 'How offten to run the scraper - hourly. default: [1]')
# @click.option('--unit', '-u', default='days', 
#     type=click.Choice(['minutes', 'hours', 'days', 'weeks'], case_sensitive=False),
#     help = 'Unit of time, select from [minutes, hours, days, weeks]: default: [days]')
def run_watcher(interval: int ):
    # if not unit in ['minutes', 'hours', 'days', 'weeks']:
    #     raise ValueError(f'{unit} is not a valid chiichSelect')
    # click.echo(f'Settings: {unit} every {interval} ')
    # unit = unit.lower()

    schedule.every(interval).minutes.do(amazon_price_scraper)
    # print(schedule.get_jobs())
    print(schedule.get_jobs())
    while True:
        sleep(10)
        schedule.run_pending()
        


if __name__ == "__main__":
    cli()