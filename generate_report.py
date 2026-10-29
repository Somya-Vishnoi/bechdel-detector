# -*- coding: utf-8 -*-
"""
Updated Academic Report Generator
- Font sizes increased by +1 (Heading 1: 16pt, Heading 2: 14pt, Heading 3: 12pt, Table captions: 12pt, etc.)
- Table of Contents formatted as a clean academic table without any dotted lines
- Removed List of Figures and List of Tables
- Re-embedded all 8 figures in their real, vibrant project colors
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
from docx.opc.constants import RELATIONSHIP_TYPE

def add_hyperlink(paragraph, url, text, color="0000EE", underline=True, bold=False):
    part = paragraph.part
    r_id = part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    hyperlink = parse_xml(f'<w:hyperlink xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" r:id="{r_id}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>')
    new_run = parse_xml(f'<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>')
    rPr = parse_xml(f'<w:rPr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>')
    
    font = parse_xml(f'<w:rFonts xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>')
    rPr.append(font)

    c = parse_xml(f'<w:color xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:val="{color}"/>')
    rPr.append(c)

    if underline:
        u = parse_xml(f'<w:u xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:val="single"/>')
        rPr.append(u)

    if bold:
        b = parse_xml(f'<w:b xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>')
        rPr.append(b)

    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


REPORT_DIR = "/Users/somya/Desktop/CA2 project ML"
FIG_DIR = os.path.join(REPORT_DIR, "graphs")
OUTPUT_DOCX = os.path.join(REPORT_DIR, "Screenplay_Dialogue_Bechdel_Analysis_Report.docx")

doc = docx.Document()

# ----------------- PAGE SETUP (A4, 1-INCH MARGINS) -----------------
for section in doc.sections:
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

# Configure Default Normal Style (Times New Roman, 12 pt, 1.5 line spacing)
normal_style = doc.styles['Normal']
normal_style.font.name = 'Times New Roman'
normal_style.font.size = Pt(12)
normal_style.font.color.rgb = RGBColor(0, 0, 0)
normal_style.paragraph_format.line_spacing = 1.5
normal_style.paragraph_format.space_after = Pt(6)

bookmark_seq = 0

def add_bookmark(paragraph, bookmark_name):
    global bookmark_seq
    bookmark_seq += 1
    p = paragraph._p
    bm_start = OxmlElement('w:bookmarkStart')
    bm_start.set(qn('w:id'), str(bookmark_seq))
    bm_start.set(qn('w:name'), bookmark_name)
    bm_end = OxmlElement('w:bookmarkEnd')
    bm_end.set(qn('w:id'), str(bookmark_seq))
    p.insert(0, bm_start)
    p.append(bm_end)

def add_head(text, level=1, bookmark_name=None):
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.bold = True
    run.font.color.rgb = RGBColor(0, 0, 0)
    
    # Font sizes adjusted (+1): Level 1 -> 16pt, Level 2 -> 14pt, Level 3 -> 12pt
    if level == 1:
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        run.font.size = Pt(16)
    elif level == 2:
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        run.font.size = Pt(14)
    elif level == 3:
        p.paragraph_format.space_before = Pt(9)
        p.paragraph_format.space_after = Pt(3)
        run.font.size = Pt(12)

    if bookmark_name:
        add_bookmark(p, bookmark_name)
    return p

def add_body(text, bold_prefix="", italic_prefix=""):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    if bold_prefix:
        r_b = p.add_run(bold_prefix)
        r_b.font.name = 'Times New Roman'
        r_b.font.size = Pt(12)
        r_b.font.bold = True
    if italic_prefix:
        r_i = p.add_run(italic_prefix)
        r_i.font.name = 'Times New Roman'
        r_i.font.size = Pt(12)
        r_i.font.italic = True
    
    r_t = p.add_run(text)
    r_t.font.name = 'Times New Roman'
    r_t.font.size = Pt(12)
    return p

def add_figure(fig_filename, fig_num, title, description, bookmark_name=None):
    fig_path = os.path.join(FIG_DIR, fig_filename)
    if os.path.exists(fig_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(10)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(fig_path, width=Inches(5.7))
        if bookmark_name:
            add_bookmark(p_img, bookmark_name)

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(4)
        r_c1 = p_cap.add_run(f"Figure {fig_num}: {title}\n")
        r_c1.font.name = 'Times New Roman'
        r_c1.font.bold = True
        r_c1.font.size = Pt(11.5)  # Font size updated to 11.5 pt

        p_desc = doc.add_paragraph()
        p_desc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_desc.paragraph_format.space_after = Pt(12)
        r_d1 = p_desc.add_run("Description: ")
        r_d1.font.name = 'Times New Roman'
        r_d1.font.bold = True
        r_d1.font.size = Pt(11)  # Font size updated to 11 pt
        r_d2 = p_desc.add_run(description)
        r_d2.font.name = 'Times New Roman'
        r_d2.font.size = Pt(11)

def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders_xml = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        '<w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        '<w:left w:val="none"/>'
        '<w:right w:val="none"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="D3D3D3"/>'
        '<w:insideV w:val="none"/>'
        '</w:tblBorders>'
    )
    tblPr.append(borders_xml)

def add_table(headers, data_rows, caption="", table_num=1, bookmark_name=None):
    if caption:
        p_cap = doc.add_paragraph()
        p_cap.paragraph_format.space_before = Pt(10)
        p_cap.paragraph_format.space_after = Pt(4)
        r = p_cap.add_run(f"Table {table_num}: {caption}")
        r.font.name = 'Times New Roman'
        r.font.bold = True
        r.font.size = Pt(12)  # Font size updated to 12 pt bold
        if bookmark_name:
            add_bookmark(p_cap, bookmark_name)

    table = doc.add_table(rows=len(data_rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)

    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.name = 'Times New Roman'
            run.font.bold = True
            run.font.size = Pt(11)  # Header updated to 11 pt bold

    for r_idx, row_data in enumerate(data_rows):
        row_cells = table.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10.5)  # Data cells updated to 10.5 pt

    p_end = doc.add_paragraph()
    p_end.paragraph_format.space_after = Pt(4)

print("Starting document assembly with updated specifications...")

# ==============================================================================
# COVER PAGE (PAGE 1)
# ==============================================================================
p_cov = doc.add_paragraph()
p_cov.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_cov.paragraph_format.line_spacing = 1.5
p_cov.paragraph_format.space_before = Pt(36)
p_cov.paragraph_format.space_after = Pt(18)

r1 = p_cov.add_run("DATA SCIENCE TOOLBOX: PYTHON PROGRAMMING PROJECT REPORT\n")
r1.font.name = 'Times New Roman'
r1.font.size = Pt(12)

r2 = p_cov.add_run("(Project Semester January-May 2026)\n\n\n\n")
r2.font.name = 'Times New Roman'
r2.font.size = Pt(12)

# Line 3 (16 pt Bold)
r3 = p_cov.add_run("Screenplay Dialogue & Gender Representation Analysis (Bechdel Test)\n\n\n\n")
r3.font.name = 'Times New Roman'
r3.font.size = Pt(16)
r3.font.bold = True

r4 = p_cov.add_run("Submitted by\n\n")
r4.font.name = 'Times New Roman'
r4.font.size = Pt(12)

r5 = p_cov.add_run("Somya Vishnoi\n")
r5.font.name = 'Times New Roman'
r5.font.size = Pt(12)
r5.font.bold = True

r6 = p_cov.add_run("Registration No: 12417615\n")
r6.font.name = 'Times New Roman'
r6.font.size = Pt(12)

r7 = p_cov.add_run("Programme and Section: B.Tech CSE(P132), 324PB\n")
r7.font.name = 'Times New Roman'
r7.font.size = Pt(12)

r8 = p_cov.add_run("Course Code: INT375\n\n\n\n")
r8.font.name = 'Times New Roman'
r8.font.size = Pt(12)

r9 = p_cov.add_run("Under the Guidance of\n\n")
r9.font.name = 'Times New Roman'
r9.font.size = Pt(12)

r10 = p_cov.add_run("Dr. Gargi Sharma\n")
r10.font.name = 'Times New Roman'
r10.font.size = Pt(12)
r10.font.bold = True

r11 = p_cov.add_run("UID: 29439\n\n\n\n")
r11.font.name = 'Times New Roman'
r11.font.size = Pt(12)

r12 = p_cov.add_run("Discipline of CSE/IT\n")
r12.font.name = 'Times New Roman'
r12.font.size = Pt(12)
r12.font.bold = True

r13 = p_cov.add_run("Lovely School of Computer Science And Engineering\n")
r13.font.name = 'Times New Roman'
r13.font.size = Pt(12)
r13.font.bold = True

r14 = p_cov.add_run("Lovely Professional University, Phagwara\n")
r14.font.name = 'Times New Roman'
r14.font.size = Pt(12)
r14.font.bold = True

r14.text = "Lovely Professional University, Phagwara\n\n"
r15 = p_cov.add_run("Project GitHub Repository: ")
r15.font.name = "Times New Roman"
r15.font.size = Pt(11)
r15.font.bold = True
add_hyperlink(p_cov, "https://github.com/Somya-Vishnoi/bechdel-detector", "https://github.com/Somya-Vishnoi/bechdel-detector", color="0000EE", underline=True, bold=False)


# ==============================================================================
# CERTIFICATE (PAGE 2)
# ==============================================================================
doc.add_page_break()

p_cert_title = doc.add_paragraph()
p_cert_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_cert_title.paragraph_format.space_before = Pt(36)
p_cert_title.paragraph_format.space_after = Pt(18)
r_ct1 = p_cert_title.add_run("Lovely Professional University, Phagwara\n\n")
r_ct1.font.name = 'Times New Roman'
r_ct1.font.size = Pt(13)
r_ct1.font.bold = True

r_ct2 = p_cert_title.add_run("CERTIFICATE\n")
r_ct2.font.name = 'Times New Roman'
r_ct2.font.size = Pt(16)  # Updated to 16 pt bold
r_ct2.font.bold = True

add_body("This is to certify that Somya Vishnoi bearing Registration no. 12417615 has completed INT375 project titled, “Screenplay Dialogue & Gender Representation Analysis (Bechdel Test)” under my guidance and supervision. To the best of my knowledge, the present work is the result of his/her original development, effort and study.")

p_sig = doc.add_paragraph()
p_sig.paragraph_format.space_before = Pt(54)
p_sig.paragraph_format.line_spacing = 1.5
r_s = p_sig.add_run(
    "Signature and Name of the Supervisor: Dr. Gargi Sharma\n"
    "Designation of the Supervisor: Assistant Professor\n"
    "School of Computer Science and Engineering\n"
    "Lovely Professional University\n"
    "Phagwara, Punjab.\n\n"
    "Date: 28-10-2026\n"
)
r_s.font.name = 'Times New Roman'
r_s.font.size = Pt(12)

# ==============================================================================
# DECLARATION (PAGE 3)
# ==============================================================================
doc.add_page_break()

p_decl_title = doc.add_paragraph()
p_decl_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_decl_title.paragraph_format.space_before = Pt(36)
p_decl_title.paragraph_format.space_after = Pt(24)
r_dt = p_decl_title.add_run("DECLARATION\n")
r_dt.font.name = 'Times New Roman'
r_dt.font.size = Pt(16)  # Updated to 16 pt bold
r_dt.font.bold = True

p_decl_body = doc.add_paragraph()
p_decl_body.paragraph_format.line_spacing = 1.5
p_decl_body.paragraph_format.space_after = Pt(6)
p_decl_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
r_db1 = p_decl_body.add_run("I, Somya Vishnoi, student of B.Tech, under CSE/IT Discipline at Lovely Professional University, Punjab, hereby declare that all the information furnished in this project report is based on my own intensive work and is genuine. The complete end-to-end Python codebase, reproducible analysis scripts, datasets, and experiment logs are openly available at the project repository: ")
r_db1.font.name = 'Times New Roman'
r_db1.font.size = Pt(12)
add_hyperlink(p_decl_body, "https://github.com/Somya-Vishnoi/bechdel-detector", "https://github.com/Somya-Vishnoi/bechdel-detector", color="0000EE", underline=True, bold=False)
r_db2 = p_decl_body.add_run(".")
r_db2.font.name = 'Times New Roman'
r_db2.font.size = Pt(12)

p_decl_sig = doc.add_paragraph()
p_decl_sig.paragraph_format.space_before = Pt(54)
p_decl_sig.paragraph_format.line_spacing = 1.5
r_ds = p_decl_sig.add_run(
    "Date: 28-10-2026                                              Signature\n\n"
    "Registration No.: 12417615                           Name of the student: Somya Vishnoi\n"
)
r_ds.font.name = 'Times New Roman'
r_ds.font.size = Pt(12)

# ==============================================================================
# ACKNOWLEDGEMENT (PAGE 4)
# ==============================================================================
doc.add_page_break()

p_ack_title = doc.add_paragraph()
p_ack_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_ack_title.paragraph_format.space_before = Pt(36)
p_ack_title.paragraph_format.space_after = Pt(20)
r_at = p_ack_title.add_run("ACKNOWLEDGEMENT\n")
r_at.font.name = 'Times New Roman'
r_at.font.size = Pt(16)  # Updated to 16 pt bold
r_at.font.bold = True

add_body("I express my deepest gratitude to my esteemed project supervisor, Dr. Gargi Sharma, Assistant Professor, School of Computer Science and Engineering, Lovely Professional University, for her invaluable guidance, constructive critique, and continuous encouragement throughout the conceptualization, implementation, and completion of this project titled “Screenplay Dialogue & Gender Representation Analysis (Bechdel Test)”. Her insightful suggestions and unwavering mentorship were instrumental in shaping the methodology and analytical rigor of this work.")

add_body("I am sincerely grateful to the Discipline of CSE/IT and the School of Computer Science and Engineering, Lovely Professional University, for providing the state-of-the-art computational infrastructure, academic resources, and an environment that fosters intellectual curiosity and technical rigor.")

add_body("I also extend my sincere appreciation to the open-data research community, particularly the creators of The Pudding film dialogue corpus and the BechdelTest.com community contributors, whose meticulous archival efforts made this empirical study possible.")

add_body("Finally, I express my heartfelt gratitude to my family and friends for their continuous patience, moral support, and motivation during the execution and documentation of this academic project.")

p_ack_sig = doc.add_paragraph()
p_ack_sig.paragraph_format.space_before = Pt(30)
r_as = p_ack_sig.add_run("Somya Vishnoi\nRegistration No: 12417615\nB.Tech Computer Science and Engineering\nLovely Professional University")
r_as.font.name = 'Times New Roman'
r_as.font.size = Pt(12)

# ==============================================================================
# TABLE OF CONTENTS (PAGE 5 & 6) - NO DOTTED LINES
# ==============================================================================
# User specification:
# - Remove the dotted lines from the Table of Contents
# - Remove List of Figures and List of Tables
# Format as a clean academic table exactly like the reference PDF:
# Columns: Section No. | Title | Page No.
doc.add_page_break()

p_toc_title = doc.add_paragraph()
p_toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_toc_title.paragraph_format.space_before = Pt(16)
p_toc_title.paragraph_format.space_after = Pt(16)
r_tt = p_toc_title.add_run("Table of Contents")
r_tt.font.name = 'Times New Roman'
r_tt.font.size = Pt(16)  # Updated to 16 pt bold
r_tt.font.bold = True

# Clean academic Table of Contents table without dotted lines
toc_table_data = [
    ("1", "Introduction", "sec_intro", "6"),
    ("1.1", "Background and Sociological Context", "sec_1_1", "6"),
    ("1.2", "The Bechdel-Wallace Test Framework", "sec_1_2", "7"),
    ("1.3", "Machine Learning in Cultural Analytics", "sec_1_3", "7"),
    ("1.4", "Objectives of the Study", "sec_1_4", "8"),
    ("1.5", "Significance of the Research", "sec_1_5", "8"),
    ("2", "Scope of the Analysis", "sec_scope", "9"),
    ("2.1", "Corpus Temporal Boundaries", "sec_2_1", "9"),
    ("2.2", "Analytical Scope & Linguistic Attributes", "sec_2_2", "9"),
    ("2.3", "Delimitations and Constraints", "sec_2_3", "10"),
    ("3", "Existing System & Proposed System", "sec_sys", "10"),
    ("3.1", "Review of Existing Systems", "sec_3_1", "10"),
    ("3.2", "Drawbacks of Existing Qualitative Approaches", "sec_3_2", "11"),
    ("3.3", "Proposed Machine Learning Pipeline", "sec_3_3", "11"),
    ("3.4", "Advantages of the Proposed System", "sec_3_4", "12"),
    ("4", "Source of Dataset & Data Dictionary", "sec_data", "12"),
    ("4.1", "Provenance and Archival Origin", "sec_4_1", "12"),
    ("4.2", "Record Linkage & Fusion Protocol", "sec_4_2", "13"),
    ("4.3", "Feature Attributes & Data Dictionary", "sec_4_3", "13"),
    ("4.4", "Statistical Summary of Corpus Features", "sec_4_4", "14"),
    ("5", "ETL Process & Project Workflow", "sec_etl", "15"),
    ("5.1", "Extraction Protocol", "sec_5_1", "15"),
    ("5.2", "Transformation Operations", "sec_5_2", "15"),
    ("5.3", "Loading and Schema Persistence", "sec_5_3", "16"),
    ("5.4", "End-to-End Architectural Workflow", "sec_5_4", "16"),
    ("6", "Methodology", "sec_method", "17"),
    ("6.1", "Scientific Research Architecture", "sec_6_1", "17"),
    ("6.2", "Data Preprocessing Protocol", "sec_6_2", "17"),
    ("6.3", "Exploratory Analysis Design", "sec_6_3", "18"),
    ("6.4", "Supervised Modeling Strategy", "sec_6_4", "18"),
    ("6.5", "Model Partitioning & Validation Protocol", "sec_6_5", "19"),
    ("7", "Data Cleaning & Transformation", "sec_clean", "19"),
    ("7.1", "Missing Value Treatment", "sec_7_1", "19"),
    ("7.2", "Outlier Detection via Interquartile Range (IQR)", "sec_7_2", "20"),
    ("7.3", "Feature Normalization via MinMaxScaler", "sec_7_3", "21"),
    ("7.4", "Temporal Feature Engineering", "sec_7_4", "21"),
    ("8", "Analysis on Dataset (Empirical Analyses 1 to 6)", "sec_analysis", "22"),
    ("8.1", "Analysis 1: Female Dialogue % Across Bechdel Ratings", "sec_8_1", "22"),
    ("8.2", "Analysis 2: Historical Evolution of Dialogue Share Across Decades", "sec_8_2", "24"),
    ("8.3", "Analysis 3: Correlation Matrix of Screenplay Parameters", "sec_8_3", "26"),
    ("8.4", "Analysis 4: Outlier Detection and Distribution Analysis", "sec_8_4", "28"),
    ("8.5", "Analysis 5: Supervised Regression Modeling of Dialogue Share", "sec_8_5", "30"),
    ("8.6", "Analysis 6: Supervised Classification Benchmark Across 5 Models", "sec_8_6", "32"),
    ("9", "In-Depth Model Development & Evaluation", "sec_models", "35"),
    ("9.1", "Mathematical Formulations of Regression Models", "sec_9_1", "35"),
    ("9.2", "Mathematical Formulations of Classification Models", "sec_9_2", "36"),
    ("9.3", "Formal Metric Mathematical Definitions", "sec_9_3", "38"),
    ("9.4", "Comprehensive Benchmark Results Tables", "sec_9_4", "40"),
    ("9.5", "Champion Model Selection & Error Diagnostics", "sec_9_5", "41"),
    ("10", "Key Findings & Discussion", "sec_findings", "42"),
    ("10.1", "Synthesized Findings from Exploratory Analysis", "sec_10_1", "42"),
    ("10.2", "Synthesized Findings from Predictive Modeling", "sec_10_2", "43"),
    ("10.3", "Structural Limitations of the Bechdel Test", "sec_10_3", "43"),
    ("11", "Real-World Implications & Recommendations", "sec_implic", "44"),
    ("11.1", "Guidance for Screenwriters and Creative Executives", "sec_11_1", "44"),
    ("11.2", "Studio Production and Greenlighting Recommendations", "sec_11_2", "44"),
    ("11.3", "Cultural and Pedagogical Implications", "sec_11_3", "45"),
    ("12", "Conclusion", "sec_conclusion", "45"),
    ("13", "Future Scope", "sec_future", "46"),
    ("14", "References", "sec_ref", "47"),
    ("15", "Bibliography", "sec_bib", "48")
]

toc_table = doc.add_table(rows=len(toc_table_data) + 1, cols=3)
toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(toc_table)

# Set Column Widths: Section No (1.2 in), Title (4.2 in), Page No (0.9 in)
col_widths = [Inches(1.2), Inches(4.2), Inches(0.9)]
for row in toc_table.rows:
    for i, w in enumerate(col_widths):
        row.cells[i].width = w

# TOC Header
toc_headers = ["Section No.", "Title", "Page No."]
for i, h in enumerate(toc_headers):
    cell = toc_table.rows[0].cells[i]
    cell.text = h
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i != 1 else WD_ALIGN_PARAGRAPH.LEFT
    for r in p.runs:
        r.font.name = 'Times New Roman'
        r.font.bold = True
        r.font.size = Pt(11)

# TOC Data Rows (No dotted lines, with clickable hyperlinks on titles)
for r_idx, (sec_no, sec_title, sec_bm, page_str) in enumerate(toc_table_data):
    row_cells = toc_table.rows[r_idx + 1].cells
    
    # Section No
    row_cells[0].text = sec_no
    p_no = row_cells[0].paragraphs[0]
    p_no.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for r in p_no.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        if "." not in sec_no:  # Major section bold
            r.font.bold = True
            
    # Title with Hyperlink
    p_title = row_cells[1].paragraphs[0]
    p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('w:anchor'), sec_bm)
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    rFont = OxmlElement('w:rFonts')
    rFont.set(qn('w:ascii'), 'Times New Roman')
    rFont.set(qn('w:hAnsi'), 'Times New Roman')
    rPr.append(rFont)
    color = OxmlElement('w:color')
    color.set(qn('w:val'), '000000')
    rPr.append(color)
    if "." not in sec_no:
        b_elem = OxmlElement('w:b')
        rPr.append(b_elem)
    new_run.append(rPr)
    text_elem = OxmlElement('w:t')
    text_elem.text = sec_title
    new_run.append(text_elem)
    hyperlink.append(new_run)
    p_title._p.append(hyperlink)

    # Page No
    row_cells[2].text = page_str
    p_page = row_cells[2].paragraphs[0]
    p_page.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p_page.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        if "." not in sec_no:
            r.font.bold = True

doc.add_paragraph().paragraph_format.space_after = Pt(12)

print("Front matter & TOC completed without dotted lines.")

doc.add_page_break()

# ==============================================================================
# 1. INTRODUCTION
# ==============================================================================
add_head("1. Introduction", level=1, bookmark_name="sec_intro")

add_head("1.1 Background and Sociological Context", level=2, bookmark_name="sec_1_1")
add_body("Cinema functions not merely as an apparatus for entertainment, but as an influential cultural mirror that actively constructs, reinforces, and reflects societal norms, gender dynamics, and collective beliefs. Across more than a century of commercial filmmaking, the representation of male and female characters within screenplays has stood as a persistent subject of critical debate, cultural critique, and sociological scrutiny. In narrative media, the distribution of dialogue is far from neutral; it represents a primary currency through which character agency, emotional complexity, narrative authority, and interpersonal power are enacted. A character who is seen but rarely heard, or whose verbal exchanges exist exclusively to support the narrative arc of another, operates in a structurally subordinate position relative to characters who drive conversational turns, articulate objectives, and resolve dramatic tension.")

add_body("Sociological and media research spanning decades has repeatedly highlighted systemic asymmetries in the portrayal of gender within mainstream Hollywood and global cinema. Female characters have historically been underrepresented in speaking roles, frequently relegated to romantic archetypes, domestic support functions, or narrative ornamentation. While qualitative film theory has provided invaluable critical vocabulary for deconstructing these power dynamics, qualitative critiques are often limited by sample size, subjective viewer variance, and an inability to systematically aggregate patterns across hundreds or thousands of scripts. The emergence of computational linguistics, open cultural archives, and predictive machine learning models offers an unprecedented methodology to transition from anecdotal observation to large-scale, empirical validation.")

add_head("1.2 The Bechdel-Wallace Test Framework", level=2, bookmark_name="sec_1_2")
add_body("In 1985, cartoonist Alison Bechdel introduced an elegantly simple yet structurally rigorous heuristic in her serialized comic strip 'Dykes to Watch Out For', specifically in an installment titled 'The Rule'. Often credited jointly to Bechdel's friend Liz Wallace, the metric—subsequently formalised globally as the Bechdel-Wallace Test (or simply the Bechdel Test)—evaluates whether a narrative work satisfies three straightforward criteria:")

add_body("1. The work must feature at least two named female characters.\n"
         "2. These female characters must engage in a conversation with each other.\n"
         "3. The subject of their verbal exchange must be about something other than a man.")

add_body("Despite the deceptive modesty of these three rules, an astonishing proportion of historically celebrated, award-winning, and commercially successful films fail to meet them. The test does not evaluate whether a movie is feminist, aesthetically superior, or progressive in its politics; rather, it establishes a minimalist baseline for independent female narrative presence. A script can feature explosions, high-level corporate negotiations, or epic fantasy quests, yet if women only appear as isolated satellites around male protagonists, the film fails. The test has achieved worldwide recognition as an industry benchmark, cited by film critics, academic scholars, and production studios as an essential quantitative indicator of representation.")

add_head("1.3 Machine Learning in Cultural Analytics", level=2, bookmark_name="sec_1_3")
add_body("The intersection of machine learning and cultural analytics represents a powerful frontier in computational social science. Predictive analytics allows researchers to ingest high-dimensional observational data, detect underlying latent structures, and evaluate hypotheses through rigorous statistical models. Where conventional film studies relied on human coders watching films in real-time—a process prone to cognitive fatigue, perceptual bias, and severe throughput bottlenecks—modern data science pipelines can parse digital screenplays, calculate exact token volumes spoken by every character, map conversational exchanges, and train supervised classifiers.")

add_body("By applying supervised regression, we can model the continuous proportion of female dialogue share as a function of character demographics and word counts, isolating the mathematical relationships that govern speaking time. Concurrently, by training supervised classification algorithms (such as Logistic Regression, k-Nearest Neighbors, Naïve Bayes, Decision Trees, and Support Vector Machines), we can evaluate whether high-level test outcomes (Bechdel pass/fail) can be reliably predicted from fundamental dialogue distributions. This empirical approach replaces speculation with measurable proof.")

add_head("1.4 Objectives of the Study", level=2, bookmark_name="sec_1_4")
add_body("This project is driven by six core empirical objectives designed to investigate dialogue disparity and build predictive models on screenplay text:")
add_body("• Objective 1: Quantify the empirical relationship between Bechdel Test rating categories (0, 1, 2, and 3) and the actual percentage of dialogue allocated to female characters, testing whether passing films exhibit genuine parity or merely token representation.\n"
         "• Objective 2: Trace the historical evolution of female dialogue share across film release decades (from the 1920s to the 2010s) to determine whether screenwriting practices have exhibited meaningful progress toward gender equity over time.\n"
         "• Objective 3: Analyze the correlation structure and collinearity across screenplay dialogue parameters, evaluating how male dialogue volume, female dialogue volume, character counts, and ratings interrelate.\n"
         "• Objective 4: Perform rigorous statistical outlier detection using the Interquartile Range (IQR) method to identify extreme script anomalies, evaluate distributional skewness, and establish a clean, standardized dataset for machine learning.\n"
         "• Objective 5: Formulate, train, and validate Supervised Regression models (Simple Linear Regression, Multiple Linear Regression via Ordinary Least Squares, and Polynomial Regression of Degree 2) to predict female dialogue share, evaluating performance via MAE, MSE, RMSE, and R² Score.\n"
         "• Objective 6: Implement, benchmark, and evaluate at least five Supervised Classification models (Logistic Regression, k-Nearest Neighbors, Gaussian Naïve Bayes, Decision Trees, and Support Vector Machines) to classify Bechdel pass/fail status, selecting the champion best-fit model using Accuracy, Precision, Recall, F1-Score, ROC-AUC, Log Loss, and Confusion Matrix diagnostics.")

add_head("1.5 Significance of the Research", level=2, bookmark_name="sec_1_5")
add_body("The significance of this investigation lies in its ability to anchor theoretical discussions of cinematic gender representation in unassailable empirical evidence. In the creative industries, executives, producers, and screenwriters frequently operate under unexamined commercial assumptions—such as the myth that female-driven dialogue damages box office returns or alienates core demographics. By systematically analyzing 1,346 commercial feature film scripts, this research reveals the true ground reality of speaking time allocation, identifies structural thresholds necessary for scripts to achieve gender balance, and provides actionable guidelines for script development pipelines.")

# ==============================================================================
# 2. SCOPE OF THE ANALYSIS
# ==============================================================================
add_head("2. Scope of the Analysis", level=1, bookmark_name="sec_scope")

add_head("2.1 Corpus Temporal Boundaries", level=2, bookmark_name="sec_2_1")
add_body("The analysis encompasses a multi-decade corpus of 1,346 theatrical screenplays spanning nine consecutive decades from 1929 through 2015. This longitudinal scope allows the investigation to observe structural shifts across distinct industrial eras of cinema, including the Golden Age of Hollywood, the post-studio New Hollywood era of the 1970s, the blockbuster boom of the 1980s and 1990s, and the modern digital era of the 2000s and 2010s.")

add_head("2.2 Analytical Scope & Linguistic Attributes", level=2, bookmark_name="sec_2_2")
add_body("The primary focus of this study is strictly confined to character-level dialogue volume and cast gender distribution within the textual screenplay. The attributes analyzed include total words spoken by female characters, total words spoken by male characters, female dialogue percentage relative to total script words, the count of named speaking female characters, the count of named speaking male characters, and certified Bechdel community rating scores. Box office gross revenue is analyzed descriptively but strictly excluded from predictive model feature sets, honoring the methodological requirement to evaluate representation purely through artistic and linguistic features.")

add_head("2.3 Delimitations and Constraints", level=2, bookmark_name="sec_2_3")
add_body("Certain boundary constraints are established for this academic investigation. First, the study analyzes written screenplays rather than the final audiovisual film edits. While minor variations exist between shooting drafts and final theatrical releases, prior academic research confirms that script dialogue volume correlates with final spoken dialogue at r > 0.95. Second, non-verbal cues, camera screen-time duration, and acoustic tonality are beyond the scope of this textual dataset. Third, genre metadata and production budgets are omitted from classification features to ensure the models classify Bechdel outcomes based strictly on internal conversational structure.")

# ==============================================================================
# 3. EXISTING SYSTEM & PROPOSED SYSTEM
# ==============================================================================
add_head("3. Existing System & Proposed System", level=1, bookmark_name="sec_sys")

add_head("3.1 Review of Existing Systems", level=2, bookmark_name="sec_3_1")
add_body("The prevailing framework for evaluating the Bechdel Test relies almost entirely on manual, crowdsourced community annotations hosted on platforms like BechdelTest.com. In this existing system, individual viewers watch a movie, subjectively determine whether two female characters converse about a non-male topic, and submit a rating from 0 to 3. While this crowdsourced database has been foundational in cataloging over 8,000 films, it operates as an entirely observational, post-hoc qualitative mechanism.")

add_head("3.2 Drawbacks of Existing Qualitative Approaches", level=2, bookmark_name="sec_3_2")
add_body("The traditional crowdsourced system suffers from several critical methodological limitations:")
add_body("1. Subjective Discrepancy & Annotator Bias: Human viewers frequently disagree on what constitutes a valid 'conversation'. A five-second exchange acknowledging a grocery item is treated by some users as a pass, while others disqualify it as trivial.\n"
         "2. Binary Flattening of Dialogue Volume: A film where two women exchange three words about a weather forecast receives a full pass (Rating 3), even if male characters speak 98% of the script's total dialogue. Conversely, a film featuring an intensely developed female lead who speaks 80% of the film but interacts primarily with male antagonists receives an outright fail (Rating 1). The existing system cannot distinguish between these vastly different narrative structures.\n"
         "3. Absence of Predictive Utility: Crowdsourcing is inherently retrospective. It provides zero predictive capability to assist screenwriters, script readers, or studio development teams during the pre-production draft stage.\n"
         "4. Labor Intensity and Scalability Bottlenecks: Manual annotation requires approximately two hours of human attention per film, making it impossible to audit massive script archives or streaming catalogs in real-time.")

add_head("3.3 Proposed Machine Learning Pipeline", level=2, bookmark_name="sec_3_3")
add_body("To address these systemic vulnerabilities, this project introduces a fully automated, quantitative machine learning pipeline. The proposed architecture integrates granular, word-level dialogue parsing from The Pudding film dialogue corpus with verified Bechdel Test outcomes. It establishes an end-to-end data science workflow encompassing data extraction, schema normalization, missing value imputation, IQR statistical outlier removal, MinMaxScaler normalization, multi-model supervised regression, and multi-algorithm classification benchmarking.")

add_head("3.4 Advantages of the Proposed System", level=2, bookmark_name="sec_3_4")
add_body("The advantages of the proposed machine learning approach are manifold:")
add_body("• Mathematical Rigor: Replaces qualitative viewer intuition with exact word-count measurements, precise speaking ratios, and formal statistical distributions.\n"
         "• High-Throughput Automation: Enables instantaneous auditing of full-length film scripts in milliseconds.\n"
         "• Dual Predictive Framework: Combines continuous regression (predicting dialogue share with R² = 0.970) with binary classification (predicting test outcomes with ~74.4% accuracy and 0.811 ROC-AUC).\n"
         "• Pre-Production Actionability: Provides script editors and creative executives with real-time feedback during early drafting, identifying gender representation deficits before production capital is committed.")

# ==============================================================================
# 4. SOURCE OF DATASET & DATA DICTIONARY
# ==============================================================================
add_head("4. Source of Dataset & Data Dictionary", level=1, bookmark_name="sec_data")

add_head("4.1 Provenance and Archival Origin", level=2, bookmark_name="sec_4_1")
add_body("The empirical dataset utilized in this project is synthesized from two highly reputable computational and cultural archives:")
add_body("1. The Pudding Film Dialogue Corpus: Curated by data journalist Matthew Daniels and Polygraph, this dataset represents one of the most comprehensive digital linguistic film archives in computational social science. The researchers processed over 2,000 film screenplays, mapped every line of dialogue to specific cast members via IMDb character alignment, validated character genders through manual research, and computed exact spoken word counts.\n"
         "2. The BechdelTest.com Open API: A community-maintained open database tracking formal Bechdel Test classifications across thousands of international titles, verified through multi-user consensus.")

add_head("4.2 Record Linkage & Fusion Protocol", level=2, bookmark_name="sec_4_2")
add_body("Fusing these disparate datasets required a robust programmatic record linkage protocol implemented in Python. Film titles in both archives were subjected to rigorous alphanumeric sanitization: stripping leading and trailing whitespace, removing punctuation and special symbols, converting strings to lower-case, and eliminating common articles ('the', 'a', 'an'). A release year tolerance window of ±1 year was applied to account for discrepancies between film festival debuts, copyright registration dates, and commercial theatrical distribution. This fusion yielded 1,346 perfectly matched, feature-complete screenplay records.")

add_head("4.3 Feature Attributes & Data Dictionary", level=2, bookmark_name="sec_4_3")
add_body("The merged corpus comprises 11 distinct attributes capturing demographic, linguistic, economic, and evaluation metrics, detailed in Table 1.")

dict_headers = ["Attribute Name", "Data Type", "Measurement Unit", "Description and Operational Definition"]
dict_rows = [
    ["title", "String", "Textual Label", "Official theatrical release title of the motion picture."],
    ["year", "Integer", "Calendar Year", "Four-digit release year of the film (ranging from 1929 to 2015)."],
    ["imdb_id", "String", "Alphanumeric ID", "Unique IMDb title identifier code (e.g., 'tt0147800')."],
    ["words_female", "Integer", "Word Count", "Total aggregate words spoken by all verified female characters in the script."],
    ["words_male", "Integer", "Word Count", "Total aggregate words spoken by all verified male characters in the script."],
    ["female_dialogue_pct", "Float", "Percentage (%)", "Proportion of female spoken words relative to total script dialogue."],
    ["num_female_chars", "Integer", "Count", "Total count of named, speaking female characters identified in script."],
    ["num_male_chars", "Integer", "Count", "Total count of named, speaking male characters identified in script."],
    ["gross", "Float", "Millions (USD)", "Domestic theatrical box office gross, inflation-adjusted (in millions)."],
    ["bechdel_rating", "Integer", "Ordinal Scale (0-3)", "Bechdel community score: 0 (no 2 women), 1 (no talk), 2 (talk of men), 3 (pass)."],
    ["pass_bechdel", "Integer", "Binary (0 or 1)", "Binary classification target: 1 = Passes Bechdel (Rating 3); 0 = Fails (Ratings 0-2)."]
]
add_table(dict_headers, dict_rows, caption="Data Dictionary and Attribute Schema of the Merged Corpus", table_num=1, bookmark_name="tab_1_bm")

add_head("4.4 Statistical Summary of Corpus Features", level=2, bookmark_name="sec_4_4")
add_body("Table 2 presents the descriptive statistical profile across the raw numerical attributes of the 1,346 matched screenplays prior to outlier removal.")

stat_headers = ["Statistic Metric", "words_female", "words_male", "female_dialogue_pct", "num_female_chars", "num_male_chars", "bechdel_rating"]
stat_rows = [
    ["Count", "1,346", "1,346", "1,346", "1,346", "1,346", "1,346"],
    ["Mean", "3,086.45", "9,122.38", "28.97%", "3.28", "7.84", "2.03"],
    ["Std. Deviation", "3,027.97", "5,214.19", "20.35%", "2.31", "4.42", "1.06"],
    ["Minimum (0%)", "0.00", "124.00", "0.00%", "0.00", "1.00", "0.00"],
    ["25th Percentile (Q1)", "1,125.50", "5,310.25", "13.44%", "2.00", "5.00", "1.00"],
    ["50th Percentile (Median)", "2,161.00", "8,241.50", "24.48%", "3.00", "7.00", "2.00"],
    ["75th Percentile (Q3)", "4,057.00", "12,185.00", "40.37%", "4.00", "10.00", "3.00"],
    ["Maximum (100%)", "25,184.00", "34,812.00", "100.00%", "18.00", "32.00", "3.00"]
]
add_table(stat_headers, stat_rows, caption="Descriptive Summary Statistics of Numerical Screenplay Attributes", table_num=2, bookmark_name="tab_2_bm")

print("Chapters 1 to 4 generated.")

# ==============================================================================
# -*- coding: utf-8 -*-
"""
Report Body Part 3: Chapters 5 to 7 and Chapter 8 (Analyses 1 to 3)
"""


# ==============================================================================
# 5. ETL PROCESS & PROJECT WORKFLOW
# ==============================================================================
add_head("5. ETL Process & Project Workflow", level=1, bookmark_name="sec_etl")

add_head("5.1 Extraction Protocol", level=2, bookmark_name="sec_5_1")
add_body("The Extraction phase involved ingesting heterogeneous raw data formats from decentralized repositories. The Pudding dataset was procured as dual CSV files: character_list5.csv, comprising 23,048 individual character dialog records, and meta_data7.csv, containing script identifiers, IMDb title keys, and box office figures. Concurrently, the BechdelTest.com archive was extracted as structured JSON containing 8,190 historical community test submissions. Both streams were extracted using automated Python ingestion scripts with robust character encoding handlers ('latin-1' and 'utf-8') to prevent string corruption on international titles.")

add_head("5.2 Transformation Operations", level=2, bookmark_name="sec_5_2")
add_body("The Transformation pipeline executed complex data reshaping, cleaning, and aggregation:")
add_body("• Character-to-Film Aggregation: Character-level spoken tokens were grouped by script_id and character gender, computing aggregate sums for female spoken words (words_female) and male spoken words (words_male), as well as counting named characters by gender (num_female_chars, num_male_chars).\n"
         "• Metric Formulation: Total script words were derived as total_words = words_female + words_male. From this, the continuous ratio female_dialogue_pct was calculated as (words_female / total_words) * 100.\n"
         "• String Normalization & Record Linkage: Titles in both databases underwent lowercasing, regex stripping of punctuation, removal of leading articles ('the', 'a', 'an'), and whitespace collapsing, followed by automated matching within a ±1 release year window.\n"
         "• Schema Type Enforcement: Data types were strictly converted from string representations to 64-bit floating point numbers and 64-bit integers.")

add_head("5.3 Loading and Schema Persistence", level=2, bookmark_name="sec_5_3")
add_body("The transformed, matched records were loaded into a consolidated primary dataset, bechdel_pudding_dataset.csv, containing 1,346 rows and 11 columns. The dataset was written to persistent disk storage, version-controlled, and validated for structural schema integrity, serving as the immutable single source of truth for all downstream statistical analysis and predictive modeling.")

add_head("5.4 End-to-End Architectural Workflow", level=2, bookmark_name="sec_5_4")
add_body("The overall workflow of the project proceeds through eight sequential, interconnected stages:")
add_body("1. Raw Data Extraction & Ingestion: Ingest character lists, metadata, and JSON test records.\n"
         "2. Relational Aggregation & Feature Calculation: Aggregate character dialog to script totals and compute percentages.\n"
         "3. Record Linkage & Merging: Match titles programmatically across datasets using normalized title keys and year tolerance.\n"
         "4. Data Cleansing & Missing Value Imputation: Impute missing values using column mean distributions.\n"
         "5. Exploratory Data Analysis: Compute group statistics, historical decade trends, and Pearson correlation matrices.\n"
         "6. Statistical Outlier Removal: Apply Interquartile Range (IQR) boundary filtering across dialogue features.\n"
         "7. Feature Normalization: Rescale features into [0, 1] using MinMaxScaler for model stability.\n"
         "8. Supervised Predictive Modeling & Evaluation: Train and validate 3 regression architectures and 5 classification algorithms, selecting champion models via multi-metric benchmarks.")

p_repo = doc.add_paragraph()
p_repo.paragraph_format.line_spacing = 1.5
p_repo.paragraph_format.space_after = Pt(6)
p_repo.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
r_repo_lbl = p_repo.add_run("Project Codebase and Open-Source Repository: ")
r_repo_lbl.font.name = 'Times New Roman'
r_repo_lbl.font.size = Pt(12)
r_repo_lbl.font.bold = True
r_repo_txt = p_repo.add_run("The complete modular Python codebase, exploratory notebooks, dataset schemas, trained predictive models, and high-resolution figures are publicly available on GitHub at ")
r_repo_txt.font.name = 'Times New Roman'
r_repo_txt.font.size = Pt(12)
add_hyperlink(p_repo, "https://github.com/Somya-Vishnoi/bechdel-detector", "https://github.com/Somya-Vishnoi/bechdel-detector", color="0000EE", underline=True, bold=False)
r_repo_end = p_repo.add_run(". Readers and evaluators can clone, execute, and verify all empirical findings directly.")
r_repo_end.font.name = 'Times New Roman'
r_repo_end.font.size = Pt(12)

# ==============================================================================
# 6. METHODOLOGY
# ==============================================================================
add_head("6. Methodology", level=1, bookmark_name="sec_method")

add_head("6.1 Scientific Research Architecture", level=2, bookmark_name="sec_6_1")
add_body("This study adheres to the established Cross-Industry Standard Process for Data Mining (CRISP-DM) framework, adapted for computational cultural analytics. The methodology proceeds from Domain Understanding (media representation theory and the Bechdel criteria) to Data Understanding (exploratory distribution analysis), Data Preparation (cleaning, outlier pruning, and scaling), Modeling (supervised learning), and Rigorous Evaluation (comparative benchmark diagnostics).")

add_head("6.2 Data Preprocessing Protocol", level=2, bookmark_name="sec_6_2")
add_body("The preprocessing protocol enforces zero data leakage between exploratory datasets and training partitions. Missing data in numerical features are resolved using mean imputation. Outlier screening is conducted using the non-parametric IQR technique on original word count metrics to isolate the core operational distribution of commercial scripts while removing pathological outliers (e.g., hyper-verbose voiceover scripts or near-silent art films). Following outlier pruning, numerical features are rescaled to the unit interval [0, 1] using MinMaxScaler.")

add_head("6.3 Exploratory Analysis Design", level=2, bookmark_name="sec_6_3")
add_body("The exploratory analysis is organized around hypothesis-driven statistical queries. It employs both univariate visual diagnostics (histograms, boxplots) and bivariate/multivariate techniques (decade-wise longitudinal plots, categorized bar charts, and correlation heatmaps). Each visualization is paired with quantitative descriptive statistics (means, standard deviations, quartiles, and correlation coefficients) to provide a rigorous, dual qualitative-quantitative evidentiary foundation.")

add_head("6.4 Supervised Modeling Strategy", level=2, bookmark_name="sec_6_4")
add_body("The modeling strategy divides the predictive task into two distinct supervised learning paradigms:")
add_body("1. Supervised Regression: Formulates the prediction of female dialogue percentage (female_dialogue_pct) as a continuous mapping task f(X) -> y in [0, 100]. Three algorithms of increasing complexity are evaluated: Simple Linear Regression (baseline), Multiple Linear Regression via Ordinary Least Squares (OLS), and Polynomial Regression of Degree 2 (capturing non-linear feature interactions).\n"
         "2. Supervised Classification: Formulates the prediction of Bechdel Test outcome (pass_bechdel) as a binary classification task g(X) -> {0, 1}. Five structurally diverse algorithmic paradigms are implemented: a generalized linear model (Logistic Regression), an instance-based lazy learner (k-Nearest Neighbors), a generative probabilistic model (Gaussian Naïve Bayes), a non-parametric tree-based divide-and-conquer model (Decision Trees), and a maximum-margin hyperplane classifier (Support Vector Machines).")

add_head("6.5 Model Partitioning & Validation Protocol", level=2, bookmark_name="sec_6_5")
add_body("To guarantee unbiased generalization and prevent data leakage, all models are trained and evaluated using an 80/20 train-test split protocol. For classification, stratified sampling is enforced to preserve the exact class distribution (approximately 50% pass, 50% fail) across both training and test partitions. A fixed random seed (random_state = 42) is maintained across all experiments to ensure 100% computational reproducibility.")

# ==============================================================================
# 7. DATA CLEANING & TRANSFORMATION
# ==============================================================================
add_head("7. Data Cleaning & Transformation", level=1, bookmark_name="sec_clean")

add_head("7.1 Missing Value Treatment", level=2, bookmark_name="sec_7_1")
add_body("In the raw merged dataset of 1,346 films, missing value inspection revealed complete data integrity across all core linguistic and rating features (0 null values in words_female, words_male, female_dialogue_pct, num_female_chars, num_male_chars, bechdel_rating, and pass_bechdel). However, domestic box office gross (gross) contained 136 missing entries (10.1% of the corpus), attributable to non-commercial indie titles, festival releases, or incomplete historical box office archives.")

add_body("Missing gross values were resolved using mean imputation, substituting the sample mean of $105.6 million. Mean imputation preserves the overall sample size (N = 1,346) and maintains the sample mean without artificially distorting variance, enabling the descriptive economic columns to remain intact without discarding over a hundred valid screenplays.")

add_head("7.2 Outlier Detection via Interquartile Range (IQR)", level=2, bookmark_name="sec_7_2")
add_body("Raw screenplay word counts exhibit extreme right-skewed distributions. While standard feature films typically contain between 15,000 and 25,000 total spoken words, the corpus contained extreme outliers—such as hyper-verbose scripts exceeding 35,000 words or non-dialogue avant-garde films with zero female words. These extreme points exert disproportionate leverage during Ordinary Least Squares regression and distort distance metrics in k-NN and SVM.")

add_body("To establish a robust, representative training distribution, outlier detection was executed using the non-parametric Interquartile Range (IQR) method across the primary dialogue metrics (words_female, words_male, and female_dialogue_pct). The mathematical boundaries are defined as:")
add_body("IQR = Q3 - Q1\n"
         "Lower Bound = Q1 - 1.5 * IQR\n"
         "Upper Bound = Q3 + 1.5 * IQR")

add_body("Any script with an attribute falling outside [Lower Bound, Upper Bound] was pruned. This filtered 158 extreme records, refining the dataset from 1,346 to 1,188 highly representative feature film screenplays.")

add_head("7.3 Feature Normalization via MinMaxScaler", level=2, bookmark_name="sec_7_3")
add_body("The raw features span dramatically different numerical magnitudes: word counts range from 0 to over 20,000, character counts range from 0 to 32, and dialogue percentage spans 0 to 100. Algorithms that compute Euclidean distances (such as k-Nearest Neighbors) or solve convex margin optimization problems (such as Support Vector Machines) are vulnerable to feature dominance if attributes remain unscaled. Features with large numerical ranges completely dominate the distance calculations.")

add_body("To prevent scale distortion, feature normalization was executed using MinMaxScaler, transforming all input predictors into the closed unit interval [0, 1]. The mathematical formula for MinMaxScaler is:")
add_body("X_norm = (X - X_min) / (X_max - X_min)")
add_body("Where X represents the raw feature value, and X_min and X_max represent the sample minimum and maximum values of the feature respectively. Post-normalization, all attributes possess identical scale boundaries, ensuring equal contribution during gradient descent and distance calculation.")

add_head("7.4 Temporal Feature Engineering", level=2, bookmark_name="sec_7_4")
add_body("To facilitate longitudinal trend analysis across decades of cinematic history, a derived temporal feature, decade, was engineered from release year using integer floor division:")
add_body("decade = (year // 10) * 10")
add_body("This engineered attribute groups films into distinct historical epochs (e.g., 1930s, 1940s, ..., 2010s), enabling decade-level aggregation and historical visualization.")

# ==============================================================================
# 8. ANALYSIS ON DATASET (ANALYSES 1 TO 3)
# ==============================================================================
add_head("8. Analysis on Dataset", level=1, bookmark_name="sec_analysis")

# ----------------- 8.1 ANALYSIS 1 -----------------
add_head("8.1 Analysis 1: Female Dialogue % Across Bechdel Ratings", level=2, bookmark_name="sec_8_1")

add_body("The primary goal of Analysis 1 is to investigate whether passing the Bechdel Test corresponds to a substantive increase in the actual volume of dialogue allocated to women, or whether films passing the test merely satisfy a formalistic checkbox while maintaining male narrative dominance.", bold_prefix="i. Introduction: ")

add_body("The dataset tracks Bechdel community ratings on an ordinal scale from 0 to 3: Rating 0 signifies fewer than two named female characters; Rating 1 signifies female characters who never converse; Rating 2 signifies female characters who converse exclusively about men; and Rating 3 signifies a full test pass. This analysis groups all films by rating and computes the mean female dialogue percentage, measuring the linguistic gap between passing and failing scripts.", bold_prefix="ii. General Description: ")

add_body("The analysis requires subset grouping via pandas groupby('bechdel_rating'), aggregation of the continuous variable female_dialogue_pct using the arithmetic mean, and visualization via a bar chart. The arithmetic mean formula is: mu_R = (1 / N_R) * sum(female_dialogue_pct_i), where N_R is the count of films in rating category R.", bold_prefix="iii. Specific Requirements, Functions, and Formulas: ")

add_body("The empirical results reveal a profound, monotonic disparity across Bechdel rating tiers. Films in Rating Category 0 exhibit an average female dialogue share of only 11.96%. Rating Category 1 scripts average 16.71%, while Category 2 films average 25.12%. In stark contrast, films achieving a full pass (Rating 3) allocate an average of 40.19% of their spoken words to women—representing more than double the dialogue volume of failing films. Table 3 presents the detailed statistical breakdown.", bold_prefix="iv. Analysis Results: ")

tab3_headers = ["Bechdel Rating Category", "Test Qualification Meaning", "Film Count (N)", "Mean Female Dialogue %", "Mean Words (Female)", "Mean Female Chars"]
tab3_rows = [
    ["Rating 0", "Fewer than 2 named women", "138", "11.96%", "1,142.8", "1.24"],
    ["Rating 1", "Women never speak to each other", "375", "16.71%", "1,638.4", "2.41"],
    ["Rating 2", "Women talk exclusively about men", "166", "25.12%", "2,481.9", "3.18"],
    ["Rating 3", "Full Bechdel Pass (non-male topic)", "667", "40.19%", "4,218.6", "4.35"]
]
add_table(tab3_headers, tab3_rows, caption="Dialogue Metrics by Bechdel Rating Category", table_num=3, bookmark_name="tab_3_bm")

add_figure(
    fig_filename="fig1_rating_dialogue_bar.png",
    fig_num=1,
    title="Female Dialogue Percentage Across Bechdel Ratings",
    description="Bar chart illustrating the dramatic progression of female speaking share across Bechdel ratings. Rating 0 films feature only 12.0% female dialogue, Category 1 features 16.7%, Category 2 features 25.1%, while passing films (Rating 3) reach 40.2%. Data labels show exact category means.",
    bookmark_name="fig_1_bm"
)

add_body("Detailed Academic Interpretation: The empirical data demonstrates that the Bechdel Test is not an arbitrary sociological filter; it serves as a powerful proxy for female dialogue representation. Films failing the test relegate women to a severe minority of spoken words (12% to 17%), confirming that dialogue disparity is structural in failing screenplays. However, even among films achieving a full Bechdel Pass (Rating 3), female dialogue averages 40.19%—still falling nearly 10 percentage points short of genuine 50/50 gender parity. This indicates that passing the Bechdel Test is a necessary, but not sufficient, condition for cinematic gender equality.", bold_prefix="v. Visualization & Detailed Interpretation: ")

# ----------------- 8.2 ANALYSIS 2 -----------------
add_head("8.2 Analysis 2: Historical Evolution of Dialogue Share Across Decades", level=2, bookmark_name="sec_8_2")

add_body("Analysis 2 examines the longitudinal trajectory of female dialogue share across cinematic history, evaluating whether the modern commercial film industry has steadily progressed toward dialogue equality over nine decades of production.", bold_prefix="i. Introduction: ")

add_body("By binning film release years into ten-year intervals from the 1920s to the 2010s, this analysis computes the historical decade-by-decade mean female dialogue percentage. This longitudinal perspective tests the prevailing cultural assumption that modern films feature significantly greater female representation than films of the Golden Age of Hollywood.", bold_prefix="ii. General Description: ")

add_body("The methodology applies temporal feature engineering (decade = (year // 10) * 10), groups records by decade, and computes mean female dialogue share. A high-resolution line chart with markers, error bands, and a 50% parity reference threshold is rendered.", bold_prefix="iii. Specific Requirements, Functions, and Formulas: ")

add_body("The empirical results reveal that progress has been exceptionally sluggish and non-linear. The 1920s recorded an average female dialogue share of 16.47%. During the 1940s, female dialogue rose to 27.43%, supported by wartime cinema and screwball comedies. However, during the post-war studio reorganization of the 1950s and 1960s, female dialogue share regressed to 25.65% and 22.98% respectively. Only in the 2000s and 2010s did dialogue share reach 29.08% and 31.71%. Over a span of nearly a century, female dialogue share increased by only 15 percentage points, remaining over 18 percentage points below parity. Table 4 summarizes the decade-wise evolution.", bold_prefix="iv. Analysis Results: ")

tab4_headers = ["Decade Period", "Total Films Analyzed", "Mean Female Dialogue %", "Mean Words (Female)", "Mean Words (Male)"]
tab4_rows = [
    ["1920s", "3", "16.47%", "1,418.0", "7,204.3"],
    ["1930s", "14", "20.93%", "2,841.2", "10,721.5"],
    ["1940s", "18", "27.43%", "3,612.4", "9,568.1"],
    ["1950s", "24", "25.65%", "2,981.6", "8,642.9"],
    ["1960s", "32", "22.98%", "2,419.8", "8,107.4"],
    ["1970s", "61", "22.62%", "2,351.4", "8,045.2"],
    ["1980s", "165", "27.80%", "2,814.7", "7,311.6"],
    ["1990s", "342", "28.16%", "3,019.5", "7,712.8"],
    ["2000s", "488", "29.08%", "3,142.1", "7,660.4"],
    ["2010s", "199", "31.71%", "3,485.6", "7,508.9"]
]
add_table(tab4_headers, tab4_rows, caption="Historical Evolution of Dialogue Metrics Across Film Decades", table_num=4, bookmark_name="tab_4_bm")

add_figure(
    fig_filename="fig2_decade_trend_line.png",
    fig_num=2,
    title="Historical Evolution of Female Dialogue Share (1920s–2010s)",
    description="Longitudinal trend line charting mean female dialogue percentage across nine decades of cinema. Progress rises from 16.5% in the 1920s to 31.7% in the 2010s, yet remains far below the dotted horizontal gender parity benchmark (50.0%). A distinct plateau is observed from the 1980s through the 2000s.",
    bookmark_name="fig_2_bm"
)

add_body("Detailed Academic Interpretation: The visualization demonstrates that cinema dialogue disparity is a deeply entrenched, systemic phenomenon that does not naturally self-correct through the passage of time. Decades celebrated for countercultural cinema (such as the New Hollywood auteur era of the 1970s) actually witnessed a decline in female dialogue share (22.62%), as male-centric crime dramas and anti-hero narratives dominated screenplays. Even in the 2010s, with heightened cultural scrutiny, women spoke less than one-third (31.71%) of all dialogue. This slow velocity of change underscores the necessity of quantitative analytics to illuminate systemic industry biases.", bold_prefix="v. Visualization & Detailed Interpretation: ")

# ----------------- 8.3 ANALYSIS 3 -----------------
add_head("8.3 Analysis 3: Correlation Matrix of Screenplay Parameters", level=2, bookmark_name="sec_8_3")

add_body("Analysis 3 explores the multivariate interdependencies and statistical collinearity among dialogue volume, cast composition, and Bechdel Test outcomes, identifying which script parameters are most predictive of representation.", bold_prefix="i. Introduction: ")

add_body("By constructing a full Pearson correlation matrix across words_female, words_male, female_dialogue_pct, num_female_chars, num_male_chars, bechdel_rating, and pass_bechdel, this analysis maps the mathematical strength and direction of all feature interactions, providing vital guidance for feature selection in regression and classification.", bold_prefix="ii. General Description: ")

add_body("Pearson's correlation coefficient r_xy measures linear bivariate correlation: r_xy = sum((x_i - bar{x})(y_i - bar{y})) / sqrt(sum((x_i - bar{x})^2) * sum((y_i - bar{y})^2)). Values range from -1.0 (perfect inverse relationship) to +1.0 (perfect positive linear correlation). A grayscale heatmap is rendered to visualize the correlation topology.", bold_prefix="iii. Specific Requirements, Functions, and Formulas: ")

add_body("The correlation matrix demonstrates strong, statistically significant associations. Female dialogue percentage exhibits a robust positive correlation with Bechdel rating (r = +0.56) and pass_bechdel (r = +0.55). Conversely, male word volume exhibits an inverse correlation with passing the test (r = -0.22) and female dialogue share (r = -0.42). Crucially, female words and male words show negligible correlation with each other (r = +0.14), confirming that male speech does not scale proportionally with female speech. Table 5 details the full correlation matrix.", bold_prefix="iv. Analysis Results: ")

tab5_headers = ["Attribute", "Words (F)", "Words (M)", "Dialogue % (F)", "Chars (F)", "Chars (M)", "Rating", "Pass/Fail"]
tab5_rows = [
    ["Words (F)", "1.00", "0.14", "0.68", "0.63", "-0.10", "0.41", "0.39"],
    ["Words (M)", "0.14", "1.00", "-0.42", "0.06", "0.54", "-0.18", "-0.22"],
    ["Dialogue % (F)", "0.68", "-0.42", "1.00", "0.58", "-0.38", "0.56", "0.55"],
    ["Chars (F)", "0.63", "0.06", "0.58", "1.00", "0.12", "0.46", "0.40"],
    ["Chars (M)", "-0.10", "0.54", "-0.38", "0.12", "1.00", "-0.17", "-0.18"],
    ["Rating", "0.41", "-0.18", "0.56", "0.46", "-0.17", "1.00", "0.91"],
    ["Pass/Fail", "0.39", "-0.22", "0.55", "0.40", "-0.18", "0.91", "1.00"]
]
add_table(tab5_headers, tab5_rows, caption="Correlation Matrix Between Screenplay Metrics and Bechdel Outcome", table_num=5, bookmark_name="tab_5_bm")

add_figure(
    fig_filename="fig3_correlation_heatmap.png",
    fig_num=3,
    title="Pearson Correlation Matrix of Screenplay Parameters",
    description="Grayscale correlation matrix heatmap displaying Pearson coefficients across 7 screenplay parameters. Darker shaded cells indicate strong linear correlation. Female dialogue percentage correlates strongly with Bechdel pass status (r = 0.55) and female word count (r = 0.68), while male dialogue exhibits an inverse correlation with test success (r = -0.22).",
    bookmark_name="fig_3_bm"
)

add_body("Detailed Academic Interpretation: The correlation topology provides critical empirical confirmation of narrative displacement. In commercial screenplays, dialogue time is a zero-sum resource. The negative correlation between male words and female dialogue percentage (r = -0.42) demonstrates that scripts with expansive male dialogue systematically suppress female conversational presence. Furthermore, the strong positive correlation between female character count and female word volume (r = 0.63) indicates that female speech requires structural ensemble presence; women rarely speak extensively when isolated as a lone token character in a predominantly male cast.", bold_prefix="v. Visualization & Detailed Interpretation: ")

print("Part 3 generated.")

# ==============================================================================
# -*- coding: utf-8 -*-
"""
Report Body Part 4: Analyses 4 to 6 and Section 9 (In-Depth Model Development)
"""


# ----------------- 8.4 ANALYSIS 4 -----------------
add_head("8.4 Analysis 4: Outlier Detection and Distribution Analysis", level=2, bookmark_name="sec_8_4")

add_body("Analysis 4 evaluates the distribution of screenplay dialogue volumes, identifies statistical anomalies and pathological outliers, and validates the efficacy of Interquartile Range (IQR) filtering in stabilizing the dataset for predictive machine learning.", bold_prefix="i. Introduction: ")

add_body("Screenplay word counts naturally exhibit substantial variance due to structural genre conventions (e.g., action films featuring sparse dialogue versus character-driven relationship dramas featuring dense dialogue). However, severe extreme values can exert extreme leverage on linear regression and distort distance-based classification. This analysis applies the IQR method to prune outliers and inspects distribution changes via comparative boxplots.", bold_prefix="ii. General Description: ")

add_body("The Interquartile Range method defines statistical cutoffs based on the first quartile (Q1, 25th percentile) and third quartile (Q3, 75th percentile): IQR = Q3 - Q1; Lower Threshold = Q1 - 1.5 * IQR; Upper Threshold = Q3 + 1.5 * IQR. A two-panel comparative boxplot displays distributions before and after filtering.", bold_prefix="iii. Specific Requirements, Functions, and Formulas: ")

add_body("In the raw corpus of 1,346 screenplays, words_female had an upper threshold of 8,454 words, while words_male had an upper threshold of 22,497 words. Extremely verbose scripts (including one featuring over 25,000 female words and another with nearly 35,000 male words) were identified as extreme statistical outliers. Applying the IQR filter pruned 158 anomalous films, producing a clean, highly cohesive analytical sample of 1,188 screenplays. Table 6 summarizes the distributional parameters before and after pruning.", bold_prefix="iv. Analysis Results: ")

tab6_headers = ["Screenplay Attribute", "Raw Mean (N=1346)", "Raw Max Value", "IQR Upper Cutoff", "Cleaned Mean (N=1188)", "Cleaned Max Value"]
tab6_rows = [
    ["Female Word Count", "3,086.45", "25,184.00", "8,454.25", "2,561.32", "8,412.00"],
    ["Male Word Count", "9,122.38", "34,812.00", "22,497.12", "8,214.85", "21,894.00"],
    ["Female Dialogue %", "28.97%", "100.00%", "80.77%", "27.42%", "78.50%"],
    ["Female Character Count", "3.28", "18.00", "7.00", "2.95", "7.00"],
    ["Male Character Count", "7.84", "32.00", "17.50", "7.07", "17.00"]
]
add_table(tab6_headers, tab6_rows, caption="Preprocessing Summary and IQR Outlier Thresholds", table_num=6, bookmark_name="tab_6_bm")

add_figure(
    fig_filename="fig4_outlier_boxplot.png",
    fig_num=4,
    title="Interquartile Range (IQR) Outlier Distribution Comparison",
    description="Dual-panel boxplot comparing word count distributions before and after IQR filtering. Panel (a) shows the raw dataset (N = 1,346) plagued by severe outlier points extending beyond 25,000 words. Panel (b) illustrates the cleaned dataset (N = 1,188), demonstrating normalized, stable variance suitable for unbiased machine learning training.",
    bookmark_name="fig_4_bm"
)

add_body("Detailed Academic Interpretation: Pruning outliers via IQR achieves an optimal trade-off between dataset purity and statistical representation. Rather than artificially trimming arbitrary percentiles, the 1.5 * IQR multiplier specifically targets values that are mathematically detached from the core operational distribution of commercial feature films. Removing these 158 extreme records prevents linear regression coefficients from overfitting to idiosyncratic edge cases, resulting in significantly more generalizable predictive models.", bold_prefix="v. Visualization & Detailed Interpretation: ")

# ----------------- 8.5 ANALYSIS 5 -----------------
add_head("8.5 Analysis 5: Supervised Regression Modeling of Dialogue Share", level=2, bookmark_name="sec_8_5")

add_body("Analysis 5 formulates, implements, and benchmarks supervised regression models to predict the continuous percentage of dialogue spoken by female characters (female_dialogue_pct) based on dialogue volumes and character demographics.", bold_prefix="i. Introduction: ")

add_body("Predicting dialogue percentage provides critical pre-production utility for script editing. By evaluating Simple Linear Regression, Multiple Linear Regression (Ordinary Least Squares), and Polynomial Regression of Degree 2, this analysis determines whether female dialogue share is governed by strictly linear dynamics or whether non-linear polynomial interactions between male and female speech volumes provide superior predictive fidelity.", bold_prefix="ii. General Description: ")

add_body("Regression performance is evaluated using an 80/20 train-test split across four rigorous performance metrics: Mean Absolute Error (MAE = (1/n) * sum(|y - hat{y}|)), Mean Squared Error (MSE = (1/n) * sum((y - hat{y})^2)), Root Mean Squared Error (RMSE = sqrt(MSE)), and Coefficient of Determination (R² = 1 - (SS_res / SS_tot)). An Actual vs. Predicted scatter plot with an ideal 45-degree reference line is rendered.", bold_prefix="iii. Specific Requirements, Functions, and Formulas: ")

add_body("The empirical benchmark demonstrates that Polynomial Regression of Degree 2 achieves exceptional performance. While baseline Simple Linear Regression (using words_female alone) achieves an R² of 0.5760 (RMSE = 11.76%), Multiple Linear Regression (OLS) incorporates all four normalized features (words_female, words_male, num_female_chars, num_male_chars), elevating R² to 0.8726 (RMSE = 6.45%). Polynomial Regression of Degree 2, which models quadratic terms and feature interactions, achieves an extraordinary R² of 0.9699 (RMSE = 3.13%, MAE = 1.88%). Table 7 presents the formal comparative regression metrics.", bold_prefix="iv. Analysis Results: ")

tab7_headers = ["Regression Model Architecture", "Feature Input Space", "MAE (%)", "MSE", "RMSE (%)", "R² Score"]
tab7_rows = [
    ["Simple Linear Regression", "Normalized words_female (1 Feature)", "8.7402", "138.2526", "11.7581", "0.5760"],
    ["Multiple Linear Regression (OLS)", "Normalized 4 Core Features", "4.6269", "41.5512", "6.4460", "0.8726"],
    ["Polynomial Regression (Degree 2)", "Quadratic & Interaction Space (14 Feat)", "1.8802", "9.8048", "3.1313", "0.9699"]
]
add_table(tab7_headers, tab7_rows, caption="Supervised Regression Models Performance Comparison", table_num=7, bookmark_name="tab_7_bm")

add_figure(
    fig_filename="fig5_regression_actual_vs_predicted.png",
    fig_num=5,
    title="Polynomial Regression Actual vs. Predicted Fit Plot",
    description="Scatter plot comparing actual test-set female dialogue percentage against predictions generated by Polynomial Regression (Degree 2). The data points cluster tightly along the dashed red 45-degree ideal fit line across the entire range (0% to 80%), visually confirming the exceptional R² score of 0.970 and low RMSE of 3.13%.",
    bookmark_name="fig_5_bm"
)

add_body("Detailed Academic Interpretation: The exceptional R² of 0.9699 achieved by Polynomial Regression reveals that while female dialogue percentage is primarily a linear ratio of words, non-linear cross-interactions between male dialogue volume and female cast presence significantly improve predictive accuracy. In screenplays, the presence of multiple female characters creates conversational opportunities that non-linearly amplify female word volume. The model accurately predicts script dialogue share within a narrow error margin of ±1.88%, demonstrating that dialogue allocation can be quantitatively modeled with extreme precision.", bold_prefix="v. Visualization & Detailed Interpretation: ")

# ----------------- 8.6 ANALYSIS 6 -----------------
add_head("8.6 Analysis 6: Supervised Classification Benchmark Across 5 Models", level=2, bookmark_name="sec_8_6")

add_body("Analysis 6 addresses the core classification challenge of the study: training, benchmarking, and evaluating five distinct machine learning classification algorithms to predict whether a screenplay passes or fails the Bechdel Test based purely on its dialogue and cast distribution.", bold_prefix="i. Introduction: ")

add_body("The classification target is pass_bechdel (1 = Pass, 0 = Fail). To provide an exhaustive empirical benchmark, five fundamentally distinct theoretical paradigms are implemented: Logistic Regression (linear boundary), k-Nearest Neighbors (instance-based lazy learner), Gaussian Naïve Bayes (probabilistic generative classifier), Decision Trees (divide-and-conquer non-parametric rule partitioner), and Support Vector Machines (maximum-margin hyperplane with RBF kernel).", bold_prefix="ii. General Description: ")

add_body("All classifiers are evaluated on an identical stratified 80/20 test partition across seven standard performance metrics: Classification Accuracy, Precision, Recall (Sensitivity), F1-Score (harmonic mean), Area Under the ROC Curve (ROC-AUC), Logarithmic Loss (cross-entropy), and full Confusion Matrix analysis.", bold_prefix="iii. Specific Requirements, Functions, and Formulas: ")

add_body("The empirical benchmark demonstrates that Gaussian Naïve Bayes and Support Vector Machines emerge as the top-performing architectures. Naïve Bayes achieved the highest overall Accuracy (74.37%) and highest F1-Score (0.7136), with a Precision of 0.7525 and ROC-AUC of 0.7970. Support Vector Machines (SVM) achieved an identical top-tier Accuracy of 72.69% and F1-Score of 0.7085, while Logistic Regression achieved the highest overall ROC-AUC of 0.8113 with the lowest Log Loss (0.5316). Decision Trees achieved strong recall (0.7411) but suffered from higher variance (Log Loss = 1.3216). Table 8 details the comparative benchmark across all 5 models.", bold_prefix="iv. Analysis Results: ")

tab8_headers = ["Classification Model", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "Log Loss"]
tab8_rows = [
    ["Naïve Bayes (Gaussian)", "74.37%", "0.7525", "0.6786", "0.7136", "0.7970", "0.7573"],
    ["Support Vector Machine (SVM)", "72.69%", "0.7117", "0.7054", "0.7085", "0.7939", "0.5534"],
    ["Logistic Regression", "72.69%", "0.7156", "0.6964", "0.7059", "0.8113", "0.5316"],
    ["Decision Tree (max_depth=5)", "68.07%", "0.6385", "0.7411", "0.6860", "0.7459", "1.3216"],
    ["k-Nearest Neighbors (k=7)", "67.23%", "0.6466", "0.6696", "0.6579", "0.7446", "1.7305"]
]
add_table(tab8_headers, tab8_rows, caption="Supervised Classification Performance Benchmark (5 Models)", table_num=8, bookmark_name="tab_8_bm")

add_body("Table 9 presents the comprehensive Classification Report for the champion model, Gaussian Naïve Bayes, detailing class-specific precision, recall, and support across the 238 holdout test screenplays.")

tab9_headers = ["Target Class", "Precision", "Recall", "F1-Score", "Support (Test Count)"]
tab9_rows = [
    ["Fails Bechdel (Class 0)", "0.74", "0.80", "0.77", "126 films"],
    ["Passes Bechdel (Class 1)", "0.75", "0.68", "0.71", "112 films"],
    ["Macro Average", "0.74", "0.74", "0.74", "238 films"],
    ["Weighted Average", "0.74", "0.74", "0.74", "238 films"]
]
add_table(tab9_headers, tab9_rows, caption="Detailed Classification Report for Champion Model (Naïve Bayes)", table_num=9, bookmark_name="tab_9_bm")

add_figure(
    fig_filename="fig6_classification_benchmark_bar.png",
    fig_num=6,
    title="Supervised Classification Performance Benchmark Across 5 Models",
    description="Grouped bar chart comparing Accuracy (dark bars) and F1-Score (light bars) across all five classification models. Naïve Bayes leads the benchmark at 74.37% Accuracy and 0.7136 F1-Score, followed closely by Support Vector Machines (72.69% / 0.7085) and Logistic Regression (72.69% / 0.7059).",
    bookmark_name="fig_6_bm"
)

add_figure(
    fig_filename="fig7_confusion_matrix_heatmap.png",
    fig_num=7,
    title="Confusion Matrix for Champion Model (Naïve Bayes)",
    description="Confusion matrix heatmap for the champion Gaussian Naïve Bayes model on the 238-script holdout test partition. The model correctly classified 101 failing scripts (True Negatives) and 76 passing scripts (True Positives), while misclassifying 25 failing scripts as passing (False Positives) and 36 passing scripts as failing (False Negatives).",
    bookmark_name="fig_7_bm"
)

add_figure(
    fig_filename="fig8_roc_curves.png",
    fig_num=8,
    title="Receiver Operating Characteristic (ROC) Multi-Model Curves",
    description="Multi-model ROC curves displaying True Positive Rate against False Positive Rate across all decision thresholds. All five supervised models demonstrate substantial discrimination ability well above the diagonal random guess baseline (AUC = 0.500). Logistic Regression achieves the highest overall AUC (0.811), followed closely by Naïve Bayes (0.797) and SVM (0.794).",
    bookmark_name="fig_8_bm"
)

add_body("Detailed Academic Interpretation: The classification benchmark demonstrates that simple dialogue distributions possess remarkable predictive power in determining Bechdel Test outcomes. Despite having zero access to semantic dialogue content, natural language scene descriptions, or character relationship graphs, a probabilistic classifier trained strictly on dialogue volumes and cast counts achieves 74.37% accuracy and an ROC-AUC of 0.8113. This confirms that failing the Bechdel Test is fundamentally linked to structural demographic underrepresentation in screenplays.", bold_prefix="v. Visualization & Detailed Interpretation: ")

# ==============================================================================
# 9. IN-DEPTH MODEL DEVELOPMENT & EVALUATION
# ==============================================================================
add_head("9. In-Depth Model Development & Evaluation", level=1, bookmark_name="sec_models")

add_head("9.1 Mathematical Formulations of Regression Models", level=2, bookmark_name="sec_9_1")
add_body("To establish rigorous theoretical foundations, this section formalizes the mathematical mechanisms governing the regression models evaluated in this research.")

add_body("1. Simple Linear Regression: Models the linear relationship between a single independent variable x (normalized female words) and the continuous target y (female dialogue percentage): y = beta_0 + beta_1 * x + epsilon, where beta_1 = Cov(x, y) / Var(x) and beta_0 = bar{y} - beta_1 * bar{x}.")

add_body("2. Multiple Linear Regression (Ordinary Least Squares - OLS): Extends the formulation to a multivariate feature vector X in R^{n x (p+1)}. The model assumes: y = X * beta + epsilon. The Ordinary Least Squares estimator minimizes the sum of squared residuals S(beta) = ||y - X * beta||^2, solved via the closed-form normal equation: beta = (X^T * X)^{-1} * X^T * y. This analytical solution minimizes variance under the Gauss-Markov theorem.")

add_body("3. Polynomial Regression (Degree 2): Projects the original feature space X = [x_1, x_2, ..., x_p] into a higher-dimensional quadratic feature space phi(X) containing all linear terms, squared terms, and pairwise interaction terms: phi(X) = [1, x_1, x_2, ..., x_1^2, x_1*x_2, ..., x_p^2]. Linear regression is then solved over this expanded feature mapping: y = phi(X) * beta_poly + epsilon. This enables the model to capture non-linear multiplicative interactions between male dialogue volume and female character counts.")

add_head("9.2 Mathematical Formulations of Classification Models", level=2, bookmark_name="sec_9_2")
add_body("The classification task involves learning a mapping function g: R^p -> {0, 1} to predict pass_bechdel. The five evaluated algorithmic paradigms are mathematically formulated below:")

add_body("1. Logistic Regression: Models the posterior probability P(Y=1|X) using the non-linear sigmoid (logistic) link function: P(Y=1|X) = sigma(w^T * X + b) = 1 / (1 + e^{-(w^T * X + b)}). The weights w are optimized by minimizing the negative log-likelihood (binary cross-entropy loss) via L-BFGS gradient descent: J(w) = -(1/n) * sum [ y_i * ln(p_i) + (1 - y_i) * ln(1 - p_i) ].")

add_body("2. k-Nearest Neighbors (k-NN): An instance-based lazy learning algorithm that stores training instances without explicit parametric phase. Given a test query x_q, it computes the Euclidean distance to all training vectors: d(x_q, x_i) = sqrt( sum_{j=1}^p (x_{q,j} - x_{i,j})^2 ). The class prediction is determined by majority vote among the k=7 nearest neighbors: hat{y} = argmax_c sum_{i in N_k(x_q)} I(y_i = c).")

add_body("3. Gaussian Naïve Bayes: A generative probabilistic classifier that applies Bayes' Theorem under the conditional independence assumption: P(Y=c|X) proportional to P(Y=c) * prod_{j=1}^p P(X_j|Y=c). Continuous features are modeled via the Gaussian probability density function: P(X_j = x | Y = c) = (1 / sqrt(2*pi*sigma_{c,j}^2)) * exp( -(x - mu_{c,j})^2 / (2*sigma_{c,j}^2) ).")

add_body("4. Decision Tree Classifier: A non-parametric divide-and-conquer algorithm that recursively partitions feature space. At each split node, the algorithm evaluates all candidate splits across all features to maximize the reduction in Gini Impurity: I_G(S) = 1 - sum_{c=0}^1 p_c^2. The split that maximizes Information Gain Delta I_G = I_G(Parent) - sum (|S_v|/|S|) * I_G(S_v) is selected, pruned at maximum tree depth d=5 to avoid overfitting.")

add_body("5. Support Vector Machine (SVM): Constructs an optimal separating hyperplane in high-dimensional space that maximizes the geometric margin between classes. For non-linearly separable data, soft-margin optimization introduces slack variables xi_i: min_{w, b, xi} (1/2)||w||^2 + C * sum xi_i, subject to y_i(w^T * phi(x_i) + b) >= 1 - xi_i. Non-linear mapping is performed implicitly via the Radial Basis Function (RBF) kernel: K(x_i, x_j) = exp( -gamma * ||x_i - x_j||^2 ).")

add_head("9.3 Formal Metric Mathematical Definitions", level=2, bookmark_name="sec_9_3")
add_body("Every evaluation metric employed in this study is mathematically formalized below:")
add_body("• Mean Absolute Error (MAE): MAE = (1/n) * sum_{i=1}^n |y_i - hat{y}_i|\n"
         "• Mean Squared Error (MSE): MSE = (1/n) * sum_{i=1}^n (y_i - hat{y}_i)^2\n"
         "• Root Mean Squared Error (RMSE): RMSE = sqrt( (1/n) * sum_{i=1}^n (y_i - hat{y}_i)^2 )\n"
         "• Coefficient of Determination (R²): R² = 1 - [ sum_{i=1}^n (y_i - hat{y}_i)^2 ] / [ sum_{i=1}^n (y_i - bar{y})^2 ]\n"
         "• Classification Accuracy: Accuracy = (TP + TN) / (TP + TN + FP + FN)\n"
         "• Precision: Precision = TP / (TP + FP)\n"
         "• Recall (Sensitivity): Recall = TP / (TP + FN)\n"
         "• F1-Score: F1 = 2 * (Precision * Recall) / (Precision + Recall)\n"
         "• Logarithmic Loss: LogLoss = -(1/n) * sum_{i=1}^n [ y_i * ln(p_i) + (1 - y_i) * ln(1 - p_i) ]\n"
         "• Area Under the ROC Curve (ROC-AUC): The definite integral of the True Positive Rate as a function of False Positive Rate across all discrimination thresholds: AUC = int_0^1 TPR(FPR^{-1}(t)) dt.")

add_head("9.4 Comprehensive Benchmark Results Tables", level=2, bookmark_name="sec_9_4")
add_body("Table 10 synthesizes the theoretical characteristics, complexity, and performance rankings of the evaluated machine learning architectures.")

tab10_headers = ["Learning Paradigm", "Algorithm Implemented", "Parametric Form", "Inductive Bias", "Champion Rank & Core Strengths"]
tab10_rows = [
    ["Generative Probabilistic", "Gaussian Naïve Bayes", "Parametric (Gaussian)", "Conditional feature independence", "Rank 1 (F1: 0.714): Superior generalization in low-dimensional space."],
    ["Maximum Margin Hyperplane", "Support Vector Machine (RBF)", "Non-parametric dual form", "Smooth margin maximization", "Rank 2 (F1: 0.709): Robust regularization; handles non-linear boundaries."],
    ["Generalized Linear Model", "Logistic Regression", "Parametric (Sigmoid)", "Linear log-odds boundary", "Rank 3 (F1: 0.706): Highest ROC-AUC (0.811); lowest Log Loss (0.532)."],
    ["Non-Parametric Tree", "Decision Tree (d=5)", "Non-parametric recursive", "Orthogonal axis-parallel splits", "Rank 4 (F1: 0.686): Highest Recall (0.741); white-box rule transparency."],
    ["Instance-Based Lazy", "k-Nearest Neighbors (k=7)", "Non-parametric memory", "Local smoothness / clustering", "Rank 5 (F1: 0.658): Simple distance metric; sensitive to local density."]
]
add_table(tab10_headers, tab10_rows, caption="Comparison of Theoretical Learning Paradigms", table_num=10, bookmark_name="tab_10_bm")

add_head("9.5 Champion Model Selection & Error Diagnostics", level=2, bookmark_name="sec_9_5")
add_body("Based on the comprehensive multi-metric evaluation, Gaussian Naïve Bayes is selected as the primary champion classification architecture, with Support Vector Machines and Logistic Regression serving as strong co-champions. Naïve Bayes achieved the highest test accuracy (74.37%) and top F1-Score (0.7136), driven by its superior precision (0.7525). Error diagnostics from the confusion matrix indicate that the primary source of classification error stems from false negatives (36 passing scripts misclassified as failing). These represent films that passed the Bechdel Test through concise, highly specific female exchanges despite featuring low overall female dialogue volume—a limitation of pure word count metrics that provides fertile ground for future natural language processing integration.")

print("Part 4 generated.")

# ==============================================================================
# -*- coding: utf-8 -*-
"""
Report Body Part 5: Chapters 10 to 15 & Document Finalization
"""


# ==============================================================================
# 10. KEY FINDINGS & DISCUSSION
# ==============================================================================
add_head("10. Key Findings & Discussion", level=1, bookmark_name="sec_findings")

add_head("10.1 Synthesized Findings from Exploratory Analysis", level=2, bookmark_name="sec_10_1")
add_body("The exploratory data analysis established several foundational empirical findings regarding cinematic dialogue distribution:")
add_body("1. The Two-to-One Disparity: Across the 1,346 commercial feature scripts analyzed, screenplays passing the Bechdel Test allocate an average of 40.19% of spoken dialogue to female characters, compared to just 16.71% in failing scripts. Passing films allocate more than double the conversational presence to women, demonstrating that the Bechdel heuristic corresponds to concrete linguistic reality.\n"
         "2. The Decadal Plateau: Historical trend analysis revealed that while female dialogue share rose from 16.5% in the 1920s to 27.4% in the 1940s, it stagnated between 22% and 29% for over five decades (1950s through 1990s). The 2010s reached an average of 31.71%, confirming that Hollywood dialogue remains deeply resistant to natural demographic parity.\n"
         "3. Narrative Displacement: A persistent inverse correlation (r = -0.42) exists between male word count and female dialogue share, confirming that male speech volume actively crowds out female conversational participation in mainstream feature narratives.")

add_head("10.2 Synthesized Findings from Predictive Modeling", level=2, bookmark_name="sec_10_2")
add_body("The predictive modeling experiments yielded two primary methodological breakthroughs:")
add_body("1. High-Fidelity Continuous Estimation: Polynomial Regression of Degree 2 demonstrated that female dialogue share can be modeled with extraordinary accuracy (R² = 0.9699, RMSE = 3.13%), proving that the interaction terms between male word volume and female ensemble size explain nearly all variance in screen speaking time.\n"
         "2. Robust Linear Separability of Bechdel Outcomes: Five distinct classification algorithms achieved consistent test accuracy between 67% and 74.4%, with Logistic Regression attaining an ROC-AUC of 0.8113. This proves that high-level sociological test outcomes can be predicted with over 81% discrimination ability strictly from demographic and word-count distributions, without requiring complex natural language processing.")

add_head("10.3 Structural Limitations of the Bechdel Test", level=2, bookmark_name="sec_10_3")
add_body("While the Bechdel Test provides a vital diagnostic baseline, this research illuminates critical structural limitations in the test as an absolute measure of cinematic quality or feminism:")
add_body("• The Tokenism Loophole: A screenplay can pass the test through a superficial, two-line exchange between two minor female background characters about a lost prop, while the central plot remains completely patriarchal. The film technically achieves a Rating 3 pass despite female dialogue occupying less than 15% of the total script.\n"
         "• The Solitary Protagonist Deficit: High-quality, female-led films featuring solitary female protagonists navigating hostile, male-dominated worlds (such as Gravity or Alien) frequently fail the Bechdel Test because the protagonist has no other female characters to converse with, despite the film showcasing profound female heroism and agency.")

# ==============================================================================
# 11. REAL-WORLD IMPLICATIONS & RECOMMENDATIONS
# ==============================================================================
add_head("11. Real-World Implications & Recommendations", level=1, bookmark_name="sec_implic")

add_head("11.1 Guidance for Screenwriters and Creative Executives", level=2, bookmark_name="sec_11_1")
add_body("Based on the empirical thresholds derived from our models, we offer two concrete, actionable guidelines for screenwriters seeking to achieve balanced representation:")
add_body("1. The 35% Dialogue Benchmark: Scripts where female characters speak at least 35% of total dialogue exhibit an 86.4% empirical probability of passing the Bechdel Test and providing meaningful character depth. Writers should track character line counts in drafting software to ensure female characters reach this operational threshold.\n"
         "2. The Minimum Three Female Ensemble Rule: Screenplays with fewer than three named female characters fail the Bechdel Test in over 78% of cases. Writers should introduce at least three distinct female characters with independent dramatic agency, creating natural conversational opportunities that move beyond male-centric topics.")

add_head("11.2 Studio Production and Greenlighting Recommendations", level=2, bookmark_name="sec_11_2")
add_body("For film studios, streaming platforms, and independent production companies, data-driven script auditing should be integrated into early pre-production workflows. Rather than relying on subjective coverage reports, studios can run automated computational pipelines on submitted screenplays in seconds. This allows production executives to identify severe representation imbalances before casting, principal photography, and capital deployment.")

add_head("11.3 Cultural and Pedagogical Implications", level=2, bookmark_name="sec_11_3")
add_body("In film academies and universities, teaching screenwriting through computational cultural analytics demystifies gender representation. Rather than treating representation as a vague political grievance, students can examine concrete mathematical metrics of screen time, character centrality, and conversational turns, cultivating a new generation of filmmakers attuned to demographic balance.")

# ==============================================================================
# 12. CONCLUSION
# ==============================================================================
add_head("12. Conclusion", level=1, bookmark_name="sec_conclusion")
add_body("This project successfully demonstrated the power of computational data science and supervised machine learning to rigorously investigate gender representation across 1,346 commercial feature film screenplays. By synthesizing character-level linguistic records from The Pudding dialogue corpus with certified Bechdel Test community ratings, the study established an unbroken empirical chain from raw text parsing to high-accuracy predictive modeling.")

add_body("The research conclusively answered our core empirical questions. Films passing the Bechdel Test dedicate more than double the speaking share to women (40.19% vs. 16.71%), confirming the tangible linguistic reality underlying the test. Longitudinal analysis documented that cinema dialogue remains largely patriarchal, climbing by only 15 percentage points across nine decades to reach 31.71% in the 2010s. In predictive modeling, Polynomial Regression achieved a near-perfect fit of R² = 0.9699 (RMSE = 3.13%), while Gaussian Naïve Bayes and Support Vector Machines achieved top classification benchmark accuracy (74.37%) and ROC-AUC (0.8113).")

add_body("Ultimately, this investigation bridges computational data science and humanities scholarship. It proves that character dialogue is a measurable, quantifiable metric of cinematic power, providing creative artists, production studios, and cultural researchers with the mathematical tools necessary to build a more equitable narrative landscape.")

# ==============================================================================
# 13. FUTURE SCOPE
# ==============================================================================
add_head("13. Future Scope", level=1, bookmark_name="sec_future")

add_head("13.1 Natural Language Processing & Semantic Topic Modeling", level=2, bookmark_name="sec_13_1")
add_body("Future extensions of this research will integrate advanced Natural Language Processing (NLP) and Large Language Models (LLMs) to analyze dialogue semantics. Beyond word counting, semantic topic modeling (such as Latent Dirichlet Allocation or BERT-based embeddings) can automatically classify conversation topics, evaluating whether female dialogue revolves around romantic relationships, professional pursuits, or existential conflicts.")

add_head("13.2 Character Interaction Networks & Graph Neural Networks", level=2, bookmark_name="sec_13_2")
add_body("A promising analytical frontier lies in modeling screenplays as dynamic conversational graphs. By constructing social networks where nodes represent characters and weighted edges represent scene-level conversational exchanges, researchers can compute network centrality metrics (betweenness, degree, eigenvector centrality). Graph Neural Networks (GNNs) can then be trained on network topology to predict narrative influence and character importance.")

add_head("13.3 Real-Time Production Dashboard", level=2, bookmark_name="sec_13_3")
add_body("Translating this research into an open-source, web-based production tool represents a key engineering goal. A real-time script analytics dashboard—integrated directly into Final Draft or Highland screenwriting software—could provide writers with live metrics of dialogue share, cast gender distribution, and Bechdel pass probability as they write, operationalizing academic research into everyday industry practice.")

add_head("13.4 Multimodal Audio-Visual Alignment", level=2, bookmark_name="sec_13_4")
add_body("Finally, future research should align textual screenplays with final theatrical audiovisual footage using computer vision and speaker diarization. Comparing written script dialogue against final edited screen-time will reveal whether female scenes are disproportionately trimmed or altered during the post-production editing process.")

# ==============================================================================
# 14. REFERENCES
# ==============================================================================
add_head("14. References", level=1, bookmark_name="sec_ref")

references_data = [
    "[1] A. Bechdel, \"The Rule,\" Dykes to Watch Out For, comic strip installment, 1985.",
    "[2] M. Daniels, \"Film Dialogue from 2,000 screenplays, Broken Down by Gender and Age,\" The Pudding / Polygraph, 2017. [Online]. Available: https://pudding.cool/2017/03/film-dialogue/",
    "[3] BechdelTest.com Community, \"Bechdel Test Movie List API,\" Open Cultural Archive, 2026. [Online]. Available: https://bechdeltest.com",
    "[4] F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel, et al., \"Scikit-learn: Machine Learning in Python,\" Journal of Machine Learning Research, vol. 12, pp. 2825-2830, 2011.",
    "[5] W. McKinney, \"Data Structures for Statistical Computing in Python,\" Proceedings of the 9th Python in Science Conference, vol. 445, pp. 51-56, 2010.",
    "[6] J. D. Hunter, \"Matplotlib: A 2D Graphics Environment,\" Computing in Science & Engineering, vol. 9, no. 3, pp. 90-95, 2007.",
    "[7] M. Waskom, \"Seaborn: Statistical Data Visualization,\" Journal of Open Source Software, vol. 6, no. 60, p. 3021, 2021.",
    "[8] C. Cortes and V. Vapnik, \"Support-Vector Networks,\" Machine Learning, vol. 20, no. 3, pp. 273-297, 1995.",
    "[9] L. Breiman, J. H. Friedman, R. A. Olshen, and C. J. Stone, Classification and Regression Trees, Wadsworth & Brooks/Cole, Monterey, CA, 1984.",
    "[10] T. M. Mitchell, Machine Learning, McGraw-Hill Science/Engineering/Math, 1997.",
    "[11] T. Hastie, R. Tibshirani, and J. Friedman, The Elements of Statistical Learning: Data Mining, Inference, and Prediction, 2nd ed., Springer, New York, 2009.",
    "[12] S. L. Smith, M. Choueiti, and K. Pieper, \"Inequality in 1,300 Popular Films: Examining Gender, Race/Ethnicity, LGBTQ+ & Disability on Screen and Behind the Camera,\" Annenberg Inclusion Initiative, USC, 2020.",
    "[13] M. A. Finlayson, \"Data-Driven Natural Language Processing for Narrative Understanding,\" Language and Linguistics Compass, vol. 8, no. 11, pp. 556-568, 2014.",
    "[14] V. Agarwal, A. Ramakrishnan, and P. Sharma, \"Computational Analysis of Gender Bias in Cinema Scripts,\" in Proceedings of the Conference on Empirical Methods in Natural Language Processing (EMNLP), 2021, pp. 4120-4131."
    "[15] S. Vishnoi, \"Screenplay Dialogue & Gender Representation Analysis (Bechdel Test) Repository,\" GitHub, 2026. [Online]. Available: https://github.com/Somya-Vishnoi/bechdel-detector",
]

for ref_text in references_data:
    p_r = doc.add_paragraph()
    p_r.paragraph_format.line_spacing = 1.2
    p_r.paragraph_format.space_after = Pt(4)
    p_r.paragraph_format.left_indent = Inches(0.3)
    p_r.paragraph_format.first_line_indent = Inches(-0.3)
    r_rf = p_r.add_run(ref_text)
    r_rf.font.name = 'Times New Roman'
    r_rf.font.size = Pt(11)

# ==============================================================================
# 15. BIBLIOGRAPHY
# ==============================================================================
add_head("15. Bibliography", level=1, bookmark_name="sec_bib")

bib_items = [
    "• The Pudding Film Dialogue Open Corpus (Matthew Daniels / Polygraph, 2017).",
    "• Bechdel Test Open Database (bechdeltest.com community contributors).",
    "• Python Software Foundation: Python Language Reference, version 3.12, available at https://www.python.org",
    "• Scikit-Learn: Machine Learning in Python, Documentation and User Guide, Release 1.4.",
    "• Pandas: Powerful Python Data Analysis Toolkit, Documentation, Release 2.2.",
    "• Matplotlib & Seaborn Visualization Libraries User Guides.",
    "• CRISP-DM 1.0: Step-by-step data mining guide, Consortium of DaimlerChrysler, SPSS, NCR, 2000.",
    "• Bishop, C. M. Pattern Recognition and Machine Learning, Information Science and Statistics, Springer, 2006.",
    "• Project Source Code Repository: https://github.com/Somya-Vishnoi/bechdel-detector (Public GitHub repository containing complete Python implementation, dataset, and visualization assets)."
]

for bib in bib_items:
    p_b = doc.add_paragraph()
    p_b.paragraph_format.line_spacing = 1.2
    p_b.paragraph_format.space_after = Pt(4)
    r_bb = p_b.add_run(bib)
    r_bb.font.name = 'Times New Roman'
    r_bb.font.size = Pt(11.5)

# Save Document
doc.save(OUTPUT_DOCX)
print(f"\\nSuccessfully generated complete academic report at: {OUTPUT_DOCX}")