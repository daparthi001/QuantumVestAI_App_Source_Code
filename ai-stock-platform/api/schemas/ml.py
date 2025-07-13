"""
Machine Learning Schemas
Created: 2025-05-20 04:52:04
Author: daparthi001
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ModelMetrics(BaseModel):
    """Model metrics schema."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    rmse: Optional[float]
    mae: Optional[float]
    r2_score: Optional[float]
    latency: float
    memory_usage: float

class ModelResponse(BaseModel):
    """Model response schema."""
    id: int
    name: str
    version: str
    type: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    metrics: ModelMetrics
    features: List[str]
    target: str
    architecture: Dict[str, Any]

    class Config:
        from_attributes = True

class TrainingConfig(BaseModel):
    """Training configuration schema."""
    batch_size: int
    epochs: int
    learning_rate: float
    optimizer: str
    loss_function: str
    validation_split: float
    early_stopping: bool
    custom_parameters: Optional[Dict[str, Any]]

class ModelTrainingResponse(BaseModel):
    """Model training response schema."""
    job_id: str
    model_id: int
    status: str
    progress: float
    started_at: datetime
    estimated_completion: datetime
    current_epoch: Optional[int]
    current_metrics: Optional[Dict[str, float]]
    log_url: str

class EvaluationMetric(BaseModel):
    """Evaluation metric schema."""
    name: str
    value: float
    threshold: Optional[float]
    comparison: Optional[str]

class ModelEvaluationResponse(BaseModel):
    """Model evaluation response schema."""
    model_id: int
    timestamp: datetime
    dataset_info: Optional[Dict[str, Any]]
    metrics: List[EvaluationMetric]
    confusion_matrix: Optional[List[List[int]]]
    roc_curve: Optional[Dict[str, List[float]]]
    pr_curve: Optional[Dict[str, List[float]]]

class PredictionResult(BaseModel):
    """Prediction result schema."""
    prediction: Any
    probability: float
    confidence: float
    features_used: Dict[str, Any]
    explanation: Optional[Dict[str, Any]]

class ModelPredictionResponse(BaseModel):
    """Model prediction response schema."""
    model_id: int
    timestamp: datetime
    results: List[PredictionResult]
    execution_time: float
    model_version: str

class FeatureImportance(BaseModel):
    """Feature importance schema."""
    feature: str
    importance: float
    correlation: Optional[float]
    shap_value: Optional[float]

class FeatureImportanceResponse(BaseModel):
    """Feature importance response schema."""
    model_id: int
    timestamp: datetime
    method: str
    features: List[FeatureImportance]
    visualization_data: Dict[str, Any]

class ModelComparison(BaseModel):
    """Model comparison schema."""
    model_id: int
    name: str
    metrics: Dict[str, float]
    advantages: List[str]
    disadvantages: List[str]

class ModelComparisonResponse(BaseModel):
    """Model comparison response schema."""
    timestamp: datetime
    models: List[ModelComparison]
    best_model: int
    comparison_matrix: Dict[str, List[float]]
    statistical_tests: Dict[str, Any]

class Hyperparameter(BaseModel):
    """Hyperparameter schema."""
    name: str
    value: Any
    description: str
    range: Optional[List[Any]]
    importance: Optional[float]

class HyperparameterResponse(BaseModel):
    """Hyperparameter response schema."""
    model_id: int
    timestamp: datetime
    hyperparameters: List[Hyperparameter]
    tuning_history: Optional[Dict[str, Any]]
    optimal_values: Dict[str, Any]

class DatasetMetadata(BaseModel):
    """Dataset metadata schema."""
    rows: int
    columns: int
    features: List[str]
    target: str
    time_range: Dict[str, datetime]
    missing_values: Dict[str, int]

class DatasetResponse(BaseModel):
    """Dataset response schema."""
    id: int
    name: str
    type: str
    description: str
    version: str
    created_at: datetime
    updated_at: datetime
    metadata: DatasetMetadata
    quality_score: float
    last_validated: datetime

    class Config:
        from_attributes = True
