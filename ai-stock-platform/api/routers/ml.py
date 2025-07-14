"""
Machine Learning Router
Created: 2025-05-20 04:52:04
Author: daparthi001
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.exceptions import PermissionDeniedError, ResourceNotFoundError
from core.security import get_current_user
from db.models.user import User
from db.session import get_db
from fastapi import APIRouter, BackgroundTasks, Body, Depends, Path, Query, status
from schemas.ml import (DatasetResponse, FeatureImportanceResponse,
                        HyperparameterResponse, ModelComparisonResponse,
                        ModelEvaluationResponse, ModelPredictionResponse,
                        ModelResponse, ModelTrainingResponse)
from services.ml_service import MLService
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/ml",
    tags=["machine-learning"],
    dependencies=[Depends(get_current_user)]
)

@router.get(
    "/models",
    response_model=List[ModelResponse],
    summary="List models",
    description="Get all available ML models"
)
async def list_models(
    model_type: Optional[str] = Query(
        None,
        regex="^(price|sentiment|portfolio|risk)$"
    ),
    status: Optional[str] = Query(
        None,
        regex="^(active|training|failed|archived)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[ModelResponse]:
    """List available ML models."""
    if current_user.role == "free":
        raise PermissionDeniedError("ML models require premium subscription")
    
    service = MLService(db)
    return await service.list_models(
        model_type=model_type,
        status=status
    )

@router.post(
    "/models/train",
    response_model=ModelTrainingResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Train model",
    description="Train a new ML model"
)
async def train_model(
    model_type: str = Query(
        ...,
        regex="^(price|sentiment|portfolio|risk)$"
    ),
    model_config: Dict[str, Any] = Body(...),
    dataset_id: Optional[int] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ModelTrainingResponse:
    """Train new ML model."""
    if current_user.role != "admin":
        raise PermissionDeniedError("Model training restricted to admin users")
    
    service = MLService(db)
    training_job = await service.train_model(
        model_type=model_type,
        model_config=model_config,
        dataset_id=dataset_id,
        user_id=current_user.id
    )
    
    if background_tasks:
        background_tasks.add_task(
            service.monitor_training,
            training_job.id
        )
    
    return training_job

@router.get(
    "/models/{model_id}/evaluate",
    response_model=ModelEvaluationResponse,
    summary="Evaluate model",
    description="Evaluate model performance"
)
async def evaluate_model(
    model_id: int,
    test_dataset_id: Optional[int] = None,
    metrics: List[str] = Query(
        ["accuracy", "precision", "recall", "f1"],
        description="Evaluation metrics"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ModelEvaluationResponse:
    """Evaluate ML model."""
    service = MLService(db)
    evaluation = await service.evaluate_model(
        model_id=model_id,
        test_dataset_id=test_dataset_id,
        metrics=metrics,
        user_id=current_user.id
    )
    
    if not evaluation:
        raise ResourceNotFoundError(f"Model {model_id} not found")
    
    return evaluation

@router.post(
    "/models/{model_id}/predict",
    response_model=ModelPredictionResponse,
    summary="Make prediction",
    description="Make predictions using model"
)
async def make_prediction(
    model_id: int,
    input_data: Dict[str, Any],
    confidence_threshold: float = Query(
        0.8,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ModelPredictionResponse:
    """Make model predictions."""
    service = MLService(db)
    prediction = await service.make_prediction(
        model_id=model_id,
        input_data=input_data,
        confidence_threshold=confidence_threshold,
        user_id=current_user.id
    )
    
    if not prediction:
        raise ResourceNotFoundError(f"Model {model_id} not found")
    
    return prediction

@router.get(
    "/models/{model_id}/features",
    response_model=FeatureImportanceResponse,
    summary="Feature importance",
    description="Get model feature importance"
)
async def get_feature_importance(
    model_id: int,
    n_features: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> FeatureImportanceResponse:
    """Get feature importance."""
    service = MLService(db)
    features = await service.get_feature_importance(
        model_id=model_id,
        n_features=n_features,
        user_id=current_user.id
    )
    
    if not features:
        raise ResourceNotFoundError(f"Model {model_id} not found")
    
    return features

@router.get(
    "/models/compare",
    response_model=ModelComparisonResponse,
    summary="Compare models",
    description="Compare multiple ML models"
)
async def compare_models(
    model_ids: List[int],
    metrics: List[str] = Query(
        ["accuracy", "latency", "memory"],
        description="Comparison metrics"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ModelComparisonResponse:
    """Compare ML models."""
    service = MLService(db)
    comparison = await service.compare_models(
        model_ids=model_ids,
        metrics=metrics,
        user_id=current_user.id
    )
    
    return comparison

@router.get(
    "/models/{model_id}/hyperparameters",
    response_model=HyperparameterResponse,
    summary="Get hyperparameters",
    description="Get model hyperparameters"
)
async def get_hyperparameters(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> HyperparameterResponse:
    """Get model hyperparameters."""
    service = MLService(db)
    hyperparameters = await service.get_hyperparameters(
        model_id=model_id,
        user_id=current_user.id
    )
    
    if not hyperparameters:
        raise ResourceNotFoundError(f"Model {model_id} not found")
    
    return hyperparameters

@router.get(
    "/datasets",
    response_model=List[DatasetResponse],
    summary="List datasets",
    description="Get available training datasets"
)
async def list_datasets(
    dataset_type: Optional[str] = Query(
        None,
        regex="^(price|sentiment|market|fundamental)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[DatasetResponse]:
    """List available datasets."""
    service = MLService(db)
    return await service.list_datasets(dataset_type)
