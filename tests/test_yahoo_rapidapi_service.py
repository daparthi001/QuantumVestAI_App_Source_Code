from services.yahoo_rapidapi_service import YahooRapidAPIService


class DummyResp:
    def __init__(self, data):
        self._data = data
    def raise_for_status(self):
        pass
    def json(self):
        return self._data


def test_no_api_key(monkeypatch):
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    assert YahooRapidAPIService.get_timeseries("IBM") is None


def test_success(monkeypatch):
    monkeypatch.setenv("RAPIDAPI_KEY", "test")
    monkeypatch.setenv("RAPIDAPI_HOST", "example.com")

    def fake_get(url, headers, params, timeout):
        assert url == "https://example.com/stock/v2/get-timeseries"
        assert headers["x-rapidapi-key"] == "test"
        assert params["symbol"] == "IBM"
        return DummyResp({"ok": True})

    monkeypatch.setattr("requests.get", fake_get)
    result = YahooRapidAPIService.get_timeseries("IBM")
    assert result == {"ok": True}


def test_request_failure(monkeypatch):
    """Service should return None when the request raises an error."""
    monkeypatch.setenv("RAPIDAPI_KEY", "test")

    def boom(*args, **kwargs):
        raise Exception("network down")

    monkeypatch.setattr("requests.get", boom)
    result = YahooRapidAPIService.get_timeseries("IBM")
    assert result is None
