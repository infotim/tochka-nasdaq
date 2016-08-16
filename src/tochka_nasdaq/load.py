#!/usr/bin/python3
# coding: utf-8

import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import os

import lxml.html as et
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from .data.models import Trade
from .data.models import Quote
from .data.models import setup_db
from .data.parse import parse_quotes
from .data.parse import parse_trades
from .util import uuid5


class Crawler(object):
    def __init__(self, loop, tickers, max_threads):
        self.loop = loop
        self.loop.set_default_executor(ThreadPoolExecutor(max_threads))
        self.max_threads = max_threads
        self.tickers = tickers
        self.queue = asyncio.Queue()

        self.result = {i: {'quotes': [], 'trades': []} for i in tickers}

    async def crawl(self):
        for ticker in self.tickers:
            for job in self.start_jobs(ticker):
                await self.queue.put(job)

        workers = [
            self.loop.create_task(self.work())
            for _ in range(self.max_threads)
        ]

        await self.queue.join()

        for worker in workers:
            worker.cancel()

    def start_jobs(self, ticker):
        yield (
            ticker,
            'http://www.nasdaq.com/symbol/{}/historical'.format(ticker),
            parse_quotes
        )
        yield (
            ticker,
            'http://www.nasdaq.com/symbol/{}/insider-trades?page=1'.format(ticker),  # noqa
            parse_trades
        )

    async def work(self):
        while True:
            ticker, url, parse_func = await self.queue.get()
            data, kind, urls = await self.loop.run_in_executor(
                None, parse_func, url
            )
            self.result[ticker][kind].extend(data)
            for url in urls:
                await self.queue.put((ticker, url, parse_func))

            self.queue.task_done()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('--threads', type=int, default=10)
    parser.add_argument('--verbose', '-v', action='store_true', default=False)
    args = parser.parse_args()

    with open(args.filename) as fh:
        tickers = [i.strip().lower() for i in fh.readlines()]

    loop = asyncio.get_event_loop()
    crawler = Crawler(loop, tickers, args.threads)

    engine = create_engine(os.environ.get('DB_URL'), echo=args.verbose)
    setup_db(engine)

    loop.run_until_complete(crawler.crawl())

    db = scoped_session(sessionmaker(bind=engine))

    for ticker, data in crawler.result.items():
        for row in data['quotes']:
            try:
                row['date'] = datetime.strptime(row['date'], '%m/%d/%Y')
            except ValueError:
                continue
            row['ticker'] = ticker
            row['volume'] = int(row['volume'].replace(',', ''))
            for k in ('open', 'close', 'high', 'low'):
                row[k] = float(row[k])

            item = Quote(**row)
            db.add(item)
        db.commit()

        for row in data['trades']:
            try:
                row['date'] = datetime.strptime(row['date'], '%m/%d/%Y')
            except ValueError:
                continue
            row['ticker'] = ticker
            row['uuid'] = uuid5([row[i] for i in sorted(row)]).hex
            for k in ('traded', 'held'):
                row[k] = int(row[k].replace(',', ''))
            try:
                row['price'] = float(row['price'])
            except ValueError:
                row['price'] = None

            item = Trade(**row)
            db.add(item)
        db.commit()


if __name__ == '__main__':
    main()
