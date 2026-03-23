from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime
from app.utils.logger import logger
import os

try:
    font_path = r"C:\Windows\Fonts\msyh.ttc"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('MicrosoftYaHei', font_path))
        FONT_NAME = 'MicrosoftYaHei'
    else:
        FONT_NAME = 'Helvetica'
except Exception as e:
    logger.warning(f"Could not register Chinese font: {e}")
    FONT_NAME = 'Helvetica'


class ApprovalPDFGenerator:
    def __init__(self):
        self.primary_color = HexColor("#1a56db")
        self.secondary_color = HexColor("#374151")
        self.header_bg = HexColor("#f3f4f6")
        self.border_color = HexColor("#d1d5db")

    def generate_approval_pdf(self, approval_data: Dict[str, Any]) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Title_CN',
            fontName=FONT_NAME,
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=self.primary_color
        ))
        styles.add(ParagraphStyle(
            name='Section_CN',
            fontName=FONT_NAME,
            fontSize=12,
            spaceAfter=8,
            spaceBefore=15,
            textColor=self.primary_color
        ))
        styles.add(ParagraphStyle(
            name='Normal_CN',
            fontName=FONT_NAME,
            fontSize=10,
            spaceAfter=5,
            textColor=self.secondary_color
        ))

        story = []

        story.append(Paragraph("Business Trip Approval Form", styles['Title_CN']))
        story.append(Spacer(1, 10))

        form_info = approval_data.get("form_info", {})
        basic_info = approval_data.get("basic_info", {})
        trip_details = approval_data.get("trip_details", {})
        cost_summary = approval_data.get("cost_summary", {})
        approval_chain = approval_data.get("approval_chain", [])

        story.append(Paragraph("1. Basic Information", styles['Section_CN']))
        basic_data = [
            ["Employee Name:", basic_info.get("employee_name", "N/A")],
            ["User Level:", basic_info.get("user_level", "N/A")],
            ["Department:", basic_info.get("department", "N/A")],
            ["Purpose:", basic_info.get("purpose", "N/A")],
        ]
        basic_table = Table(basic_data, colWidths=[80*mm, 90*mm])
        basic_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), self.secondary_color),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(basic_table)
        story.append(Spacer(1, 10))

        story.append(Paragraph("2. Trip Details", styles['Section_CN']))
        trip_data = [
            ["Departure:", trip_details.get("departure", "N/A")],
            ["Destination:", trip_details.get("destination", "N/A")],
            ["Start Date:", trip_details.get("start_date", "N/A")],
            ["End Date:", trip_details.get("end_date", "N/A")],
        ]
        trip_table = Table(trip_data, colWidths=[80*mm, 90*mm])
        trip_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), self.secondary_color),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(trip_table)
        story.append(Spacer(1, 10))

        story.append(Paragraph("3. Cost Summary", styles['Section_CN']))
        cost_data = [
            ["Item", "Amount (CNY)", "Remarks"],
            ["Transport", f"{cost_summary.get('transport', 0):.2f}", "Flight/Train"],
            ["Hotel", f"{cost_summary.get('hotel', 0):.2f}", "Accommodation"],
            ["Dining", f"{cost_summary.get('dining', 0):.2f}", "Meals/Entertainment"],
            ["Total", f"{cost_summary.get('total', 0):.2f}", ""],
        ]
        cost_table = Table(cost_data, colWidths=[50*mm, 40*mm, 80*mm])
        cost_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), self.header_bg),
            ('BACKGROUND', (0, -1), (-1, -1), self.header_bg),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.border_color),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(cost_table)
        story.append(Spacer(1, 15))

        story.append(Paragraph("4. Approval Chain", styles['Section_CN']))
        if approval_chain:
            chain_text = " -> ".join(approval_chain)
            story.append(Paragraph(chain_text, styles['Normal_CN']))
        else:
            story.append(Paragraph("No approval information", styles['Normal_CN']))
        story.append(Spacer(1, 20))

        story.append(Paragraph("5. Signatures", styles['Section_CN']))
        sign_data = [
            ["Applicant Signature:", "________________", "Date:", "________________"],
            ["Approver Signature:", "________________", "Date:", "________________"],
        ]
        sign_table = Table(sign_data, colWidths=[40*mm, 35*mm, 30*mm, 35*mm])
        sign_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(sign_table)
        story.append(Spacer(1, 30))

        footer_text = f"Generated by Intelligent Business Travel Assistant | Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(footer_text, styles['Normal_CN']))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(f"Generated approval PDF, size: {len(pdf_bytes)} bytes")
        return pdf_bytes

    def generate_html(self, approval_data: Dict[str, Any]) -> str:
        basic_info = approval_data.get("basic_info", {})
        trip_details = approval_data.get("trip_details", {})
        cost_summary = approval_data.get("cost_summary", {})
        approval_chain = approval_data.get("approval_chain", [])

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Business Trip Approval Form</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ text-align: center; color: #1a56db; }}
        h2 {{ color: #1a56db; border-bottom: 2px solid #1a56db; padding-bottom: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #d1d5db; padding: 10px; text-align: left; }}
        th {{ background-color: #f3f4f6; font-weight: bold; }}
        .total {{ background-color: #f3f4f6; font-weight: bold; }}
        .signature {{ margin-top: 30px; }}
        .footer {{ text-align: center; color: #6b7280; margin-top: 40px; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>Business Trip Approval Form</h1>

    <h2>1. Basic Information</h2>
    <table>
        <tr><th width="20%">Employee Name</th><td width="30%">{basic_info.get('employee_name', 'N/A')}</td>
            <th width="20%">User Level</th><td width="30%">{basic_info.get('user_level', 'N/A')}</td></tr>
        <tr><th>Department</th><td>{basic_info.get('department', 'N/A')}</td>
            <th>Purpose</th><td>{basic_info.get('purpose', 'N/A')}</td></tr>
    </table>

    <h2>2. Trip Details</h2>
    <table>
        <tr><th width="20%">Departure</th><td width="30%">{trip_details.get('departure', 'N/A')}</td>
            <th width="20%">Destination</th><td width="30%">{trip_details.get('destination', 'N/A')}</td></tr>
        <tr><th>Start Date</th><td>{trip_details.get('start_date', 'N/A')}</td>
            <th>End Date</th><td>{trip_details.get('end_date', 'N/A')}</td></tr>
    </table>

    <h2>3. Cost Summary</h2>
    <table>
        <tr><th>Item</th><th>Amount (CNY)</th><th>Remarks</th></tr>
        <tr><td>Transport</td><td>{cost_summary.get('transport', 0):.2f}</td><td>Flight/Train</td></tr>
        <tr><td>Hotel</td><td>{cost_summary.get('hotel', 0):.2f}</td><td>Accommodation</td></tr>
        <tr><td>Dining</td><td>{cost_summary.get('dining', 0):.2f}</td><td>Meals/Entertainment</td></tr>
        <tr class="total"><td>Total</td><td colspan="2">{cost_summary.get('total', 0):.2f}</td></tr>
    </table>

    <h2>4. Approval Chain</h2>
    <p>{' -> '.join(approval_chain) if approval_chain else 'No approval information'}</p>

    <div class="signature">
        <h2>5. Signatures</h2>
        <table>
            <tr><th width="15%">Applicant Signature</th><td width="35%">________________</td>
                <th width="15%">Date</th><td width="35%">________________</td></tr>
            <tr><th>Approver Signature</th><td>________________</td>
                <th>Date</th><td>________________</td></tr>
        </table>
    </div>

    <div class="footer">
        Generated by Intelligent Business Travel Assistant | Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
</body>
</html>
        """
        return html


pdf_generator = ApprovalPDFGenerator()