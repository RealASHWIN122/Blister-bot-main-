import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak
from reportlab.lib.units import inch

def build_pdf():
    pdf_path = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\scoring mechanism\Scoring_Mechanism_Report.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#0F172A")   # Slate dark
    c_secondary = colors.HexColor("#2563EB") # Royal blue accent
    c_dark = colors.HexColor("#1F2937")      # Body text
    c_light_bg = colors.HexColor("#F8FAFC")  # Light gray

    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.white,
        alignment=1,
        spaceAfter=4
    )

    style_subtitle = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor("#93C5FD"),
        alignment=1,
        spaceAfter=4
    )

    style_h1 = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_secondary,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=5
    )

    style_bullet = ParagraphStyle(
        'Bullet_Custom',
        parent=style_body,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    style_caption = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceBefore=2,
        spaceAfter=6
    )

    elements = []

    # Banner
    header_data = [
        [Paragraph("BLISTER BOT: STRIP SCORING & EJECTIONS REPORT", style_title)],
        [Paragraph("MECHANICAL DESIGN, KINEMATIC TRAJECTORIES, AND FIRMWARE LOGIC", style_subtitle)]
    ]
    header_table = Table(header_data, colWidths=[7.5*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8))

    # Meta
    meta_data = [
        [
            Paragraph("<b>Module:</b> Scoring & Ejection Mechanism", style_body),
            Paragraph("<b>Target Core:</b> STM32U585 MCU + Dragonwing MPU", style_body),
            Paragraph("<b>Output:</b> 270° U-Flap + Silicone Plunger", style_body)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[2.5*inch, 3.2*inch, 1.8*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light_bg),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 8))

    # Section 1
    elements.append(Paragraph("1. Mechanical Innovation: 270-Degree U-Shaped Scoring", style_h1))
    elements.append(HRFlowable(width="100%", thickness=1.2, color=c_secondary, spaceBefore=1, spaceAfter=6))
    
    elements.append(Paragraph(
        "Conventional automated medicine dispensers crush fragile tablets because they rely on high-force mechanical punching. "
        "Blister Bot eliminates this risk by using a motorized rotary cutter wheel to score a precise 270-degree U-shaped cut in the aluminum foil backing, "
        "leaving a hinged flap connected at the top edge. A soft silicone plunger pin then pushes the tablet through the open flap.",
        style_body
    ))

    # Section 2: Render Stills
    elements.append(Paragraph("2. 3D Kinematic Simulation Stills", style_h1))
    elements.append(HRFlowable(width="100%", thickness=1.2, color=c_secondary, spaceBefore=1, spaceAfter=6))

    img_s1 = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\scoring mechanism\scoring_toolhead.png"
    img_s2 = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\scoring mechanism\u_flap_scored.png"
    img_s3 = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\scoring mechanism\tablet_ejection.png"

    # Check if images exist yet
    imgs_ready = os.path.exists(img_s1) and os.path.exists(img_s2) and os.path.exists(img_s3)
    
    if imgs_ready:
        stills_table_data = [
            [
                Image(img_s1, width=2.3*inch, height=1.3*inch),
                Image(img_s2, width=2.3*inch, height=1.3*inch),
                Image(img_s3, width=2.3*inch, height=1.3*inch),
            ],
            [
                Paragraph("<b>Step 1:</b> Toolhead Approach", style_caption),
                Paragraph("<b>Step 2:</b> 270° U-Flap Scored", style_caption),
                Paragraph("<b>Step 3:</b> Silicone Plunger Ejection", style_caption),
            ]
        ]
        stills_table = Table(stills_table_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
        stills_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 2),
        ]))
        elements.append(stills_table)

    # Section 3: Mathematics & Transformations
    elements.append(Paragraph("3. Front-to-Back Coordinate Mapping & Waypoint Generation", style_h1))
    elements.append(HRFlowable(width="100%", thickness=1.2, color=c_secondary, spaceBefore=1, spaceAfter=6))

    elements.append(Paragraph("• <b>Camera-to-Gantry Transformation:</b> X_gantry = (X_pixel * 0.45) + 12.0 mm, Y_gantry = (Y_pixel * 0.45) + 8.5 mm.", style_bullet))
    elements.append(Paragraph("• <b>Dynamic Clearance Margin:</b> R_cut = R_pill + 2.0 mm safety buffer.", style_bullet))
    elements.append(Paragraph("• <b>270° Trajectory Traversal:</b> P1 (Top-Left Approach) -> P2 (Bottom-Left) -> P3 (Bottom-Right) -> P4 (Top-Right Exit). Top horizontal edge remains uncut.", style_bullet))

    # Section 4: File Inventory
    elements.append(Paragraph("4. Module Deliverables Inventory", style_h1))
    elements.append(HRFlowable(width="100%", thickness=1.2, color=c_secondary, spaceBefore=1, spaceAfter=6))

    inv_data = [
        [Paragraph("<b>Deliverable File</b>", style_body), Paragraph("<b>Function / Purpose</b>", style_body)],
        [Paragraph("<b>deblister_vision_mapper.py</b>", style_body), Paragraph("Python vision coordinate mapper and 270° U-trajectory generator.", style_body)],
        [Paragraph("<b>scoring_gantry_controller.ino</b>", style_body), Paragraph("Arduino C++ sketch for real-time STM32 MCU stepper motion & solenoid actuation.", style_body)],
        [Paragraph("<b>animate_scoring_mechanism.py</b>", style_body), Paragraph("Blender 5.2 Python script animating toolhead, U-flap opening, plunger, and MP4 video.", style_body)],
        [Paragraph("<b>scoring_mechanism.blend</b>", style_body), Paragraph("Specialized 3D kinematic model file.", style_body)],
        [Paragraph("<b>scoring_mechanism_demo.mp4</b>", style_body), Paragraph("Rendered 120-frame MP4 animation video demonstration.", style_body)],
        [Paragraph("<b>Scoring_Mechanism_DeepDive.md</b>", style_body), Paragraph("Technical deep-dive markdown documentation.", style_body)],
    ]
    inv_table = Table(inv_data, colWidths=[3.0*inch, 4.5*inch])
    inv_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(inv_table)

    doc.build(elements)
    print(f"Successfully generated Scoring Mechanism PDF Report: {pdf_path}")

if __name__ == "__main__":
    build_pdf()
