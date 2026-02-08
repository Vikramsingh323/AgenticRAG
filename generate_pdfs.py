#!/usr/bin/env python
"""Generate sample PDF documents for testing"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import os

# Create doc_dump folder if it doesn't exist
os.makedirs('doc_dump', exist_ok=True)

# Get default styles
styles = getSampleStyleSheet()

# Custom title style
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor='#1f4788',
    spaceAfter=30,
    alignment=1
)

# PDF 1: Technical Documentation
pdf_path1 = 'doc_dump/technical_guide.pdf'
doc1 = SimpleDocTemplate(pdf_path1, pagesize=letter)
story1 = []

story1.append(Paragraph("Technical Integration Guide", title_style))
story1.append(Spacer(1, 0.3*inch))
story1.append(Paragraph("Introduction", styles['Heading2']))
story1.append(Paragraph(
    "This document provides a comprehensive guide for integrating various systems and APIs. "
    "It covers installation, configuration, and best practices for developers.",
    styles['Normal']
))
story1.append(Spacer(1, 0.2*inch))
story1.append(Paragraph("Getting Started", styles['Heading2']))
story1.append(Paragraph(
    "Step 1: Install required dependencies<br/>"
    "Step 2: Configure API keys<br/>"
    "Step 3: Initialize the system<br/>"
    "Step 4: Run test cases",
    styles['Normal']
))

doc1.build(story1)
print(f"✓ Created {pdf_path1}")

# PDF 2: Business Report
pdf_path2 = 'doc_dump/quarterly_report.pdf'
doc2 = SimpleDocTemplate(pdf_path2, pagesize=letter)
story2 = []

story2.append(Paragraph("Q4 2025 Business Report", title_style))
story2.append(Spacer(1, 0.3*inch))
story2.append(Paragraph("Executive Summary", styles['Heading2']))
story2.append(Paragraph(
    "This report summarizes the performance metrics and strategic initiatives completed "
    "during the fourth quarter of 2025.",
    styles['Normal']
))
story2.append(Spacer(1, 0.2*inch))
story2.append(Paragraph("Key Metrics", styles['Heading2']))
story2.append(Paragraph(
    "Revenue Growth: +25%<br/>"
    "Customer Acquisition: 150 new clients<br/>"
    "Product Launches: 3 new features<br/>"
    "Team Expansion: 12 new hires",
    styles['Normal']
))
story2.append(Spacer(1, 0.2*inch))
story2.append(Paragraph("Conclusion", styles['Heading2']))
story2.append(Paragraph(
    "The quarter demonstrated strong growth across all business segments with "
    "successful product launches and market expansion.",
    styles['Normal']
))

doc2.build(story2)
print(f"✓ Created {pdf_path2}")

# PDF 3: User Manual
pdf_path3 = 'doc_dump/user_manual.pdf'
doc3 = SimpleDocTemplate(pdf_path3, pagesize=letter)
story3 = []

story3.append(Paragraph("Software User Manual", title_style))
story3.append(Spacer(1, 0.3*inch))
story3.append(Paragraph("System Requirements", styles['Heading2']))
story3.append(Paragraph(
    "Operating System: Windows 10+, macOS 10.14+, Ubuntu 18.04+<br/>"
    "RAM: Minimum 4GB (8GB recommended)<br/>"
    "Storage: 2GB free disk space<br/>"
    "Internet: Broadband connection required",
    styles['Normal']
))
story3.append(Spacer(1, 0.2*inch))
story3.append(Paragraph("Installation Instructions", styles['Heading2']))
story3.append(Paragraph(
    "1. Download the installer from the official website<br/>"
    "2. Run the installer and follow the setup wizard<br/>"
    "3. Accept the license agreement<br/>"
    "4. Choose installation directory<br/>"
    "5. Click Install and wait for completion",
    styles['Normal']
))
story3.append(Spacer(1, 0.2*inch))
story3.append(Paragraph("Getting Help", styles['Heading2']))
story3.append(Paragraph(
    "For support, visit our documentation portal or contact support@example.com",
    styles['Normal']
))

doc3.build(story3)
print(f"✓ Created {pdf_path3}")

print("\nAll PDFs generated successfully in doc_dump folder!")
