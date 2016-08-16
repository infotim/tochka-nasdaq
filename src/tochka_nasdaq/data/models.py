# coding: utf-8
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session

Base = declarative_base()


def setup_db(engine):
    Base.metadata.create_all(bind=engine)


class Quote(Base):
    __tablename__ = 'quote'

    date = Column(Date, primary_key=True)
    ticker = Column(String, primary_key=True)
    open = Column(Numeric(10, 4))
    high = Column(Numeric(10, 4))
    low = Column(Numeric(10, 4))
    close = Column(Numeric(10, 4))
    volume = Column(Integer)


class Trade(Base):
    __tablename__ = 'trade'

    uuid = Column(postgresql.UUID, primary_key=True)
    date = Column(Date, index=True)
    insider = Column(String, index=True)
    ticker = Column(String)
    relation = Column(String)
    transaction = Column(String)
    owner = Column(String)
    traded = Column(Integer)
    held = Column(Integer)
    price = Column(Numeric(10, 4))
