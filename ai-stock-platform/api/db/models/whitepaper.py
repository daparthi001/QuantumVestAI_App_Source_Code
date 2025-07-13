from uuid import uuid4

from db.base_class import Base
from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.dialects.postgresql import ARRAY  # If using PostgreSQL
from sqlalchemy.orm import relationship


class Whitepaper(Base):
    """Whitepaper model for storing uploaded documents."""
    __tablename__ = "whitepapers"
    __table_args__ = {"extend_existing": True}
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(ARRAY(String), nullable=True)  # For PostgreSQL
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, nullable=False)  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    analyzed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="whitepapers")
    analyses = relationship("WhitepaperAnalysis", back_populates="whitepaper")


class WhitepaperAnalysis(Base):
    """Model for storing whitepaper analysis results."""
    __tablename__ = "whitepaper_analyses"
    __table_args__ = {"extend_existing": True}
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    whitepaper_id = Column(String, ForeignKey("whitepapers.id"))
    analysis_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    # Relationships    whitepaper = relationship("Whitepaper", back_populates="analyses")
