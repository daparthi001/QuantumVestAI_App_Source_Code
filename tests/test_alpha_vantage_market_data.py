from api.utils.market_data import MarketDataClient


class DummyResp:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


def test_get_data(monkeypatch):
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "demo")
    client = MarketDataClient()

    def fake_get(url, params, timeout):
        assert params["symbol"] == "IBM"
        return DummyResp({"foo": "bar"})

    monkeypatch.setattr("requests.get", fake_get)
    result = client.get_data("IBM")
    assert result["symbol"] == "IBM"
    assert result["data"] == {"foo": "bar"}
    assert result["source"] == "alphavantage"


def test_get_latest_price(monkeypatch):
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "demo")
    data = {"Time Series (1min)": {"2021-01-01 00:00:00": {"4. close": "123.45"}}}
    monkeypatch.setattr("requests.get", lambda url, params, timeout: DummyResp(data))
    client = MarketDataClient()
    price = client.get_latest_price("IBM")
    assert price == 123.45


def test_get_historical(monkeypatch):
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "demo")
    data = {
        "Time Series (Daily)": {
            "2021-01-01": {"close": "1"},
            "2021-01-02": {"close": "2"},
            "2021-01-03": {"close": "3"},
        }
    }
    monkeypatch.setattr("requests.get", lambda url, params, timeout: DummyResp(data))
    client = MarketDataClient()
    hist = client.get_historical("IBM", "2021-01-02", "2021-01-03")
    assert hist == [
        {"date": "2021-01-02", "close": "2"},
        {"date": "2021-01-03", "close": "3"},
    ]
