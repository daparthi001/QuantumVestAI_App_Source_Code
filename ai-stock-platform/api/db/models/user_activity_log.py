from db.base_class import Base, TimestampMixin
from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class UserActivityLog(Base, TimestampMixin):
    __tablename__ = "user_activity_log"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String(100), nullable=False)
    activity_details = Column(JSON)
    ip_address = Column(String(45))

    # Relationships    user = relationship("User", back_populates="activities")
