# from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy import (
    Column, ForeignKey, Integer, Float,
    String, create_engine, update, delete, 
    insert, DateTime, 
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
from typing import List
from pathlib  import Path

Base = declarative_base()
ROOTDIR = Path(__file__).parents[1].resolve()
DBPATH = str(ROOTDIR / "database"/ "amazon.db")

engine = create_engine(f"sqlite:////{DBPATH}", echo=False)

class WatchListTable(Base):
    __tablename__ = "watchlist"

    asin = Column(String, primary_key = True )
    targetprice = Column(Float)

class TrackerTable(Base):
    """Parent Table, One to Many"""
    __tablename__ = "trackers"

    asin = Column(String, primary_key =True)
    title = Column(String)
    url = Column(String)
    pricetables = relationship(
        "PriceTable", 
        backref = 'tracker',
        # back_populates='trackers',
        cascade="all, delete, delete-orphan"
        )
    # def __repr__(self) -> str:
    #     return super().__repr__()

class PriceTable(Base):
    """Child table One to Many"""
    __tablename__ ='prices'

    id = Column(Integer, primary_key = True)
    datetime = Column(DateTime)
    price  = Column(Float)

    asin_id = Column(Integer, ForeignKey('trackers.asin'))
  
 

Base.metadata.create_all(engine)
LocalSession = sessionmaker(bind=engine)
db: Session = LocalSession()


class WatchList:
    """Add to watchlist"""
    def __init__(self, asin, target_price):
        self.asin = asin
        self.targetprice = target_price

    def query(self):
        return db.query(WatchListTable).filter(WatchListTable.asin == self.asin)

    def add(self):
        """Add price target"""
        res = self.query().first()
        if res is None:
            res = WatchListTable(**self.__dict__)
            db.add(res)
            db.commit()
    
    def delete(self):
        """Delete record"""
        self.query().delete()

    def update_price(self, price):
        """Update price target"""
        self.query().update({'targetprice': price})
        db.commit()

