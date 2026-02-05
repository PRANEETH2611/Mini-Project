from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import pandas as pd
import io
from datetime import datetime

def generate_pdf_report(df):
    """
    Generate a PDF report from the dataframe.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Title
    elements.append(Paragraph("AIOps Incident Report", title_style))
    elements.append(Spacer(1, 12))
    
    # Date
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 24))
    
    # Executive Summary
    total_records = len(df)
    alerts_count = int((df["alert_status"] == "ALERT").sum())
    
    elements.append(Paragraph("Executive Summary", heading_style))
    elements.append(Paragraph(f"Total Records Analyzed: {total_records}", normal_style))
    elements.append(Paragraph(f"Total Alerts Detected: {alerts_count}", normal_style))
    elements.append(Spacer(1, 12))

    if alerts_count > 0:
        alert_rate = (alerts_count / total_records) * 100
        elements.append(Paragraph(f"Alert Rate: {alert_rate:.2f}%", normal_style))
    else:
        elements.append(Paragraph("System Health: Optimal", normal_style))
        
    elements.append(Spacer(1, 24))
    
    # Recent Incidents Table
    elements.append(Paragraph("Recent Critical Incidents (Top 10)", heading_style))
    elements.append(Spacer(1, 12))
    
    alerts_df = df[df["alert_status"] == "ALERT"].tail(10)
    
    if not alerts_df.empty:
        # Prepare table data
        data = [['Timestamp', 'Root Cause', 'Confidence', 'Action']]
        
        for _, row in alerts_df.iterrows():
            data.append([
                str(row['timestamp']),
                row['predicted_root_cause'],
                f"{row['failure_probability']:.2%}",
                row['recommended_action']
            ])
            
        t = Table(data, colWidths=[120, 100, 80, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("No critical incidents found in the analyzed period.", normal_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
