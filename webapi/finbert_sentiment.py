from transformers import pipeline

def get_finbert_sentiment(text: str) -> dict:
    try:
        classifier = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone", top_k=None)
        result = classifier(text)
        return result[0] if isinstance(result, list) else result
    except Exception as e:
        return {"label": "neutral", "score": 0.0, "error": str(e)}
