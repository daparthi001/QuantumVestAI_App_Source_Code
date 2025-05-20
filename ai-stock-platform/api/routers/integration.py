"""
Integration Router
Created: 2025-05-20 04:56:23
Author: daparthi001
"""
from fastapi import APIRouter, Depends, Query, Path, status, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.security import get_current_user, verify_webhook_signature
from core.exceptions import ResourceNotFoundError, PermissionDeniedError, IntegrationError
from api.db.session import get_db
from api.db.models.user import User
from api.services.integration_service import IntegrationService
from api.schemas.integration import (
    IntegrationCreate,
    IntegrationResponse,
    WebhookResponse,
    ExportResponse,
    DataSyncResponse,
    IntegrationStatusResponse,
    ApiKeyResponse,
    OAuthConfigResponse
)

router = APIRouter(
    prefix="/integrations",
    tags=["integrations"],
    dependencies=[Depends(get_current_user)]
)

@router.post(
    "/",
    response_model=IntegrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create integration",
    description="Create a new third-party integration"
)
async def create_integration(
    integration: IntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> IntegrationResponse:
    """Create new integration."""
    if current_user.role == "free":
        raise PermissionDeniedError("Integrations require premium subscription")
    
    service = IntegrationService(db)
    return await service.create_integration(
        integration=integration,
        user_id=current_user.id
    )

@router.get(
    "/",
    response_model=List[IntegrationResponse],
    summary="List integrations",
    description="Get all user integrations"
)
async def list_integrations(
    status: Optional[str] = Query(
        None,
        regex="^(active|inactive|error)$"
    ),
    integration_type: Optional[str] = Query(
        None,
        regex="^(broker|data|analytics|crm)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[IntegrationResponse]:
    """List all integrations."""
    service = IntegrationService(db)
    return await service.list_integrations(
        user_id=current_user.id,
        status=status,
        integration_type=integration_type
    )

@router.post(
    "/webhook/{integration_id}",
    response_model=WebhookResponse,
    summary="Handle webhook",
    description="Handle integration webhook"
)
async def handle_webhook(
    integration_id: int,
    request: Request,
    signature: str = Query(..., alias="x-webhook-signature"),
    db: Session = Depends(get_db)
) -> WebhookResponse:
    """Handle integration webhook."""
    payload = await request.json()
    
    if not verify_webhook_signature(payload, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    service = IntegrationService(db)
    return await service.process_webhook(
        integration_id=integration_id,
        payload=payload
    )

@router.post(
    "/{integration_id}/export",
    response_model=ExportResponse,
    summary="Export data",
    description="Export data to integration"
)
async def export_data(
    integration_id: int,
    data_type: str = Query(
        ...,
        regex="^(portfolio|trades|analysis|reports)$"
    ),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ExportResponse:
    """Export data to integration."""
    service = IntegrationService(db)
    return await service.export_data(
        integration_id=integration_id,
        data_type=data_type,
        start_date=start_date,
        end_date=end_date,
        user_id=current_user.id
    )

@router.post(
    "/{integration_id}/sync",
    response_model=DataSyncResponse,
    summary="Sync data",
    description="Synchronize data with integration"
)
async def sync_data(
    integration_id: int,
    sync_type: str = Query(
        ...,
        regex="^(full|incremental)$"
    ),
    resources: List[str] = Query(
        ["positions", "orders", "accounts"],
        description="Resources to sync"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DataSyncResponse:
    """Sync integration data."""
    service = IntegrationService(db)
    return await service.sync_data(
        integration_id=integration_id,
        sync_type=sync_type,
        resources=resources,
        user_id=current_user.id
    )

@router.get(
    "/{integration_id}/status",
    response_model=IntegrationStatusResponse,
    summary="Get status",
    description="Get integration status"
)
async def get_integration_status(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> IntegrationStatusResponse:
    """Get integration status."""
    service = IntegrationService(db)
    status = await service.get_status(
        integration_id=integration_id,
        user_id=current_user.id
    )
    
    if not status:
        raise ResourceNotFoundError(f"Integration {integration_id} not found")
    
    return status

@router.post(
    "/{integration_id}/api-key",
    response_model=ApiKeyResponse,
    summary="Generate API key",
    description="Generate new integration API key"
)
async def generate_api_key(
    integration_id: int,
    expires_in_days: int = Query(
        30,
        ge=1,
        le=365,
        description="Key expiration in days"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ApiKeyResponse:
    """Generate integration API key."""
    service = IntegrationService(db)
    return await service.generate_api_key(
        integration_id=integration_id,
        expires_in_days=expires_in_days,
        user_id=current_user.id
    )

@router.get(
    "/oauth/config",
    response_model=OAuthConfigResponse,
    summary="OAuth config",
    description="Get OAuth configuration"
)
async def get_oauth_config(
    provider: str = Query(
        ...,
        regex="^(google|github|twitter)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> OAuthConfigResponse:
    """Get OAuth configuration."""
    service = IntegrationService(db)
    return await service.get_oauth_config(provider)