#!/usr/bin/env python3
# coding: utf-8
import decimal
import os

from flask import Flask
from flask import g
from flask import json
from flask import jsonify
from flask import render_template
from flask import request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from .data import query


class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super().default(o)


app = Flask(__name__)
app.json_encoder = JSONEncoder


def get_db():
    if not hasattr(g, 'db'):
        engine = create_engine(os.environ.get('DB_URL'))
        g.db = scoped_session(sessionmaker(bind=engine))
    return g.db


@app.route('/api')
@app.route('/')
def list_tickers():
    data = query.list_tickers(get_db())
    if request.path.startswith('/api'):
        return jsonify(data)
    else:
        return render_template('list_tickers.html', data=data)


@app.route('/api/<ticker>')
@app.route('/<ticker>')
def list_ticker_history(ticker):
    data = query.list_ticker_history(get_db(), ticker)
    if request.path.startswith('/api'):
        return jsonify(data)
    else:
        return render_template('list_ticker_history.html', data=data)


@app.route('/api/<ticker>/analytics')
@app.route('/<ticker>/analytics')
def list_ticker_analytics(ticker):
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    data = query.list_ticker_analytics(get_db(), ticker, date_from, date_to)
    if request.path.startswith('/api'):
        return jsonify(data)
    else:
        return render_template('list_ticker_analytics.html', data=data)


@app.route('/api/<ticker>/insider')
@app.route('/<ticker>/insider')
def list_insiders(ticker):
    data = query.list_insiders(get_db(), ticker)
    if request.path.startswith('/api'):
        return jsonify(data)
    else:
        return render_template('list_insiders.html', data=data)


@app.route('/api/<ticker>/insider/<insider>')
@app.route('/<ticker>/insider/<insider>')
def list_insider(ticker, insider):
    data = query.list_insider(get_db(), ticker, insider.upper())
    if request.path.startswith('/api'):
        return jsonify(data)
    else:
        return render_template('list_insiders.html', data=data)


@app.route('/api/<ticker>/delta')
@app.route('/<ticker>/delta')
def list_delta(ticker):
    data = query.list_delta(
        get_db(), ticker,
        float(request.args.get('value')), request.args.get('type')
    )
    if request.path.startswith('/api'):
        return jsonify(data)
    else:
        return render_template('list_delta.html', data=data)


def main():
    app.run()



if __name__ == '__main__':
    app.run(debug=True)
