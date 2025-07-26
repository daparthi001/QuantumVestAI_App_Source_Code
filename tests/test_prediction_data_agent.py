from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from api.services.prediction_data_agent import PredictionDataAgent
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime

TestBase = declarative_base()
# Mark the base class so PyTest does not treat it as a test
TestBase.__test__ = False


class Stock(TestBase):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True)
    ticker = Column(String)
    name = Column(String)
    exchange = Column(String)
    last_price = Column(Float)
    last_updated = Column(DateTime)


class StockPrice(TestBase):
    __tablename__ = "stock_prices"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer)
    date = Column(DateTime)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adjusted_close = Column(Float)
    volume = Column(Integer)


def test_prediction_data_agent(monkeypatch):
    # Set up in-memory database
    engine = create_engine("sqlite:///:memory:")
    TestBase.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Fake yfinance download
    def fake_download(symbol, period="1d", interval="1d", progress=False):
        return pd.DataFrame({
            "Date": [datetime(2024, 1, 1)],
            "Open": [100.0],
            "High": [110.0],
            "Low": [90.0],
            "Close": [105.0],
            "Adj Close": [105.0],
            "Volume": [1000],
        })

    monkeypatch.setattr("api.services.prediction_data_agent.yf.download", fake_download)

    agent = PredictionDataAgent(
        session,
        ["TEST"],
        stock_model=Stock,
        price_model=StockPrice,
    )
    agent.update_symbols(days=1)

    assert session.query(Stock).count() == 1
    assert session.query(StockPrice).count() == 1

