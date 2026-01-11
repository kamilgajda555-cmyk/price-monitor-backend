from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import io
import csv
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from app.models.database import get_db
from app.models.models import Product, PriceHistory, Source
from app.schemas.schemas import ReportRequest
from app.api.auth import get_current_user

router = APIRouter()

@router.post("/generate")
def generate_report(
    report_request: ReportRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate and download report in specified format"""
    
    if report_request.report_type == "products":
        data = _get_products_report_data(db, report_request)
    elif report_request.report_type == "price_changes":
        data = _get_price_changes_report_data(db, report_request)
    elif report_request.report_type == "sources":
        data = _get_sources_report_data(db, report_request)
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    if report_request.format == "csv":
        return _generate_csv(data, report_request.report_type)
    elif report_request.format == "excel":
        return _generate_excel(data, report_request.report_type)
    elif report_request.format == "pdf":
        return _generate_pdf(data, report_request.report_type)
    else:
        raise HTTPException(status_code=400, detail="Invalid format")

def _get_products_report_data(db: Session, report_request: ReportRequest):
    """Get products data for report"""
    query = db.query(Product)
    
    if report_request.filters:
        if report_request.filters.get("category"):
            query = query.filter(Product.category == report_request.filters["category"])
        if report_request.filters.get("is_active") is not None:
            query = query.filter(Product.is_active == report_request.filters["is_active"])
    
    products = query.all()
    
    data = []
    for product in products:
        # Get latest price
        latest_price = db.query(PriceHistory).filter(
            PriceHistory.product_id == product.id
        ).order_by(PriceHistory.checked_at.desc()).first()
        
        data.append({
            "ID": product.id,
            "Name": product.name,
            "SKU": product.sku or "",
            "EAN": product.ean or "",
            "Category": product.category or "",
            "Brand": product.brand or "",
            "Base Price": product.base_price or 0,
            "Latest Price": latest_price.price if latest_price else 0,
            "Active": "Yes" if product.is_active else "No",
            "Created": product.created_at.strftime("%Y-%m-%d")
        })
    
    return data

def _get_price_changes_report_data(db: Session, report_request: ReportRequest):
    """Get price changes data for report"""
    date_from = report_request.date_from or (datetime.utcnow() - timedelta(days=30))
    date_to = report_request.date_to or datetime.utcnow()
    
    price_history = db.query(
        PriceHistory, Product.name, Source.name.label("source_name")
    ).join(Product).join(Source).filter(
        PriceHistory.checked_at.between(date_from, date_to)
    ).order_by(PriceHistory.checked_at.desc()).all()
    
    data = []
    for history, product_name, source_name in price_history:
        data.append({
            "Product": product_name,
            "Source": source_name,
            "Price": history.price,
            "Currency": history.currency,
            "Available": "Yes" if history.availability else "No",
            "Checked At": history.checked_at.strftime("%Y-%m-%d %H:%M")
        })
    
    return data

def _get_sources_report_data(db: Session, report_request: ReportRequest):
    """Get sources data for report"""
    sources = db.query(Source).all()
    
    data = []
    for source in sources:
        # Count products for this source
        product_count = db.query(PriceHistory).filter(
            PriceHistory.source_id == source.id
        ).distinct(PriceHistory.product_id).count()
        
        data.append({
            "ID": source.id,
            "Name": source.name,
            "Type": source.type or "",
            "Base URL": source.base_url or "",
            "Products": product_count,
            "Active": "Yes" if source.is_active else "No",
            "Created": source.created_at.strftime("%Y-%m-%d")
        })
    
    return data

def _generate_csv(data, report_type):
    """Generate CSV file"""
    if not data:
        raise HTTPException(status_code=404, detail="No data to export")
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={report_type}_{datetime.now().strftime('%Y%m%d')}.csv"}
    )

def _generate_excel(data, report_type):
    """Generate Excel file"""
    if not data:
        raise HTTPException(status_code=404, detail="No data to export")
    
    df = pd.DataFrame(data)
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=report_type, index=False)
    
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={report_type}_{datetime.now().strftime('%Y%m%d')}.xlsx"}
    )

def _generate_pdf(data, report_type):
    """Generate PDF file"""
    if not data:
        raise HTTPException(status_code=404, detail="No data to export")
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Title
    styles = getSampleStyleSheet()
    title = Paragraph(f"{report_type.replace('_', ' ').title()} Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Date
    date_text = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal'])
    elements.append(date_text)
    elements.append(Spacer(1, 12))
    
    # Table
    table_data = [list(data[0].keys())]
    for row in data:
        table_data.append([str(v) for v in row.values()])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={report_type}_{datetime.now().strftime('%Y%m%d')}.pdf"}
    )
