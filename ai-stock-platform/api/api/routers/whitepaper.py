from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime

from api.db.session import get_db
from api.db.models.user import User
from api.db.models.whitepaper import Whitepaper, WhitepaperAnalysis
from api.core.security import get_current_user
from api.utils.whitepaper_analysis import WhitepaperAnalyzer
from api.schemas.whitepaper import (
    WhitepaperCreate, 
    WhitepaperResponse,
    WhitepaperAnalysisResponse,
    WhitepaperComparisonRequest,
    WhitepaperComparisonResponse
)

router = APIRouter(prefix="/whitepapers")

# Initialize analyzer
whitepaper_analyzer = WhitepaperAnalyzer()

# File upload helper
def save_upload_file(upload_file: UploadFile, folder: str = "uploads/whitepapers") -> str:
    """Save an uploaded file and return the path."""
    os.makedirs(folder, exist_ok=True)
    
    # Create a unique filename
    file_ext = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(folder, unique_filename)
    
    # Save the file
    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())
    
    return file_path

async def analyze_whitepaper_task(file_path: str, paper_id: str, db: Session) -> None:
    """Background task to analyze a whitepaper and store results."""
    try:
        # Get whitepaper from database
        whitepaper = db.query(Whitepaper).filter(Whitepaper.id == paper_id).first()
        if not whitepaper:
            return
        
        # Update status
        whitepaper.status = "processing"
        db.commit()
        
        # Analyze whitepaper
        results = await whitepaper_analyzer.analyze_whitepaper(file_path, paper_id)
        
        # Create analysis record
        analysis = WhitepaperAnalysis(
            whitepaper_id=paper_id,
            analysis_data=results,
            created_at=datetime.utcnow()
        )
        
        db.add(analysis)
        
        # Update whitepaper status
        whitepaper.status = "completed"
        whitepaper.analyzed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        # Update status to failed
        whitepaper = db.query(Whitepaper).filter(Whitepaper.id == paper_id).first()
        if whitepaper:
            whitepaper.status = "failed"
            whitepaper.error_message = str(e)[:255]  # Truncate if too long
            db.commit()

@router.post("/", response_model=WhitepaperResponse, status_code=202)
async def upload_whitepaper(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a whitepaper for analysis."""
    # Validate file extension
    allowed_extensions = {'.pdf', '.txt', '.docx'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not supported. Must be one of: {', '.join(allowed_extensions)}"
        )
    
    # Save file
    file_path = save_upload_file(file)
    
    # Create whitepaper record
    whitepaper = Whitepaper(
        title=title,
        description=description,
        tags=tags.split(',') if tags else [],
        file_path=file_path,
        file_name=file.filename,
        file_size=os.path.getsize(file_path),
        user_id=current_user.id,
        status="pending",
        created_at=datetime.utcnow()
    )
    
    db.add(whitepaper)
    db.commit()
    db.refresh(whitepaper)
    
    # Start analysis in background
    background_tasks.add_task(
        analyze_whitepaper_task, 
        file_path=file_path, 
        paper_id=whitepaper.id, 
        db=db
    )
    
    return {
        "id": whitepaper.id,
        "title": whitepaper.title,
        "status": whitepaper.status,
        "message": "Whitepaper uploaded successfully. Analysis is being processed."
    }

@router.get("/{whitepaper_id}", response_model=WhitepaperResponse)
async def get_whitepaper(
    whitepaper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get whitepaper information."""
    whitepaper = db.query(Whitepaper).filter(
        Whitepaper.id == whitepaper_id,
        Whitepaper.user_id == current_user.id
    ).first()
    
    if not whitepaper:
        raise HTTPException(status_code=404, detail="Whitepaper not found")
    
    return whitepaper

@router.get("/{whitepaper_id}/analysis", response_model=WhitepaperAnalysisResponse)
async def get_whitepaper_analysis(
    whitepaper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get whitepaper analysis results."""
    # Check if whitepaper exists and belongs to user
    whitepaper = db.query(Whitepaper).filter(
        Whitepaper.id == whitepaper_id,
        Whitepaper.user_id == current_user.id
    ).first()
    
    if not whitepaper:
        raise HTTPException(status_code=404, detail="Whitepaper not found")
    
    # Get latest analysis
    analysis = db.query(WhitepaperAnalysis).filter(
        WhitepaperAnalysis.whitepaper_id == whitepaper_id
    ).order_by(WhitepaperAnalysis.created_at.desc()).first()
    
    if not analysis:
        if whitepaper.status == "failed":
            raise HTTPException(
                status_code=422, 
                detail=f"Analysis failed: {whitepaper.error_message}"
            )
        else:
            raise HTTPException(
                status_code=404, 
                detail="Analysis not found. The whitepaper may still be processing."
            )
    
    return {
        "whitepaper_id": whitepaper_id,
        "title": whitepaper.title,
        "status": whitepaper.status,
        "analyzed_at": whitepaper.analyzed_at,
        "analysis_data": analysis.analysis_data
    }

@router.post("/compare", response_model=WhitepaperComparisonResponse)
async def compare_whitepapers(
    request: WhitepaperComparisonRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare multiple whitepapers."""
    # Check if all whitepapers exist and belong to user
    whitepapers = []
    for paper_id in request.whitepaper_ids:
        whitepaper = db.query(Whitepaper).filter(
            Whitepaper.id == paper_id,
            Whitepaper.user_id == current_user.id
        ).first()
        
        if not whitepaper:
            raise HTTPException(status_code=404, detail=f"Whitepaper with ID {paper_id} not found")
        
        if whitepaper.status != "completed":
            raise HTTPException(
                status_code=422, 
                detail=f"Whitepaper {paper_id} analysis is not complete. Status: {whitepaper.status}"
            )
        
        whitepapers.append(whitepaper)
    
    # Create comparison task
    paper_ids = [w.id for w in whitepapers]
    file_paths = [w.file_path for w in whitepapers]
    
    # This would be implemented as a background task in a real application
    # For simplicity, we'll do it synchronously in this example
    comparison_results = await whitepaper_analyzer.compare_whitepapers(file_paths, paper_ids)
    
    return {
        "whitepaper_ids": paper_ids,
        "comparison_id": str(uuid.uuid4()),
        "status": "completed",
        "results": comparison_results
    }

@router.get("/investment-insights/{whitepaper_id}")
async def get_investment_insights(
    whitepaper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get investment insights from a whitepaper analysis."""
    # Check if whitepaper exists and belongs to user
    whitepaper = db.query(Whitepaper).filter(
        Whitepaper.id == whitepaper_id,
        Whitepaper.user_id == current_user.id
    ).first()
    
    if not whitepaper:
        raise HTTPException(status_code=404, detail="Whitepaper not found")
    
    # Get latest analysis
    analysis = db.query(WhitepaperAnalysis).filter(
        WhitepaperAnalysis.whitepaper_id == whitepaper_id
    ).order_by(WhitepaperAnalysis.created_at.desc()).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Generate investment insights
    insights = whitepaper_analyzer.extract_investment_insights(analysis.analysis_data)
    
    return insights

@router.get("/", response_model=List[WhitepaperResponse])
async def list_whitepapers(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all whitepapers for the current user."""
    whitepapers = db.query(Whitepaper).filter(
        Whitepaper.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return whitepapers