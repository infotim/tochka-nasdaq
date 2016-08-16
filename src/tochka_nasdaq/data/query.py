# coding: utf-8
import functools

from sqlalchemy.sql import text

from .models import Trade
from .models import Quote


def as_dict(obj):
    out = {}
    keys = [i for i in dir(obj) if not i[0] == '_' and i != 'metadata']
    for key in keys:
        out[key] = getattr(obj, key)
    return out


def as_dicts(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return [as_dict(i) for i in func(*args, **kwargs)]
    return wrapper


def list_tickers(db):
    data = db.query(Quote)\
        .group_by('ticker')\
        .with_entities(Quote.ticker)\
        .all()
    return [i[0] for i in data]


@as_dicts
def list_ticker_history(db, ticker):
    data = db.query(Quote)\
        .filter_by(ticker=ticker)\
        .order_by(Quote.date.desc())\
        .all()
    return data


def list_ticker_analytics(db, ticker, date_from, date_to):
    f = db.query(Quote).filter_by(ticker=ticker, date=date_from).one()
    t = db.query(Quote).filter_by(ticker=ticker, date=date_to).one()
    return [{
        'ticker': ticker,
        'date_from': f.date,
        'date_to': t.date,
        'diff_open': t.open - f.open,
        'diff_high': t.high - f.high,
        'diff_low': t.low - f.low,
        'diff_close': t.close - f.close,
        'diff_volume': t.volume - f.volume,
    }]


@as_dicts
def list_insiders(db, ticker):
    data = db.query(Trade)\
        .filter_by(ticker=ticker)\
        .order_by(Trade.date.desc())\
        .all()
    return data


@as_dicts
def list_insider(db, ticker, name):
    data = db.query(Trade)\
        .filter_by(ticker=ticker, insider=name)\
        .order_by(Trade.date.desc())\
        .all()
    return data


def list_delta(db, ticker, value, type):
    query_template = """
        WITH RECURSIVE r AS (
            (
                SELECT min(date) as date_from, 0::numeric FROM quote WHERE ticker = :ticker
            )
            UNION ALL
            (
                SELECT date, diff FROM (
                    SELECT date, {type} - first_value({type}) OVER (ORDER BY date) AS diff
                    FROM quote
                    JOIN r ON (r.date_from <= date)
                    WHERE ticker = :ticker
                    ORDER BY date
                ) AS dt
                WHERE abs(dt.diff) > :value
                LIMIT 1
            )
        )
        SELECT * FROM r;
    """  # noqa
    query_raw = query_template.format(type=type)
    data = list(
        db.execute(text(query_raw), {'ticker': ticker, 'value': value})
    )
    out = []
    if len(data) > 1:
        for i in range(1, len(data)):
            out.append({
                'ticker': ticker,
                'date_from': data[i-1][0],
                'date_to': data[i][0],
                'diff': data[i][1]
            })
    return out
