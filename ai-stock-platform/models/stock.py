"""Minimal stock models used in tests."""


class Stock:
    """Simplified Stock representation."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class WatchList(list):
    """Simple list-based watch list."""

    pass


__all__ = ["Stock", "WatchList"]

