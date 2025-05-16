from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class WhitepaperCreate(BaseModel):
    """Schema for creating a whitepaper."""
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class WhitepaperResponse(BaseModel):
    """Schema for whitepaper response."""
    id: str
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    status: str
    created_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class WhitepaperAnalysisResponse(BaseModel):
    """Schema for whitepaper analysis response."""
    whitepaper_id: str
    title: str
    status: str
    analyzed_at: Optional[datetime] = None
    analysis_data: Dict[str, Any]

class WhitepaperComparisonRequest(BaseModel):
    """Schema for whitepaper comparison request."""
    whitepaper_ids: List[str]

class WhitepaperComparisonResponse(BaseModel):
    """Schema for whitepaper comparison response."""
    whitepaper_ids: List[str]
    comparison_id: str
    status: str
    results: Dict[str, Any]