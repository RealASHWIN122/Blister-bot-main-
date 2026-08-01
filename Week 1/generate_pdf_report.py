import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, KeepTogether, PageBreak
from reportlab.lib.units import inch

def build_pdf():
    pdf_path = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\Week1_Documentation.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#1A365D")   # Deep navy blue
    c_secondary = colors.HexColor("#0D9488") # Teal accent
    c_dark = colors.HexColor("#1F2937")      # Charcoal dark text
    c_light_bg = colors.HexColor("#F3F4F6")  # Soft light grey background

    # Custom Styles
    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.white,
        alignment=1, # Center
        spaceAfter=6
    )

    style_subtitle = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#E2E8F0"),
        alignment=1,
        spaceAfter=4
    )

    style_h1 = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_dark,
        spaceAfter=6
    )

    style_bullet = ParagraphStyle(
        'Bullet_Custom',
        parent=style_body,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    style_caption = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#4B5563"),
        alignment=1,
        spaceBefore=3,
        spaceAfter=8
    )

    elements = []

    # --- COVER HEADER BANNER ---
    header_data = [
        [Paragraph("INTELLIGENT EDGE-AI MEDICINE DISPENSER", style_title)],
        [Paragraph("PROJECT BLISTER BOT — WEEK 1 TECHNICAL DOCUMENTATION & 3D MODEL REPORT", style_subtitle)]
    ]
    header_table = Table(header_data, colWidths=[7.5*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))

    # --- METADATA BAR ---
    meta_data = [
        [
            Paragraph("<b>Project:</b> Blister Bot (LLM Dispenser)", style_body),
            Paragraph("<b>Platform:</b> Arduino UNO Q (Linux + STM32)", style_body),
            Paragraph("<b>Date:</b> August 2026", style_body)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[2.5*inch, 3.2*inch, 1.8*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light_bg),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10))

    # --- SECTION 1: EXECUTIVE SUMMARY ---
    elements.append(Paragraph("1. Executive Summary & Project Vision", style_h1))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_secondary, spaceBefore=1, spaceAfter=8))
    
    summary_text = (
        "The <b>Intelligent Edge-AI Medicine Dispenser ('Blister Bot')</b> is an autonomous, fully offline healthcare assistant. "
        "Unlike conventional pill organizers that require manual sorting into individual bins or constant cloud connectivity, "
        "Blister Bot operates locally to interpret written prescriptions via optical character recognition (OCR), converse naturally with patients "
        "using a quantized Large Language Model (LLM), enforce strict overdose prevention rules, and <b>mechanically extract tablets directly "
        "from their original, uncut aluminum blister strips</b>."
    )
    elements.append(Paragraph(summary_text, style_body))

    # --- SECTION 2: HARDWARE ARCHITECTURE ---
    elements.append(Paragraph("2. Dual-Processor Hardware Architecture", style_h1))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_secondary, spaceBefore=1, spaceAfter=8))

    hw_table_data = [
        [Paragraph("<b>Subsystem Component</b>", style_body), Paragraph("<b>Hardware / Firmware</b>", style_body), Paragraph("<b>Primary Responsibilities & Workloads</b>", style_body)],
        [Paragraph("<b>Linux MPU</b>", style_body), Paragraph("Qualcomm Dragonwing QRB2210", style_body), Paragraph("Runs localized LLM (llama.cpp + TinyLlama), speech recognition (Whisper.cpp), prescription OCR, face recognition, and database management.", style_body)],
        [Paragraph("<b>Real-Time MCU</b>", style_body), Paragraph("STM32U585 Microcontroller", style_body), Paragraph("Dedicated exclusively to non-blocking 2-axis CNC gantry motor control (AccelStepper), limit switches, safety interlocks, and plunger actuators.", style_body)],
        [Paragraph("<b>Smart Display</b>", style_body), Paragraph("7\" Portrait TFT/LCD Panel", style_body), Paragraph("Renders patient dosage schedules, visual cross-check reference images, consumption graphs, and system telemetry.", style_body)],
        [Paragraph("<b>Vision System</b>", style_body), Paragraph("Integrated HD Camera Module", style_body), Paragraph("Handles patient facial recognition, prescription scanning, pill identification, coordinate mapping, and hand-to-mouth action verification.", style_body)],
    ]
    hw_table = Table(hw_table_data, colWidths=[1.5*inch, 1.8*inch, 4.2*inch])
    hw_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(hw_table)
    elements.append(Spacer(1, 10))

    # --- SECTION 3: VISUAL REFERENCE BREAKDOWN ---
    elements.append(Paragraph("3. Visual Reference Breakdown (From Video Analysis)", style_h1))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_secondary, spaceBefore=1, spaceAfter=8))

    elements.append(Paragraph("Key architectural and mechanical insights extracted from reference video frames:", style_body))

    img_frame1 = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\frames\frame_002.jpg"
    img_frame2 = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\frames\frame_005.jpg"
    img_frame3 = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\frames\frame_008.jpg"

    ref_imgs_data = [
        [
            Image(img_frame1, width=2.3*inch, height=1.3*inch),
            Image(img_frame2, width=2.3*inch, height=1.3*inch),
            Image(img_frame3, width=2.3*inch, height=1.3*inch),
        ],
        [
            Paragraph("<b>Frame 002:</b> Dual Chamber & Touch UI", style_caption),
            Paragraph("<b>Frame 005:</b> CNC Gantry & U-Scoring", style_caption),
            Paragraph("<b>Frame 008:</b> Appliance Overview", style_caption),
        ]
    ]
    ref_table = Table(ref_imgs_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
    ref_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(ref_table)

    elements.append(Paragraph("• <b>Dual-Chamber Layout:</b> The left chamber is illuminated and houses the multi-slot blister rack behind a transparent acrylic door; the right side houses the smart display, top AI camera, and pill output tray.", style_bullet))
    elements.append(Paragraph("• <b>U-Shaped Foil Scoring:</b> To prevent pill damage caused by high-force punching, a motorized rotary cutter scores a 270-degree hinged flap in the aluminum backing, allowing a soft silicone plunger to push the pill out gently.", style_bullet))

    elements.append(PageBreak()) # Clean page break for 3D model breakdown

    # --- SECTION 4: 3D MODEL DEVELOPMENT IN BLENDER ---
    elements.append(Paragraph("4. 3D Model Development & Blender Implementation", style_h1))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_secondary, spaceBefore=1, spaceAfter=8))

    elements.append(Paragraph(
        "During Week 1, a complete, accurate 3D model of Blister Bot was procedurally constructed in <b>Blender 5.2 LTS</b> using Python automation script <code>create_blister_bot_model.py</code>. "
        "The model was saved as <code>blister_bot.blend</code> and rendered headlessly into high-resolution presentation preview images.",
        style_body
    ))

    render_p = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\renders\render_perspective.png"
    render_m = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\renders\render_mechanism.png"
    render_f = r"c:\FARIS\Blister Bot\Blister-bot-main-\Week 1\renders\render_front.png"

    render_imgs_data = [
        [
            Image(render_p, width=3.5*inch, height=1.97*inch),
            Image(render_m, width=3.5*inch, height=1.97*inch),
        ],
        [
            Paragraph("<b>Render 1:</b> Perspective Isometric View", style_caption),
            Paragraph("<b>Render 2:</b> Deblistering Mechanism Close-Up", style_caption),
        ]
    ]
    render_table = Table(render_imgs_data, colWidths=[3.75*inch, 3.75*inch])
    render_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(render_table)
    elements.append(Spacer(1, 6))

    # Front render centered
    front_table_data = [
        [Image(render_f, width=4.0*inch, height=2.25*inch)],
        [Paragraph("<b>Render 3:</b> Front Presentation View", style_caption)]
    ]
    front_table = Table(front_table_data, colWidths=[7.5*inch])
    front_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    elements.append(front_table)

    # --- SECTION 5: DETAILED 3D GEOMETRY BREAKDOWN ---
    elements.append(Paragraph("5. Mechanical & Component Breakdown in 3D Model", style_h1))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_secondary, spaceBefore=1, spaceAfter=8))

    elements.append(Paragraph("• <b>Appliance Chassis & Enclosure:</b> Desktop form-factor with rounded matte white ABS plastic shell, dark metallic backing wall, top warm LED light strip (Mat_LED_Warm), cyan status light bar (Mat_LED_Cyan), and beveled transparent acrylic front window door.", style_bullet))
    elements.append(Paragraph("• <b>Smart Touch Interface:</b> 7\" portrait screen with customized UI widgets (pill schedule card, status bar, action buttons), top camera housing with glass lens, status LED strip, and lower dispensing cup drawer.", style_bullet))
    elements.append(Paragraph("• <b>2-Axis CNC Deblistering Gantry:</b> Upper/lower X aluminum extrusions, vertical Y lead screw, linear guide rod, carriage block, and dual NEMA 17 stepper motors.", style_bullet))
    elements.append(Paragraph("• <b>Scoring Toolhead & Ejection Pin:</b> Motorized rotary steel cutter disc engineered for 270-degree foil flap scoring and spring-loaded silicone plunger pin positioned above a funneled delivery chute.", style_bullet))

    # --- SECTION 6: DELIVERABLES & INVENTORY ---
    elements.append(Paragraph("6. Week 1 Deliverables & File Inventory", style_h1))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_secondary, spaceBefore=1, spaceAfter=8))

    inv_data = [
        [Paragraph("<b>File / Resource Name</b>", style_body), Paragraph("<b>Type / Location</b>", style_body), Paragraph("<b>Description & Contents</b>", style_body)],
        [Paragraph("<b>Project Blueprint.pdf</b>", style_body), Paragraph("Week 1/", style_body), Paragraph("Full technical blueprint and software/hardware requirements specification.", style_body)],
        [Paragraph("<b>blister_bot.blend</b>", style_body), Paragraph("Week 1/", style_body), Paragraph("Native 3D project model file generated in Blender 5.2 LTS.", style_body)],
        [Paragraph("<b>create_blister_bot_model.py</b>", style_body), Paragraph("Week 1/", style_body), Paragraph("Python script for procedural geometry generation, shading, lighting, and rendering.", style_body)],
        [Paragraph("<b>Week1_Documentation.md</b>", style_body), Paragraph("Week 1/", style_body), Paragraph("Comprehensive markdown documentation report.", style_body)],
        [Paragraph("<b>frames/</b>", style_body), Paragraph("Week 1/frames/", style_body), Paragraph("Directory containing 10 reference image frames extracted from reference video.", style_body)],
        [Paragraph("<b>renders/</b>", style_body), Paragraph("Week 1/renders/", style_body), Paragraph("High-resolution 3D preview render images (perspective, mechanism, front).", style_body)],
    ]
    inv_table = Table(inv_data, colWidths=[2.0*inch, 1.5*inch, 4.0*inch])
    inv_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(inv_table)

    doc.build(elements)
    print(f"Successfully generated PDF documentation at: {pdf_path}")

if __name__ == "__main__":
    build_pdf()
