from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from database.connection import get_db
from database.models.user import User, Investigation, OSINTResult
from api.routes.auth import get_current_user

router = APIRouter()

@router.post("/")
async def create_investigation(
    title: str,
    target: str,
    target_type: str,
    description: Optional[str] = None,
    priority: str = "medium",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new investigation"""
    investigation = Investigation(
        title=title,
        description=description,
        target=target,
        target_type=target_type,
        priority=priority,
        owner_id=current_user.id
    )
    db.add(investigation)
    db.commit()
    db.refresh(investigation)
    
    return {
        "id": investigation.id,
        "uuid": investigation.uuid,
        "title": investigation.title,
        "target": investigation.target,
        "target_type": investigation.target_type,
        "status": investigation.status,
        "priority": investigation.priority,
        "created_at": investigation.created_at
    }

@router.get("/")
async def get_investigations(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's investigations"""
    query = db.query(Investigation).filter(Investigation.owner_id == current_user.id)
    
    if status:
        query = query.filter(Investigation.status == status)
    
    investigations = query.order_by(Investigation.created_at.desc()).all()
    
    return [
        {
            "id": inv.id,
            "uuid": inv.uuid,
            "title": inv.title,
            "target": inv.target,
            "target_type": inv.target_type,
            "status": inv.status,
            "priority": inv.priority,
            "created_at": inv.created_at,
            "updated_at": inv.updated_at,
            "results_count": len(inv.results)
        }
        for inv in investigations
    ]

@router.get("/{investigation_id}")
async def get_investigation(
    investigation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific investigation"""
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.owner_id == current_user.id
    ).first()
    
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    return {
        "id": investigation.id,
        "uuid": investigation.uuid,
        "title": investigation.title,
        "description": investigation.description,
        "target": investigation.target,
        "target_type": investigation.target_type,
        "status": investigation.status,
        "priority": investigation.priority,
        "created_at": investigation.created_at,
        "updated_at": investigation.updated_at,
        "completed_at": investigation.completed_at,
        "results": [
            {
                "id": result.id,
                "module_name": result.module_name,
                "sub_module": result.sub_module,
                "query": result.query,
                "result_type": result.result_type,
                "confidence_score": result.confidence_score,
                "created_at": result.created_at,
                "data": result.data
            }
            for result in investigation.results
        ]
    }

@router.put("/{investigation_id}")
async def update_investigation(
    investigation_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update investigation"""
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.owner_id == current_user.id
    ).first()
    
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    if title:
        investigation.title = title
    if description:
        investigation.description = description
    if status:
        investigation.status = status
        if status == "completed":
            investigation.completed_at = datetime.utcnow()
    if priority:
        investigation.priority = priority
    
    investigation.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Investigation updated successfully"}

@router.delete("/{investigation_id}")
async def delete_investigation(
    investigation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete investigation"""
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.owner_id == current_user.id
    ).first()
    
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    db.delete(investigation)
    db.commit()
    
    return {"message": "Investigation deleted successfully"}