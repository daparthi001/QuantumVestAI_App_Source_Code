class SentimentRecord:
    """Simplified sentiment record used for tests."""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    async def save(self) -> None:
        """Persist the record (no-op in tests)."""
        pass
