import click 
from price_tracker.tracker import AmazonPrice 
from requests_html import HTMLSession, HTMLResponse


@click.group()
def cli():
    pass

@cli.command()
@click.argument('asin')
@click.argument('price')
@click.option('--update','-u', is_flag=True, help='Update price target')
@click.option('--add', '-a', is_flag=True, help='Add to target price target')
@click.option('--delete', '-d', is_flag=True, help='Delete price target')
def Watch_list(asin, price,update, add, delete):
    """Watch list"""
    watch = WatchList(asin, price)
    if update:
        watch.update_price()
    if add:
        watch.add()
    if delete:
        watch.delete()


@cli.command()
@click.option('--hour')
def run_watcher(hour= None):

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
        # r.html.render()
        sleep(1)
        am = AmazonPrice(r.html, amz_url) 
        # print(am.price_info_dict())
        am.add()
        if am.target_price(watch.targetprice):
            send_msg(
                title = 'Price below target',
                description = f'{am.title}\n\n**Price: {am.price}**',
                url = am.url
            )


if __name__ == "__main__":
    cli()