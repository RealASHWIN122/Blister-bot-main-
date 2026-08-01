import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.units import inch

def build_pdf():
    pdf_path = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\vertical scoring mechanism\Vertical_Scoring_Report.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#0F172A")
    c_accent = colors.HexColor("#EA580C")
    c_dark = colors.HexColor("#1F2937")
    c_light_bg = colors.HexColor("#FFF7ED")

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
        textColor=colors.HexColor("#FFEDD5"),
        alignment=1,
        spaceAfter=4
    )

    style_h1 = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_accent,
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

    # Header Banner
    header_data = [
        [Paragraph("VERTICAL STRIP PLUNGER EJECTION REPORT", style_title)],
        [Paragraph("PROJECT BLISTER BOT — VERTICAL 2-AXIS CNC & PLUNGER DYNAMICS", style_subtitle)]
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
            Paragraph("<b>Module:</b> Vertical Scoring Mechanism", style_body),
            Paragraph("<b>Strip Orientation:</b> Vertical (Cartridge)", style_body),
            Paragraph("<b>Plunger Action:</b> Horizontal Push", style_body)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[2.6*inch, 2.7*inch, 2.2*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light_bg),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#FED7AA")),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 8))

    # Section 1
    elements.append(Paragraph("1. Mechanical Innovation: Vertical Strip & Horizontal Plunger Ejection", style_h1))
    elements.append(HRFlowable(width="100%", thickness=1.2, color=c_accent, spaceBefore=1, spaceAfter=6))
    
    elements.append(Paragraph(
        "In <b>Blister Bot</b>, medicine blister strips are held vertically inside multi-slot cartridges. "
        "The deblistering toolhead operates on a vertical 2-axis CNC gantry behind the vertical foil sheet. "
        "The motorized rotary cutter wheel scores a 270-degree U-shaped flap in the vertical foil card. "
        "A soft silicone plunger pin then extends horizontally (+Z direction) through the vertical strip, pushing the capsule tablet out of the front PVC bubble so it drops into the slanted delivery chute below.",
        style_body
    ))

    # Section 2: Still Previews
    elements.append(Paragraph("2. Rendered 3D Kinematic Previews", style_h1))
    elements.append(HRFlowable(width="100%", thickness=1.2, color=c_accent, spaceBefore=1, spaceAfter=6))

    img1 = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\vertical scoring mechanism\vertical_strip_toolhead.png"
    img2 = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\vertical scoring mechanism\vertical_u_flap.png"
    img3 = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\vertical scoring mechanism\vertical_plunger_eject.png"

    if os.path.exists(img1) and os.path.exists(img2) and os.path.exists(img3):
        imgs_data = [
            [
                Image(img1, width=2.3*inch, height=1.3*inch),
                Image(img2, width=2.3*inch, height=1.3*inch),
                Image(img3, width=2.3*inch, height=1.3*inch),
            ],
            [
                Paragraph("<b>Phase 1:</b> Vertical Align", style_caption),
                Paragraph("<b>Phase 3:</b> 270° Vertical U-Flap", style_caption),
                Paragraph("<b>Phase 5:</b> Horizontal Plunger Eject", style_caption),
            ]
        ]
        imgs_table = Table(imgs_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
        imgs_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('PADDING', (0,0), (-1,-1), 2)]))
        elements.append(imgs_table)

    # Section 3: Kinematic Steps
    elements.append(Paragraph("3. Kinematic Sequence Parameters", style_h1))
    elements.append(HRFlowable(width="100%", thickness=1.2, color=c_accent, spaceBefore=1, spaceAfter=6))

    elements.append(Paragraph("• <b>Step 1 (Vertical Align):</b> Gantry positions toolhead carriage vertically (Y) and horizontally (X) over target bubble.", style_bullet))
    elements.append(Paragraph("• <b>Step 2 (Blade Engage):</b> Rotary cutter wheel engages forward onto vertical foil backing.", style_bullet))
    elements.append(Paragraph("• <b>Step 3 (270° U-Scoring):</b> Cutter traverses 3-sided U-path, leaving top edge uncut to form hinged aluminum flap.", style_bullet))
    elements.append(Paragraph("• <b>Step 4 (Open Foil Flap):</b> Cutter retracts; vertical aluminum flap swings open 75°.", style_bullet))
    elements.append(Paragraph("• <b>Step 5 (Horizontal Plunger Eject):</b> Silicone plunger pin extends horizontally 14mm, pushing capsule tablet out into slanted chute.", style_bullet))

    # Section 4: File Inventory
    elements.append(Paragraph("4. Vertical Scoring Folder Inventory (`vertical scoring mechanism/`)", style_h1))
    elements.append(HRFlowable(width="100%", thickness=1.2, color=c_accent, spaceBefore=1, spaceAfter=6))

    inv_data = [
        [Paragraph("<b>File Name</b>", style_body), Paragraph("<b>Function / Purpose</b>", style_body)],
        [Paragraph("<b>vertical_strip_plunger_animation.html</b>", style_body), Paragraph("Interactive 3D WebGL Three.js animation web app for vertical strip ejection.", style_body)],
        [Paragraph("<b>vertical_strip_ejection_demo.mp4</b>", style_body), Paragraph("Generated MP4 animation video showing vertical scoring & plunger ejection.", style_body)],
        [Paragraph("<b>vertical_scoring_mechanism.blend</b>", style_body), Paragraph("Native 3D Blender project model file (vertical strip orientation).", style_body)],
        [Paragraph("<b>animate_vertical_scoring.py</b>", style_body), Paragraph("Blender Python script for 3D model generation & keyframe rendering.", style_body)],
        [Paragraph("<b>encode_vertical_mp4.py</b>", style_body), Paragraph("OpenCV Python script encoding PNG frames to MP4 video format.", style_body)],
        [Paragraph("<b>Vertical_Scoring_Report.pdf</b>", style_body), Paragraph("Publication-ready PDF documentation report.", style_body)],
    ]
    inv_table = Table(inv_data, colWidths=[3.2*inch, 4.3*inch])
    inv_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#FED7AA")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#FDBA74")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(inv_table)

    doc.build(elements)
    print(f"Successfully generated Vertical Scoring PDF Report: {pdf_path}")

if __name__ == "__main__":
    build_pdf()
