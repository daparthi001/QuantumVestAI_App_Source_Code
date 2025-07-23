"""
AuditLog model for QuantumVestAI
Created: 2025-07-23
Author: daparthi001
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
    JSON,
)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.base import Base



class AuditLog(Base):
    """Audit log model for tracking user actions"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(50), nullable=False, index=True)
    record_id = Column(Integer, index=True)
    action = Column(String(20), nullable=False, index=True)
    old_values = Column(JSON)
    new_values = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            action.in_(['INSERT', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'ACCESS']),
            name='valid_action'
        ),
        {
            "extend_existing": True
        }
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', table='{self.table_name}')>"

    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            "id": self.id,
            "table_name": self.table_name,
            "record_id": self.record_id,
            "action": self.action,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "user_id": self.user_id,
            "ip_address": str(self.ip_address) if self.ip_address else None,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }