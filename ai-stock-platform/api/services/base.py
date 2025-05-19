"""
Base Service Implementation
Created: 2025-05-19 03:45:54
Author: daparthi001
"""
from sqlalchemy.orm import Session
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from fastapi.encoders import jsonable_encoder
from datetime import datetime

from api.models.base import ModelBase
from api.core.exceptions import ResourceNotFoundError

ModelType = TypeVar("ModelType", bound=ModelBase)

class BaseService(Generic[ModelType]):
    """Base class for all services"""
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: int) -> Optional[ModelType]:
        """Get a single record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> List[ModelType]:
        """Get multiple records with optional filtering"""
        query = self.db.query(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        return query.offset(skip).limit(limit).all()
    
    def create(self, *, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record"""
        obj_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_data)
        
        if hasattr(db_obj, "created_at"):
            db_obj.created_at = datetime.utcnow()
        if hasattr(db_obj, "updated_at"):
            db_obj.updated_at = datetime.utcnow()
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, *, id: int, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Update an existing record"""
        db_obj = self.get(id)
        if not db_obj:
            raise ResourceNotFoundError(f"{self.model.__name__} with id {id} not found")
        
        obj_data = jsonable_encoder(obj_in)
        
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        if hasattr(db_obj, "updated_at"):
            db_obj.updated_at = datetime.utcnow()
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, *, id: int) -> bool:
        """Delete a record"""
        db_obj = self.get(id)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        return True
    
    def count(self, filters: Dict[str, Any] = None) -> int:
        """Count records with optional filtering"""
        query = self.db.query(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        return query.count()