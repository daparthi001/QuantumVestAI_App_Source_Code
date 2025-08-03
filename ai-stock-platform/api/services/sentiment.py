"""News sentiment analysis using a FinBERT model.

The real project uses the FinBERT transformer from HuggingFace.  Downloading
and executing that model would make the test environment very heavy, so this
module loads the model only when the required dependencies are available.  When
`transformers` or its model files are missing the service falls back to a
very small rule based heuristic so that unit tests can still exercise the API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

try:  # pragma: no cover - exercised conditionally during tests
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    import torch
    _TRANSFORMERS_AVAILABLE = True
except Exception:  # pragma: no cover - used when dependencies are missing
    AutoModelForSequenceClassification = AutoTokenizer = None  # type: ignore
    torch = None  # type: ignore
    _TRANSFORMERS_AVAILABLE = False

LABELS = ["negative", "neutral", "positive"]


@dataclass
class SentimentResult:
    label: str
    score: float


class SentimentService:
    """Analyse news text and return a sentiment score."""

    def __init__(self) -> None:
        if _TRANSFORMERS_AVAILABLE:
            try:  # pragma: no cover - model loading is expensive
                self.tokenizer = AutoTokenizer.from_pretrained(
                    "ProsusAI/finbert",
                    local_files_only=True,
                )
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    "ProsusAI/finbert",
                    local_files_only=True,
                )
            except Exception:
                # Model files not available; fall back to heuristic mode.
                self.tokenizer = None
                self.model = None
        else:
            self.tokenizer = None
            self.model = None

    # The method is kept synchronous for simplicity
    def analyse(self, text: str) -> SentimentResult:
        """Return the sentiment for ``text``.

        When the FinBERT model is available it is used, otherwise a very small
        heuristic based on keyword matching is employed.  This keeps the tests
        lightweight while exercising the same API surface.
        """

        if self.model and self.tokenizer:  # pragma: no cover - heavy path
            inputs = self.tokenizer(text, return_tensors="pt")
            with torch.no_grad():
                logits = self.model(**inputs).logits
                scores = torch.softmax(logits, dim=1)[0]
            idx = int(scores.argmax())
            return SentimentResult(LABELS[idx], float(scores[idx]))

        # Heuristic fallback
        lowered = text.lower()
        if any(word in lowered for word in ["gain", "positive", "up"]):
            return SentimentResult("positive", 0.0)
        if any(word in lowered for word in ["loss", "negative", "down"]):
            return SentimentResult("negative", 0.0)
        return SentimentResult("neutral", 0.0)
