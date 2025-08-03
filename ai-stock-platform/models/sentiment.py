"""Minimal sentiment model used in tests."""


class SentimentRecord:
    """Simplified sentiment record used for tests."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def save(self) -> None:  # pragma: no cover - placeholder
        pass


__all__ = ["SentimentRecord"]

