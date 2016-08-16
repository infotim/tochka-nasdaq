# coding: utf-8

import asyncio
from concurrent.futures import Future
import urllib.parse as urlparse

import lxml.html as et

from ..util import grouper


def parse_quotes(url):
    html = et.parse(url)

    cols = html.xpath(
        "//div[@id='historicalContainer']//table/tbody/tr/td/text()"
    )
    cols = [i.strip() for i in cols]

    quotes = []
    fields = ('date', 'open', 'high', 'low', 'close', 'volume')
    for row in grouper(cols, 6):
        quotes.append(dict(zip(fields, row)))
    return (quotes, 'quotes', [])


def parse_trades(url, max_pages=10):
    html = et.parse(url)

    cols = html.xpath("//div[@class='genTable']/table/tr/td")
    cols = [i.text_content() for i in cols]

    trades = []
    urls = []
    fields = (
        'insider', 'relation', 'date', 'transaction',
        'owner', 'traded', 'price', 'held'
    )

    current_page = int(qs_dict(url).get('page', 1))
    if current_page == 1:
        last = html.xpath(
            "//a[@id='quotes_content_left_lb_LastPage']/@href"
        )[0]
        qs = qs_dict(last)

        last_page = int(qs.get('page', 1))
        for i in range(2, min(last_page, max_pages) + 1):
            urls.append(urlparse.urlunparse(
                urlparse.urlparse(url)._replace(query='page={}'.format(i))
            ))

    for row in grouper(cols, 8):
        trades.append(dict(zip(fields, row)))
    return (trades, 'trades', urls)


def qs_dict(url):
    return dict(urlparse.parse_qsl(urlparse.urlparse(url).query))
