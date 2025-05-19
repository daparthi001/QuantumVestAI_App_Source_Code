"""
User Model
Created: 2025-05-19 05:29:26
Author: daparthi001
"""
from sqlalchemy import Boolean, Column, String, Integer
from api.db.base_class import Base, TimestampMixin

class User(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<User {self.username}>"