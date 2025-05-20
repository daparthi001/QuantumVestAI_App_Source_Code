from sqlalchemy import Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from db.base_class import Base, TimestampMixin


class UserActivityLog(Base, TimestampMixin):
    __tablename__ = "user_activity_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String(100), nullable=False)
    activity_details = Column(JSON)
    ip_address = Column(String(45))

    # Relationships
    user = relationship("User", back_populates="activities")