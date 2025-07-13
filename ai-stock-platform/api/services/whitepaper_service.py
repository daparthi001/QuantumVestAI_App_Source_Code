from __future__ import annotations

"""Simplified whitepaper service used by API routes."""

import os
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session
from fastapi import UploadFile

from utils.whitepaper_analysis import WhitepaperAnalyzer


class WhitepaperService:
    """Service for handling whitepaper uploads and analysis."""

    _storage: Dict[int, str] = {}
    _id_counter: int = 1

    def __init__(self, db: Session) -> None:
        self.db = db
        self.analyzer = WhitepaperAnalyzer()

    async def upload_whitepaper(
        self,
        file: UploadFile,
        ticker: str,
        document_type: str,
        document_date: str,
        user_id: int,
    ) -> Dict[str, Any]:
        """Save file and trigger analysis. Returns whitepaper metadata."""
        contents = await file.read()
        save_path = os.path.join("/tmp", file.filename)
        with open(save_path, "wb") as f:
            f.write(contents)

        wp_id = WhitepaperService._id_counter
        WhitepaperService._id_counter += 1
        WhitepaperService._storage[wp_id] = save_path

        now = datetime.utcnow()
        return {
            "id": wp_id,
            "ticker": ticker,
            "document_type": document_type,
            "document_date": datetime.strptime(document_date, "%Y-%m-%d"),
            "title": file.filename,
            "file_size": len(contents),
            "file_type": file.content_type,
            "page_count": 1,
            "language": "en",
            "user_id": user_id,
            "status": "uploaded",
            "processing_status": "completed",
            "created_at": now,
            "updated_at": now,
            "file_url": save_path,
            "thumbnail_url": None,
        }

    async def get_analysis(
        self,
        whitepaper_id: int,
        analysis_type: str,
        user_id: int,
    ) -> Dict[str, Any] | None:
        """Return analysis results for a whitepaper."""
        path = self._storage.get(whitepaper_id)
        if not path:
            return None

        analysis = await self.analyzer.analyze_whitepaper(path)
        return {
            "whitepaper_id": whitepaper_id,
            "analysis_type": analysis_type,
            "timestamp": datetime.utcnow(),
            "financial_metrics": [],
            "risk_factors": [],
            "strategic_goals": [],
            "key_insights": analysis.get("summary", {}).get("key_points", []),
            "market_impact": {},
            "sentiment_analysis": analysis.get("sentiment_analysis", {}),
            "confidence_score": analysis.get("innovation_score", {}).get("score", 50),
        }

    async def compare_whitepapers(
        self,
        whitepaper_id: int,
        compare_id: int,
        aspects: List[str],
        user_id: int,
    ) -> Dict[str, Any]:
        """Compare two whitepapers and return a simple diff."""
        path_a = self._storage.get(whitepaper_id)
        path_b = self._storage.get(compare_id)
        if not path_a or not path_b:
            return {}

        analysis_a = await self.analyzer.analyze_whitepaper(path_a)
        analysis_b = await self.analyzer.analyze_whitepaper(path_b)

        return {
            "first_whitepaper_id": whitepaper_id,
            "second_whitepaper_id": compare_id,
            "timestamp": datetime.utcnow(),
            "comparison_aspects": aspects,
            "comparisons": [],
            "summary": "Simple comparison",
            "key_differences": [],
            "recommendations": [],
        }

    async def get_metrics(
        self,
        whitepaper_id: int,
        metric_types: List[str],
        user_id: int,
    ) -> Dict[str, Any] | None:
        """Return placeholder metrics for a whitepaper."""
        path = self._storage.get(whitepaper_id)
        if not path:
            return None

        return {
            "whitepaper_id": whitepaper_id,
            "timestamp": datetime.utcnow(),
            "metric_types": metric_types,
            "metrics": [],
            "trends": {},
            "benchmarks": {},
            "data_quality": 1.0,
        }

    async def get_summary(
        self,
        whitepaper_id: int,
        summary_type: str,
        max_length: int,
        user_id: int,
    ) -> Dict[str, Any] | None:
        """Return a short summary of the whitepaper."""
        path = self._storage.get(whitepaper_id)
        if not path:
            return None

        analysis = await self.analyzer.analyze_whitepaper(path)
        summary_text = analysis.get("summary", "")
        return {
            "whitepaper_id": whitepaper_id,
            "timestamp": datetime.utcnow(),
            "summary_type": summary_type,
            "sections": [
                {
                    "title": "Summary",
                    "content": str(summary_text)[:max_length],
                    "key_points": [],
                    "word_count": len(str(summary_text).split()),
                    "page_references": [],
                }
            ],
            "total_word_count": len(str(summary_text).split()),
            "key_takeaways": [],
            "methodology": "auto",
            "confidence_score": analysis.get("innovation_score", {}).get("score", 50),
        }
