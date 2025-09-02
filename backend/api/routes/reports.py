from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Optional
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import markdown

from database.connection import get_db
from database.models.user import User, Investigation
from api.routes.auth import get_current_user
from config.settings import settings

router = APIRouter()

def create_pdf_report(investigation: Investigation, results: list) -> str:
    """Create PDF report for investigation"""
    os.makedirs(settings.reports_path, exist_ok=True)
    filename = f"report_{investigation.uuid}.pdf"
    filepath = os.path.join(settings.reports_path, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.navy
    )
    story.append(Paragraph(f"H4WK5INT OSINT Report", title_style))
    story.append(Spacer(1, 20))
    
    # Investigation details
    story.append(Paragraph(f"<b>Investigation:</b> {investigation.title}", styles['Normal']))
    story.append(Paragraph(f"<b>Target:</b> {investigation.target}", styles['Normal']))
    story.append(Paragraph(f"<b>Type:</b> {investigation.target_type}", styles['Normal']))
    story.append(Paragraph(f"<b>Status:</b> {investigation.status}", styles['Normal']))
    story.append(Paragraph(f"<b>Created:</b> {investigation.created_at}", styles['Normal']))
    if investigation.description:
        story.append(Paragraph(f"<b>Description:</b> {investigation.description}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Results summary
    story.append(Paragraph("Results Summary", styles['Heading2']))
    story.append(Paragraph(f"Total results found: {len(results)}", styles['Normal']))
    
    # Group results by module
    modules = {}
    for result in results:
        if result.module_name not in modules:
            modules[result.module_name] = []
        modules[result.module_name].append(result)
    
    for module_name, module_results in modules.items():
        story.append(Spacer(1, 15))
        story.append(Paragraph(f"{module_name.upper()} Results ({len(module_results)} found)", styles['Heading3']))
        
        for result in module_results[:10]:  # Limit to first 10 results per module
            story.append(Paragraph(f"<b>Query:</b> {result.query}", styles['Normal']))
            story.append(Paragraph(f"<b>Type:</b> {result.result_type}", styles['Normal']))
            story.append(Paragraph(f"<b>Confidence:</b> {result.confidence_score}%", styles['Normal']))
            if result.source_url:
                story.append(Paragraph(f"<b>Source:</b> {result.source_url}", styles['Normal']))
            story.append(Spacer(1, 10))
    
    doc.build(story)
    return filepath

def create_markdown_report(investigation: Investigation, results: list) -> str:
    """Create Markdown report for investigation"""
    os.makedirs(settings.reports_path, exist_ok=True)
    filename = f"report_{investigation.uuid}.md"
    filepath = os.path.join(settings.reports_path, filename)
    
    content = f"""# H4WK5INT OSINT Report

## Investigation Details
- **Title**: {investigation.title}
- **Target**: {investigation.target}
- **Type**: {investigation.target_type}
- **Status**: {investigation.status}
- **Created**: {investigation.created_at}
- **Description**: {investigation.description or 'N/A'}

## Results Summary
Total results found: {len(results)}

"""
    
    # Group results by module
    modules = {}
    for result in results:
        if result.module_name not in modules:
            modules[result.module_name] = []
        modules[result.module_name].append(result)
    
    for module_name, module_results in modules.items():
        content += f"### {module_name.upper()} Results ({len(module_results)} found)\n\n"
        
        for result in module_results:
            content += f"#### {result.result_type}\n"
            content += f"- **Query**: {result.query}\n"
            content += f"- **Confidence**: {result.confidence_score}%\n"
            if result.source_url:
                content += f"- **Source**: {result.source_url}\n"
            content += f"- **Found**: {result.created_at}\n\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

def create_json_report(investigation: Investigation, results: list) -> str:
    """Create JSON report for investigation"""
    os.makedirs(settings.reports_path, exist_ok=True)
    filename = f"report_{investigation.uuid}.json"
    filepath = os.path.join(settings.reports_path, filename)
    
    report_data = {
        "investigation": {
            "id": investigation.id,
            "uuid": investigation.uuid,
            "title": investigation.title,
            "target": investigation.target,
            "target_type": investigation.target_type,
            "status": investigation.status,
            "priority": investigation.priority,
            "description": investigation.description,
            "created_at": investigation.created_at.isoformat() if investigation.created_at else None,
            "updated_at": investigation.updated_at.isoformat() if investigation.updated_at else None,
            "completed_at": investigation.completed_at.isoformat() if investigation.completed_at else None
        },
        "results": [
            {
                "id": result.id,
                "uuid": result.uuid,
                "module_name": result.module_name,
                "sub_module": result.sub_module,
                "query": result.query,
                "result_type": result.result_type,
                "data": result.data,
                "metadata": result.metadata,
                "confidence_score": result.confidence_score,
                "source_url": result.source_url,
                "created_at": result.created_at.isoformat() if result.created_at else None
            }
            for result in results
        ],
        "generated_at": datetime.utcnow().isoformat(),
        "total_results": len(results)
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    return filepath

@router.post("/generate/{investigation_id}")
async def generate_report(
    investigation_id: int,
    format: str = "pdf",  # pdf, markdown, json, html
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate investigation report"""
    # Get investigation
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.owner_id == current_user.id
    ).first()
    
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    # Get results
    results = investigation.results
    
    if not results:
        raise HTTPException(status_code=400, detail="No results found for this investigation")
    
    # Generate report based on format
    if format == "pdf":
        filepath = create_pdf_report(investigation, results)
    elif format == "markdown":
        filepath = create_markdown_report(investigation, results)
    elif format == "json":
        filepath = create_json_report(investigation, results)
    elif format == "html":
        # Create markdown first, then convert to HTML
        md_filepath = create_markdown_report(investigation, results)
        with open(md_filepath, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        html_content = markdown.markdown(md_content)
        filename = f"report_{investigation.uuid}.html"
        filepath = os.path.join(settings.reports_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>H4WK5INT OSINT Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #2c3e50; }}
                    h2 {{ color: #34495e; border-bottom: 2px solid #ecf0f1; }}
                    h3 {{ color: #7f8c8d; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
            {html_content}
            </body>
            </html>
            """)
    else:
        raise HTTPException(status_code=400, detail="Unsupported report format")
    
    return {
        "message": "Report generated successfully",
        "filepath": filepath,
        "filename": os.path.basename(filepath),
        "format": format
    }

@router.get("/download/{filename}")
async def download_report(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Download generated report"""
    filepath = os.path.join(settings.reports_path, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Read file content
    with open(filepath, 'rb') as f:
        content = f.read()
    
    # Determine content type
    if filename.endswith('.pdf'):
        media_type = 'application/pdf'
    elif filename.endswith('.json'):
        media_type = 'application/json'
    elif filename.endswith('.md'):
        media_type = 'text/markdown'
    elif filename.endswith('.html'):
        media_type = 'text/html'
    else:
        media_type = 'application/octet-stream'
    
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/list/{investigation_id}")
async def list_reports(
    investigation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List available reports for investigation"""
    # Verify investigation ownership
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.owner_id == current_user.id
    ).first()
    
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    # Find report files
    report_files = []
    if os.path.exists(settings.reports_path):
        for filename in os.listdir(settings.reports_path):
            if filename.startswith(f"report_{investigation.uuid}"):
                filepath = os.path.join(settings.reports_path, filename)
                stat = os.stat(filepath)
                report_files.append({
                    "filename": filename,
                    "format": filename.split('.')[-1],
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
    
    return {"reports": report_files}