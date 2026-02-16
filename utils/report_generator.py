"""
PDF Report Generator for GeoVision
Generates professional PDF reports for LULC, Change Detection, and Risk Assessment
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
import matplotlib.pyplot as plt
import numpy as np

class GeoVisionReportGenerator:
    """Generate professional PDF reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=12
        )
    
    def generate_lulc_report(self, location_name, classification_result, satellite_image=None):
        """Generate LULC classification report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("GeoVision Land Cover Classification Report", self.title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Location and Date
        story.append(Paragraph(f"<b>Location:</b> {location_name}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Classification Result
        story.append(Paragraph("Classification Results", self.heading_style))
        predicted_class = classification_result['predicted_class']
        confidence = classification_result['confidence']
        description = classification_result['description']
        
        result_data = [
            ['Predicted Class', predicted_class],
            ['Confidence', f"{confidence*100:.2f}%"],
            ['Description', description]
        ]
        
        result_table = Table(result_data, colWidths=[2*inch, 4*inch])
        result_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(result_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Top 3 Predictions
        story.append(Paragraph("Top 3 Predictions", self.heading_style))
        top_3_data = [['Rank', 'Class', 'Confidence']]
        for i, pred in enumerate(classification_result['top_3_predictions'], 1):
            top_3_data.append([str(i), pred['class'], f"{pred['confidence']*100:.2f}%"])
        
        top_3_table = Table(top_3_data, colWidths=[1*inch, 3*inch, 2*inch])
        top_3_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(top_3_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_change_detection_report(self, location_name, change_results, start_date, end_date):
        """Generate change detection report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("GeoVision Change Detection Report", self.title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Location and Dates
        story.append(Paragraph(f"<b>Location:</b> {location_name}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Analysis Period:</b> {start_date} to {end_date}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        story.append(Paragraph("Summary", self.heading_style))
        ndvi_stats = change_results['statistics']['ndvi']
        ndbi_stats = change_results['statistics']['ndbi']
        ndmi_stats = change_results['statistics']['ndmi']
        
        veg_change = ndvi_stats['vegetation_gain'] - ndvi_stats['vegetation_loss']
        urban_change = ndbi_stats['urban_expansion'] - ndbi_stats['urban_reduction']
        moisture_change = ndmi_stats['moisture_gain'] - ndmi_stats['moisture_loss']
        
        summary_text = f"""
        <b>Vegetation Change:</b> {veg_change:+.1f}% ({'Increase' if veg_change > 0 else 'Decrease'})<br/>
        <b>Urban Development:</b> {urban_change:+.1f}% ({'Expansion' if urban_change > 0 else 'Reduction'})<br/>
        <b>Moisture Change:</b> {moisture_change:+.1f}% ({'Increase' if moisture_change > 0 else 'Decrease'})
        """
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Detailed Statistics
        story.append(Paragraph("Detailed Statistics", self.heading_style))
        
        stats_data = [
            ['Index', 'Metric', 'Value'],
            ['NDVI', 'Vegetation Gain', f"{ndvi_stats['vegetation_gain']:.2f}%"],
            ['', 'Vegetation Loss', f"{ndvi_stats['vegetation_loss']:.2f}%"],
            ['NDBI', 'Urban Expansion', f"{ndbi_stats['urban_expansion']:.2f}%"],
            ['', 'Urban Reduction', f"{ndbi_stats['urban_reduction']:.2f}%"],
            ['NDMI', 'Moisture Gain', f"{ndmi_stats['moisture_gain']:.2f}%"],
            ['', 'Moisture Loss', f"{ndmi_stats['moisture_loss']:.2f}%"]
        ]
        
        stats_table = Table(stats_data, colWidths=[1.5*inch, 2.5*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(stats_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_risk_assessment_report(self, location_name, risk_data, weather_data):
        """Generate risk assessment report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("GeoVision Risk Assessment Report", self.title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Location and Date
        story.append(Paragraph(f"<b>Location:</b> {location_name}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Risk Score
        story.append(Paragraph("Overall Risk Assessment", self.heading_style))
        risk_score = risk_data['risk_score']
        risk_level = risk_data['risk_level']
        
        risk_text = f"""
        <b>Risk Score:</b> {risk_score}/100<br/>
        <b>Risk Level:</b> {risk_level}
        """
        story.append(Paragraph(risk_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Current Weather
        story.append(Paragraph("Current Weather Conditions", self.heading_style))
        weather_text = f"""
        <b>Temperature:</b> {weather_data.get('temperature', 'N/A')}°C<br/>
        <b>Humidity:</b> {weather_data.get('humidity', 'N/A')}%<br/>
        <b>Wind Speed:</b> {weather_data.get('wind_speed', 'N/A')} m/s<br/>
        <b>Conditions:</b> {weather_data.get('weather_description', 'N/A')}
        """
        story.append(Paragraph(weather_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Risk Factors
        story.append(Paragraph("Risk Factors", self.heading_style))
        factors_data = [['Factor', 'Severity', 'Description']]
        for factor in risk_data.get('factors', []):
            factors_data.append([
                factor.get('name', 'Unknown'),
                factor.get('severity', 'Unknown'),
                factor.get('description', 'No description')[:50] + '...'
            ])
        
        if len(factors_data) > 1:
            factors_table = Table(factors_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
            factors_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(factors_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
