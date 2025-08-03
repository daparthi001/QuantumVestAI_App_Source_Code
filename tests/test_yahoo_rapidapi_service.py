from services.yahoo_rapidapi_service import YahooRapidAPIService


class DummyResp:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


def setup_function():
    YahooRapidAPIService._cache.clear()


def test_no_api_key(monkeypatch):
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    assert YahooRapidAPIService.get_live_price("IBM") is None


def test_fetch_and_cache(monkeypatch):
    monkeypatch.setenv("RAPIDAPI_KEY", "test")
    monkeypatch.setenv("RAPIDAPI_HOST", "example.com")

    data = {
        "quoteResponse": {
            "result": [
                {
                    "regularMarketPrice": 101.0,
                    "regularMarketChange": 1.5,
                    "regularMarketChangePercent": 1.49,
                }
            ]
        }
    }

    calls = {"count": 0}

    def fake_get(url, headers, params, timeout):
        calls["count"] += 1
        assert url == "https://example.com/market/v2/get-quotes"
        assert headers["x-rapidapi-key"] == "test"
        assert params["symbols"] == "IBM"
        return DummyResp(data)

    monkeypatch.setattr("requests.get", fake_get)
    result = YahooRapidAPIService.get_live_price("IBM")
    assert result == {
        "price": 101.0,
        "change": 1.5,
        "percent_change": 1.49,
    }

    # Second call should hit the cache
    result2 = YahooRapidAPIService.get_live_price("IBM")
    assert result2 == result
    assert calls["count"] == 1
