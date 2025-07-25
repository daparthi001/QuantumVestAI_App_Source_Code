import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
try:
    import torch
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    torch = None  # type: ignore
    logging.getLogger("api").warning(
        "PyTorch not available, FinBertSentiment will use mock predictions"
    )
from transformers import AutoModelForSequenceClassification, AutoTokenizer

logger = logging.getLogger("api")

class FinBertSentiment:
    """
    Financial text sentiment analysis using FinBERT.
    
    FinBERT is a pre-trained NLP model to analyze sentiment of financial text.
    It is based on BERT and fine-tuned with financial text.
    """
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        """
        Initialize FinBERT sentiment model.
        
        Args:
            model_name: Pre-trained model name or path
        """
        self.model_name = model_name
        if torch is not None:
            self.device = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )
        else:
            self.device = "cpu"
        self.tokenizer = None
        self.model = None
        self.labels = ["negative", "neutral", "positive"]
        self.loaded = False
        self.cache_dir = Path("models/finbert")
        
        # Load model on first use to avoid unnecessary memory usage
    
    def _load_model(self) -> None:
        """Load model and tokenizer if not already loaded."""
        if not self.loaded:
            if torch is None:
                logger.warning(
                    "PyTorch not installed. FinBERT model cannot be loaded; using mock predictions"
                )
                return
            try:
                logger.info(f"Loading FinBERT model from {self.model_name}")
                
                # Create cache directory if it doesn't exist
                os.makedirs(self.cache_dir, exist_ok=True)
                
                # Load tokenizer and model
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name, 
                    cache_dir=self.cache_dir
                )
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name, 
                    cache_dir=self.cache_dir
                )
                self.model.to(self.device)
                self.model.eval()
                self.loaded = True
                
                logger.info("FinBERT model loaded successfully")
            except Exception as e:
                logger.exception(f"Error loading FinBERT model: {e}")
                # Fall back to mock predictions if model can't be loaded
                self.loaded = False
    
    def predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Predict sentiment for a list of financial texts.
        
        Args:
            texts: List of financial texts to analyze
            
        Returns:
            List of dictionaries with sentiment analysis results
        """
        # If no texts, return empty list
        if not texts:
            return []
        
        # Try to load model if not loaded
        if not self.loaded:
            self._load_model()
        
        results = []
        
        try:
            # If model loaded successfully, use it for prediction
            if self.loaded:
                # Use batch processing for efficiency
                for i in range(0, len(texts), 8):  # Process in batches of 8
                    batch_texts = texts[i:i+8]
                    batch_results = self._predict_batch(batch_texts)
                    results.extend(batch_results)
            else:
                # Fall back to mock predictions if model can't be loaded
                results = self._mock_predictions(texts)
                
        except Exception as e:
            logger.exception(f"Error in FinBERT prediction: {e}")
            # Fall back to mock predictions
            results = self._mock_predictions(texts)
        
        return results
    
    def _predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Predict sentiment for a batch of texts.
        
        Args:
            texts: List of financial texts to analyze
            
        Returns:
            List of dictionaries with sentiment analysis results
        """
        results = []
        if torch is None or self.model is None or self.tokenizer is None:
            return self._mock_predictions(texts)

        # Tokenize texts
        encoded_input = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )

        # Move inputs to the same device as model
        encoded_input = {k: v.to(self.device) for k, v in encoded_input.items()}

        # Predict
        with torch.no_grad():
            outputs = self.model(**encoded_input)
            scores = torch.nn.functional.softmax(outputs.logits, dim=1)
            scores = scores.detach().cpu().numpy()
        
        # Process results
        for i, text in enumerate(texts):
            label_id = scores[i].argmax()
            sentiment = self.labels[label_id]
            confidence = float(scores[i][label_id])
            
            # Create result dictionary
            result = {
                "text": text[:100] + "..." if len(text) > 100 else text,
                "sentiment": sentiment,
                "confidence": round(confidence, 4),
                "scores": {
                    "negative": round(float(scores[i][0]), 4),
                    "neutral": round(float(scores[i][1]), 4),
                    "positive": round(float(scores[i][2]), 4)
                }
            }
            
            results.append(result)
        
        return results
    
    def _mock_predictions(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Generate mock sentiment predictions when model is unavailable.
        
        Args:
            texts: List of financial texts to analyze
            
        Returns:
            List of dictionaries with mock sentiment analysis results
        """
        results = []
        
        for text in texts:
            # Determine mock sentiment based on text keywords
            if not text or len(text) < 5:
                sentiment = "neutral"
                scores = {"negative": 0.1, "neutral": 0.8, "positive": 0.1}
            elif any(kw in text.lower() for kw in ["up", "rise", "gain", "grow", "positive", "bull", "higher"]):
                sentiment = "positive"
                scores = {"negative": 0.1, "neutral": 0.2, "positive": 0.7}
            elif any(kw in text.lower() for kw in ["down", "fall", "drop", "decline", "negative", "bear", "lower"]):
                sentiment = "negative"
                scores = {"negative": 0.7, "neutral": 0.2, "positive": 0.1}
            else:
                sentiment = "neutral"
                scores = {"negative": 0.2, "neutral": 0.6, "positive": 0.2}
            
            # Create result dictionary
            result = {
                "text": text[:100] + "..." if len(text) > 100 else text,
                "sentiment": sentiment,
                "confidence": scores[sentiment],
                "scores": scores,
                "mock": True  # Indicate this is a mock prediction
            }
            
            results.append(result)
        
        return results
    
    def analyze_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment of news articles.
        
        Args:
            news_items: List of news articles containing at least 'title' and 'description'
            
        Returns:
            List of news items with sentiment analysis added
        """
        texts = []
        
        # Prepare texts for analysis
        for item in news_items:
            # Combine title and description for better context
            text = item.get('title', '')
            if item.get('description'):
                text += " - " + item['description']
            texts.append(text)
        
        # Get sentiment predictions
        sentiment_results = self.predict(texts)
        
        # Add sentiment to news items
        result_items = []
        for i, item in enumerate(news_items):
            if i < len(sentiment_results):
                enriched_item = item.copy()
                enriched_item['sentiment'] = sentiment_results[i]['sentiment']
                enriched_item['sentiment_scores'] = sentiment_results[i]['scores']
                enriched_item['sentiment_confidence'] = sentiment_results[i]['confidence']
                result_items.append(enriched_item)
        
        return result_items
    
    def get_stock_sentiment_summary(
        self, news_items: List[Dict[str, Any]], lookback_days: int = 7
    ) -> Dict[str, Any]:
        """
        Generate sentiment summary for a stock based on recent news.
        
        Args:
            news_items: List of news articles with sentiment analysis
            lookback_days: Number of days to consider for recent news
            
        Returns:
            Dictionary with sentiment summary
        """
        # Filter recent news
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)
        
        recent_news = []
        for item in news_items:
            # Parse date and filter
            try:
                news_date = datetime.strptime(item.get('published_at', ''), "%Y-%m-%dT%H:%M:%SZ")
                if news_date >= cutoff_date:
                    recent_news.append(item)
            except (ValueError, TypeError):
                # If date can't be parsed, include the news anyway
                recent_news.append(item)
        
        # Count sentiment distribution
        counts = {"positive": 0, "neutral": 0, "negative": 0}
        for item in recent_news:
            sentiment = item.get('sentiment', 'neutral')
            counts[sentiment] += 1
        
        total = sum(counts.values()) or 1  # Avoid division by zero
        
        # Calculate sentiment score (-100 to +100)
        sentiment_score = int(
            ((counts["positive"] - counts["negative"]) / total) * 100
        )
        
        # Determine sentiment category
        if sentiment_score >= 50:
            category = "Very Bullish"
        elif sentiment_score >= 20:
            category = "Bullish"
        elif sentiment_score > -20:
            category = "Neutral"
        elif sentiment_score > -50:
            category = "Bearish"
        else:
            category = "Very Bearish"
        
        # Generate a summary text
        if total == 0:
            summary = "No recent news found for this stock."
        else:
            summary = (
                f"Based on {total} recent news articles, sentiment is {category.lower()} "
                f"with {counts['positive']} positive, {counts['neutral']} neutral, and "
                f"{counts['negative']} negative mentions."
            )
        
        # Return sentiment summary
        return {
            "score": sentiment_score,
            "category": category,
            "distribution": {
                "positive": round(counts["positive"] / total * 100, 1),
                "neutral": round(counts["neutral"] / total * 100, 1),
                "negative": round(counts["negative"] / total * 100, 1)
            },
            "counts": counts,
            "total_articles": total,
            "summary": summary,
            "news_sample": recent_news[:5] if recent_news else []
        }
