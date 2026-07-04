import os
import subprocess
import sys

# Ensure reportlab is installed
try:
    import reportlab
except ImportError:
    print("Installing reportlab to generate VSB PDF...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate():
    pdf_filename = "fee_structure.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter,
                            rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1e3a8a'), # VSB Blue Accent
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#2563eb'),
        spaceBefore=12,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=6
    )
    
    # Document Header
    story.append(Paragraph("<b>V.S.B. ENGINEERING COLLEGE, KARUR</b>", title_style))
    story.append(Paragraph("<b>Official Fee Structure & General Guidelines</b>", ParagraphStyle('Sub', parent=title_style, fontSize=12, leading=14, textColor=colors.HexColor('#4b5563'))))
    story.append(Paragraph("<b>Academic Year:</b> 2026-2027", ParagraphStyle('AY', parent=body_style, fontName='Helvetica-Bold', fontSize=10)))
    story.append(Spacer(1, 15))
    
    # Section 1: Undergraduate Departments
    story.append(Paragraph("1. Undergraduate Departments Offered", h2_style))
    story.append(Paragraph("The college offers undergraduate engineering and technology degrees in the following departments:", body_style))
    
    depts = [
        "• Artificial Intelligence and Data Science (AI&DS)",
        "• Artificial Intelligence and Machine Learning (AI&ML)",
        "• Bio Technology",
        "• Biomedical Engineering",
        "• Chemical Engineering",
        "• Civil Engineering",
        "• Computer and Communication Engineering (CCE)",
        "• Computer Science and Engineering (CSE)",
        "• Computer Science and Business Systems (CSBS)",
        "• Electrical and Electronics Engineering (EEE)",
        "• Electronics and Communication Engineering (ECE)",
        "• Information Technology (IT)",
        "• Mechanical Engineering"
    ]
    for dept in depts:
        story.append(Paragraph(dept, ParagraphStyle('BulletText', parent=body_style, leftIndent=15, spaceAfter=3)))
        
    story.append(Spacer(1, 10))
    
    # Section 2: Tuition Fees Quota Wise
    story.append(Paragraph("2. Annual Tuition Fees Structure", h2_style))
    story.append(Paragraph("Tuition fees are structured by quota allocation as detailed below:", body_style))
    
    quota_data = [
        ["Quota Type", "Annual Tuition Fee", "Description / Eligibility"],
        ["Government Quota", "₹55,000 / year", "Allocated through single-window TNEA counseling"],
        ["Management Quota", "₹87,500 / year", "Direct college administration admission quota"]
    ]
    
    t_quota = Table(quota_data, colWidths=[150, 150, 200])
    t_quota.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f3f4f6')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_quota)
    story.append(Spacer(1, 12))
    
    # Section 3: Additional Mandatory & Optional Fees
    story.append(Paragraph("3. Additional Fees Structure", h2_style))
    
    additional_data = [
        ["Fee Description", "Amount (₹)", "Frequency / Type"],
        ["Examination Fee", "₹2,500", "Annual / Academic Year"],
        ["Laboratory Fee", "₹3,000", "Annual / Academic Year"],
        ["Library Fee", "₹1,500", "Annual / Academic Year"],
        ["Development Fee", "₹5,000", "Annual / Academic Year"],
        ["Hostel Fee", "₹60,000", "Annual / Optional Accommodation Fee"],
        ["Transport Fee", "₹18,000", "Annual / Optional Commute Fee"]
    ]
    
    t_add = Table(additional_data, colWidths=[200, 120, 180])
    t_add.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f9fafb')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#e5e7eb')),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_add)
    story.append(Spacer(1, 12))
    
    # Section 4: Scholarships
    story.append(Paragraph("4. Available Scholarships", h2_style))
    story.append(Paragraph("Students can apply for the following scholarships based on eligibility constraints:", body_style))
    
    scholarships = [
        "1. <b>First Graduate Scholarship:</b> Available to students who are the first graduates in their family.",
        "2. <b>Merit Scholarship:</b> Awarded based on academic marks and performance criteria.",
        "3. <b>BC/MBC Scholarship:</b> Government welfare scheme scholarship for backward and most backward class students.",
        "4. <b>SC/ST Scholarship:</b> Government welfare scheme tuition waivers and post-matric scholarships for SC/ST students."
    ]
    for schol in scholarships:
        story.append(Paragraph(schol, ParagraphStyle('ScholText', parent=body_style, leftIndent=15, spaceAfter=4)))
        
    story.append(Spacer(1, 10))
    
    # Section 5: Contact
    story.append(Paragraph("5. College Contact Information", h2_style))
    story.append(Paragraph("For further clarification on payments or administrative rules, please contact:", body_style))
    story.append(Paragraph("<b>V.S.B. Engineering College</b>", ParagraphStyle('C1', parent=body_style, fontName='Helvetica-Bold')))
    story.append(Paragraph("NH-67 Covai Road, Karur, Tamil Nadu, India", body_style))
    
    doc.build(story)
    print(f"VSB Sample PDF successfully generated as {pdf_filename}")

if __name__ == "__main__":
    generate()
