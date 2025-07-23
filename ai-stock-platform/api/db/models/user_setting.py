"""
UserSetting model for QuantumVestAI
Created: 2025-07-23
Author: daparthi001
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.base import Base



class UserSetting(Base):
    """User-specific settings model"""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False, default="general")
    key = Column(String(100), nullable=False)
    value = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="user_settings")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'category', 'key', name='uq_user_category_key'),
    )

    def __repr__(self):
        return f"<UserSetting(user_id={self.user_id}, key='{self.category}.{self.key}')>"

    def to_dict(self):
        """Convert user setting to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category": self.category,
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }