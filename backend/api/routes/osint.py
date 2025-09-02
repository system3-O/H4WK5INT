from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import asyncio

from database.connection import get_db
from database.models.user import User, Investigation, OSINTResult
from api.routes.auth import get_current_user
from modules.socmint import SOCMINTModule
from modules.humint import HUMINTModule
from modules.imint import IMINTModule
from modules.techint import TECHINTModule
from modules.geoint import GEOINTModule
from modules.webint import WEBINTModule

router = APIRouter()

async def run_osint_module(
    investigation_id: int,
    module_name: str,
    query: str,
    options: Dict[str, Any],
    db: Session
):
    """Run OSINT module in background"""
    try:
        # Get module instance
        modules = {
            "socmint": SOCMINTModule(),
            "humint": HUMINTModule(),
            "imint": IMINTModule(),
            "techint": TECHINTModule(),
            "geoint": GEOINTModule(),
            "webint": WEBINTModule()
        }
        
        if module_name not in modules:
            return
        
        module = modules[module_name]
        results = await module.run_investigation(query, options)
        
        # Save results to database
        for result in results:
            osint_result = OSINTResult(
                investigation_id=investigation_id,
                module_name=module_name,
                sub_module=result.get("sub_module"),
                query=query,
                result_type=result.get("type"),
                data=result.get("data"),
                metadata=result.get("metadata"),
                confidence_score=result.get("confidence", 50),
                source_url=result.get("source_url")
            )
            db.add(osint_result)
        
        db.commit()
        
    except Exception as e:
        print(f"Error running {module_name} module: {str(e)}")

@router.post("/socmint")
async def run_socmint(
    investigation_id: int,
    query: str,
    platforms: Optional[list] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run Social Media Intelligence module"""
    # Verify investigation ownership
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.owner_id == current_user.id
    ).first()
    
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    options = {"platforms": platforms or ["twitter", "facebook", "instagram", "linkedin"]}
    
    background_tasks.add_task(
        run_osint_module,
        investigation_id,
        "socmint",
        query,
        options,
        db
    )
    
    return {"message": "SOCMINT investigation started", "investigation_id": investigation_id}

@router.post("/humint")
async def run_humint(
    investigation_id: int,
    query: str,
    search_types: Optional[list] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run Human Intelligence module"""
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.owner_id == current_user.id
    ).first()
    
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    options = {"search_types": search_types or ["email", "username", "phone", "name"]}
    
    background_tasks.add_task(
        run_osint_module,
        investigation_id,
        "humint",
        query,
        options,
        db
    )
    
    return {"message": "HUMINT investigation started", "investigation_id": investigation_id}

@router.post("/imint")
async def run_imint(
    investigation_id: int,
    image_url: str,
    analysis_types: Optional[list] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run Image Intelligence module"""
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.owner_id == current_user.id
    ).first()
    
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    options = {"analysis_types": analysis_types or ["reverse_search", "metadata", "faces"]}
    
    background_tasks.add_task(
        run_osint_module,
        investigation_id,
        "imint",
        image_url,
        options,
        db
    )
    
    return {"message": "IMINT investigation started", "investigation_id": investigation_id}

@router.post("/techint")
async def run_techint(
    investigation_id: int,
    target: str,
    scan_types: Optional[list] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run Technical Intelligence module"""
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.owner_id == current_user.id
    ).first()
    
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    options = {"scan_types": scan_types or ["dns", "subdomains", "ports", "ssl", "whois"]}
    
    background_tasks.add_task(
        run_osint_module,
        investigation_id,
        "techint",
        target,
        options,
        db
    )
    
    return {"message": "TECHINT investigation started", "investigation_id": investigation_id}

@router.post("/geoint")
async def run_geoint(
    investigation_id: int,
    query: str,
    location_types: Optional[list] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run Geographic Intelligence module"""
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.owner_id == current_user.id
    ).first()
    
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    options = {"location_types": location_types or ["ip_geo", "address", "coordinates"]}
    
    background_tasks.add_task(
        run_osint_module,
        investigation_id,
        "geoint",
        query,
        options,
        db
    )
    
    return {"message": "GEOINT investigation started", "investigation_id": investigation_id}

@router.post("/webint")
async def run_webint(
    investigation_id: int,
    query: str,
    search_engines: Optional[list] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run Web Intelligence module"""
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.owner_id == current_user.id
    ).first()
    
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    options = {"search_engines": search_engines or ["google", "bing", "duckduckgo"]}
    
    background_tasks.add_task(
        run_osint_module,
        investigation_id,
        "webint",
        query,
        options,
        db
    )
    
    return {"message": "WEBINT investigation started", "investigation_id": investigation_id}

@router.get("/modules")
async def get_available_modules():
    """Get list of available OSINT modules"""
    return {
        "modules": [
            {
                "name": "socmint",
                "title": "Social Media Intelligence",
                "description": "Profile enumeration, social graph mapping, content analysis",
                "platforms": ["twitter", "facebook", "instagram", "linkedin", "tiktok"]
            },
            {
                "name": "humint", 
                "title": "Human Intelligence",
                "description": "People search, employment history, background checks",
                "search_types": ["email", "username", "phone", "name", "address"]
            },
            {
                "name": "imint",
                "title": "Image Intelligence", 
                "description": "Reverse image search, metadata extraction, facial recognition",
                "analysis_types": ["reverse_search", "metadata", "faces", "objects"]
            },
            {
                "name": "techint",
                "title": "Technical Intelligence",
                "description": "Domain enumeration, port scanning, technology analysis",
                "scan_types": ["dns", "subdomains", "ports", "ssl", "whois", "technologies"]
            },
            {
                "name": "geoint",
                "title": "Geographic Intelligence",
                "description": "IP geolocation, address lookup, coordinate analysis",
                "location_types": ["ip_geo", "address", "coordinates", "satellite"]
            },
            {
                "name": "webint",
                "title": "Web Intelligence",
                "description": "Search engine intelligence, web crawling, dorking",
                "search_engines": ["google", "bing", "duckduckgo", "yandex"]
            }
        ]
    }