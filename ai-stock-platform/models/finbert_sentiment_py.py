from transformers import pipeline

def get_finbert_sentiment(text: str) -> dict:
    """
    Get financial sentiment analysis for a given text using FinBERT.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary containing sentiment label and score
    """
    try:
        classifier = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone", top_k=None)
        result = classifier(text)
        
        # Process result
        if isinstance(result, list) and len(result) > 0:
            # Get the first result if list
            sentiment_data = result[0]
            
            # If result is a list of multiple sentiments, get the highest scoring one
            if isinstance(sentiment_data, list):
                sentiment_data = max(sentiment_data, key=lambda x: x['score'])
                
            return {
                "label": sentiment_data.get("label", "neutral"),
                "score": float(sentiment_data.get("score", 0.0))
            }
        else:
            return {"label": "neutral", "score": 0.5}
            
    except Exception as e:
        return {"label": "neutral", "score": 0.5, "error": str(e)}
