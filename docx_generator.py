import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from pathlib import Path
from config import TEMPLATE_DOCX_PATH, OUTPUT_DIR

COLOR_HEADER = RGBColor(0x00, 0x33, 0x66)    # Azul Escuro Institucional UFMG
COLOR_SUBHEADER = RGBColor(0x00, 0x66, 0x99) # Azul Secundário
COLOR_TEXT = RGBColor(0x2B, 0x2B, 0x2B)      # Grafite Escuro

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_title(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(17)
    run.font.bold = True
    run.font.color.rgb = COLOR_HEADER
    return p

def add_subtitle(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(12)
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(10.5)
    run.font.italic = True
    run.font.color.rgb = COLOR_SUBHEADER
    return p

def add_section_header(doc, number_str, title_str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    
    r_num = p.add_run(number_str + " ")
    r_num.font.name = 'Calibri'
    r_num.font.size = Pt(12)
    r_num.font.bold = True
    r_num.font.color.rgb = COLOR_SUBHEADER
    
    r_title = p.add_run(title_str.upper())
    r_title.font.name = 'Calibri'
    r_title.font.size = Pt(12)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_HEADER
    return p

def add_body_p(doc, text, bold_prefix=None):
    if not text:
        return None
    paragraphs = text.split("\n\n")
    last_p = None
    for i, part in enumerate(paragraphs):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        
        if bold_prefix and i == 0:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Calibri'
            r_pre.font.size = Pt(10)
            r_pre.font.bold = True
            r_pre.font.color.rgb = COLOR_TEXT
            
        r_text = p.add_run(part)
        r_text.font.name = 'Calibri'
        r_text.font.size = Pt(10)
        r_text.font.color.rgb = COLOR_TEXT
        last_p = p
    return last_p

def add_callout(doc, title, text, bg_hex="F0F4F8", border_hex="003366", icon="📌"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="24" w:space="0" w:color="{border_hex}"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    r_t = p.add_run(f"{icon} {title}\n")
    r_t.font.name = 'Calibri'
    r_t.font.size = Pt(10)
    r_t.font.bold = True
    r_t.font.color.rgb = COLOR_HEADER
    
    r_b = p.add_run(text)
    r_b.font.name = 'Calibri'
    r_b.font.size = Pt(9.5)
    r_b.font.italic = True
    r_b.font.color.rgb = COLOR_TEXT
    
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def add_fairs_table(doc, fairs_data):
    """Gera a tabela estruturada de Inteligência Competitiva de Feiras (WI, RC, UFRJ, PUC)."""
    tbl = doc.add_table(rows=1, cols=4)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    hdr_cells = tbl.rows[0].cells
    hdr_cells[0].width = Inches(2.2)
    hdr_cells[1].width = Inches(0.9)
    hdr_cells[2].width = Inches(0.9)
    hdr_cells[3].width = Inches(2.5)
    
    for c in hdr_cells:
        set_cell_background(c, "003366")
        set_cell_margins(c, top=80, bottom=80, left=100, right=100)
        
    p0 = hdr_cells[0].paragraphs[0]
    p0.add_run("Feira / Evento").font.bold = True
    p0.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p0.runs[0].font.size = Pt(9)
    
    p1 = hdr_cells[1].paragraphs[0]
    p1.add_run("2025").font.bold = True
    p1.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p1.runs[0].font.size = Pt(9)
    
    p2 = hdr_cells[2].paragraphs[0]
    p2.add_run("2026").font.bold = True
    p2.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p2.runs[0].font.size = Pt(9)

    p3 = hdr_cells[3].paragraphs[0]
    p3.add_run("Detalhes da Participação").font.bold = True
    p3.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p3.runs[0].font.size = Pt(9)

    for item in fairs_data:
        row_cells = tbl.add_row().cells
        row_cells[0].width = Inches(2.2)
        row_cells[1].width = Inches(0.9)
        row_cells[2].width = Inches(0.9)
        row_cells[3].width = Inches(2.5)
        
        set_cell_background(row_cells[0], "F9FAFB")
        set_cell_background(row_cells[1], "FFFFFF")
        set_cell_background(row_cells[2], "FFFFFF")
        set_cell_background(row_cells[3], "FFFFFF")
        
        for c in row_cells:
            set_cell_margins(c, top=60, bottom=60, left=100, right=100)
            
        p_f = row_cells[0].paragraphs[0]
        r_f = p_f.add_run(item.get("feira", ""))
        r_f.font.bold = True
        r_f.font.size = Pt(8.5)
        
        p_s25 = row_cells[1].paragraphs[0]
        r_s25 = p_s25.add_run(item.get("status_2025", "Não"))
        r_s25.font.size = Pt(8.5)
        r_s25.font.bold = True
        if str(item.get("status_2025")).lower() in ["sim", "true"]:
            r_s25.font.color.rgb = RGBColor(0x28, 0xA7, 0x45)
            
        p_s26 = row_cells[2].paragraphs[0]
        r_s26 = p_s26.add_run(item.get("status_2026", "Não"))
        r_s26.font.size = Pt(8.5)
        r_s26.font.bold = True
        if str(item.get("status_2026")).lower() in ["sim", "true"]:
            r_s26.font.color.rgb = RGBColor(0x28, 0xA7, 0x45)

        p_det = row_cells[3].paragraphs[0]
        r_det = p_det.add_run(item.get("detalhes", ""))
        r_det.font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_objections_table(doc, objections_list):
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    hdr_cells = tbl.rows[0].cells
    hdr_cells[0].width = Inches(2.3)
    hdr_cells[1].width = Inches(4.2)
    set_cell_background(hdr_cells[0], "003366")
    set_cell_background(hdr_cells[1], "003366")
    set_cell_margins(hdr_cells[0], top=100, bottom=100, left=120, right=120)
    set_cell_margins(hdr_cells[1], top=100, bottom=100, left=120, right=120)
    
    p0 = hdr_cells[0].paragraphs[0]
    r0 = p0.add_run("Objeção Provável do Cliente")
    r0.font.bold = True
    r0.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    r0.font.size = Pt(9.5)
    
    p1 = hdr_cells[1].paragraphs[0]
    r1 = p1.add_run("Resposta Estruturada & Contra-Argumento Tático")
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    r1.font.size = Pt(9.5)

    for item in objections_list:
        row_cells = tbl.add_row().cells
        row_cells[0].width = Inches(2.3)
        row_cells[1].width = Inches(4.2)
        
        set_cell_background(row_cells[0], "F9FAFB")
        set_cell_background(row_cells[1], "FFFFFF")
        set_cell_margins(row_cells[0], top=80, bottom=80, left=120, right=120)
        set_cell_margins(row_cells[1], top=80, bottom=80, left=120, right=120)
        
        p_obj = row_cells[0].paragraphs[0]
        p_obj.paragraph_format.space_after = Pt(0)
        r_obj = p_obj.add_run(item.get("objecao", ""))
        r_obj.font.bold = True
        r_obj.font.size = Pt(9)
        r_obj.font.color.rgb = COLOR_TEXT
        
        p_resp = row_cells[1].paragraphs[0]
        p_resp.paragraph_format.space_after = Pt(0)
        r_resp = p_resp.add_run(item.get("resposta", ""))
        r_resp.font.size = Pt(9)
        r_resp.font.color.rgb = COLOR_TEXT

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(6)

def generate_one_page_docx(company_data, ai_analysis, output_dir=OUTPUT_DIR, template_path=TEMPLATE_DOCX_PATH):
    nome = company_data["nome"]
    
    if Path(template_path).exists():
        doc = docx.Document(template_path)
        for p in list(doc.paragraphs):
            p._element.getparent().remove(p._element)
        for t in list(doc.tables):
            t._element.getparent().remove(t._element)
    else:
        doc = docx.Document()

    # Cabeçalho Principal
    add_title(doc, f"DOSSIÊ ESTRATÉGICO DE INTELIGÊNCIA: {nome.upper()}")
    add_subtitle(doc, "Manual de Preparação e Suporte para Reunião Comercial — UFMG Hub / Feira de Carreiras")

    # Tabela 0: Ficha Técnica de Inteligência
    table = doc.add_table(rows=5, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    atuacao_raw = ai_analysis.get("atuacao_bh_mg_detalhada", "")
    tem_mg = "Sim" if "MINAS GERAIS: SIM" in atuacao_raw.upper() else ("Sim" if "MG" in atuacao_raw else "A confirmar")
    tem_bh = "Sim" if "BELO HORIZONTE: SIM" in atuacao_raw.upper() else ("Sim" if "BELO HORIZONTE" in atuacao_raw.upper() else "A confirmar")

    labels_data = [
        ("Empresa Prospectada", nome),
        ("Presença Regional (MG / BH)", f"Minas Gerais: {tem_mg} | Belo Horizonte: {tem_bh}"),
        ("Histórico Feira UFMG", f"2024: {company_data['participou_2024']} (Cota: {company_data['cota_2024']}) | 2025: {company_data['participou_2025']} (Cota: {company_data['cota_2025']}) | 2026: {company_data['participou_2026']} (Cota: {company_data['cota_2026']})"),
        ("Contato / Responsável", f"{company_data.get('nome_contato') or company_data.get('responsavel_2026') or 'A mapear'} ({company_data.get('email') or 'Sem e-mail cadastrado'})"),
        ("Feiras Mapeadas", "Workshop Integrativo (WI) e PUC Carreiras")
    ]

    for idx, (label, val) in enumerate(labels_data):
        row = table.rows[idx]
        cell_lbl, cell_val = row.cells[0], row.cells[1]
        cell_lbl.width = Inches(2.2)
        cell_val.width = Inches(4.3)
        
        set_cell_background(cell_lbl, "EBF3FA")
        set_cell_background(cell_val, "FAFAFA")
        set_cell_margins(cell_lbl, top=70, bottom=70, left=100, right=100)
        set_cell_margins(cell_val, top=70, bottom=70, left=100, right=100)
        
        p0 = cell_lbl.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(label)
        r0.font.bold = True
        r0.font.size = Pt(9)
        r0.font.color.rgb = COLOR_HEADER
        
        p1 = cell_val.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        r1.font.size = Pt(9)
        r1.font.color.rgb = COLOR_TEXT

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # 1. Visão Geral & Atuação no Mercado
    add_section_header(doc, "1.0", "Visão Geral Institucional & Foco de Mercado (Brasil & MG)")
    add_body_p(doc, ai_analysis.get("resumo_extenso", ""))

    # 2. Atuação em Belo Horizonte e MG
    add_section_header(doc, "2.0", "Presença Física, Fábricas e Localização de Operações em BH & MG")
    add_body_p(doc, ai_analysis.get("atuacao_bh_mg_detalhada", ""))

    # 3. Histórico de Relacionamento e Patrocínios
    add_section_header(doc, "3.0", "Histórico de Relacionamento & Análise de Patrocínios (2024 - 2026)")
    add_body_p(doc, ai_analysis.get("historico_relacionamento_analise", ""))

    # 4. Programas de Estágio e Trainee
    add_section_header(doc, "4.0", "Programas de Atração de Talentos em BH & MG (Estágio & Trainee)")
    add_body_p(doc, ai_analysis.get("programas_estagio_trainee_completo", ""))

    # 5. Inteligência Competitiva e Outras Feiras (Tabela Concreta)
    add_section_header(doc, "5.0", "Inteligência Competitiva & Presença Confirmada em Outros Eventos")
    add_fairs_table(doc, ai_analysis.get("outras_feiras_tabela", []))

    # 6. Posicionamento de Marca & ESG
    add_section_header(doc, "6.0", "Posicionamento de Marca, ESG & Inovação")
    add_body_p(doc, ai_analysis.get("posicionamento_esg_inovacao", ""))

    # 7. Manual de Reunião de Vendas (Guia Tático)
    add_section_header(doc, "7.0", "Guia Tático para Reunião Comercial com o Cliente")
    
    # 7.1 Ganchos de Abertura
    ganchos_txt = "\n".join([f"• {g}" for g in ai_analysis.get("guia_reuniao_ganchos", [])])
    add_callout(doc, "Ganchos de Abertura para Iniciar a Reunião", ganchos_txt, bg_hex="F4F6F9", border_hex="003366", icon="💡")

    # 7.2 Pitch Principal
    add_callout(doc, "Discurso Principal de Valor (Pitch B2B)", ai_analysis.get("guia_reuniao_pitch", ""), bg_hex="FFFDF0", border_hex="B8860B", icon="🎯")

    # 7.3 Tabela de Objeções
    add_body_p(doc, "Abaixo estão as objeções mais prováveis do cliente durante a reunião e as respostas recomendadas:", bold_prefix="Matriz de Objeções & Respostas Táticas: ")
    add_objections_table(doc, ai_analysis.get("guia_reuniao_objecoes", []))

    clean_filename = "".join(c for c in nome if c.isalnum() or c in (' ', '_', '-')).strip()
    output_filename = Path(output_dir) / f"Dossie_Estrategico_{clean_filename}.docx"
    doc.save(output_filename)
    return output_filename


def add_student_kpis_table(doc, stats):
    """Gera tabela de cartões de KPI com números reais da base de estudantes da UFMG."""
    tbl = doc.add_table(rows=2, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    kpis = [
        ("TOTAL DE INSCRITOS NA BASE UFMG", f"{stats.get('total_base', 7842):,}".replace(",", "."), "Base ativa de e-mail marketing / MEC"),
        ("PÚBLICO-ALVO NO PERFIL DA EMPRESA", f"{stats.get('total_target', 0):,} alunos ({stats.get('pct_target', 0)}%)".replace(",", "."), "Estudantes matriculados nos cursos prioritários"),
        ("ABERTOS A PROPOSTAS DE EMPREGO/ESTÁGIO", f"{stats.get('total_abertos', 0):,} alunos ({stats.get('pct_abertos', 0)}%)".replace(",", "."), "Alunos do público-alvo receptivos a contato direto"),
        ("FORMAÇÃO IMEDIATA / CURTÍSSIMO PRAZO", f"{stats.get('pipeline_formatura', [{}])[0].get('alunos', 0):,} alunos disponíveis".replace(",", "."), "Formandos 2025/2026 prontos para estágio final ou contratação")
    ]
    
    coords = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for idx, (r, c) in enumerate(coords):
        title, val, sub = kpis[idx]
        cell = tbl.rows[r].cells[c]
        cell.width = Inches(3.25)
        set_cell_background(cell, "F4F7FA")
        set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
        
        tcPr = cell._element.get_or_add_tcPr()
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="18" w:space="0" w:color="003366"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
        tcPr.append(borders)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r_t = p.add_run(title + "\n")
        r_t.font.name = 'Calibri'
        r_t.font.size = Pt(8.5)
        r_t.font.bold = True
        r_t.font.color.rgb = COLOR_SUBHEADER
        
        r_v = p.add_run(val + "\n")
        r_v.font.name = 'Calibri'
        r_v.font.size = Pt(13)
        r_v.font.bold = True
        r_v.font.color.rgb = COLOR_HEADER
        
        r_s = p.add_run(sub)
        r_s.font.name = 'Calibri'
        r_s.font.size = Pt(8)
        r_s.font.italic = True
        r_s.font.color.rgb = COLOR_TEXT
        
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def add_target_courses_table(doc, cursos_detalhe):
    """Gera a tabela estruturada de detalhamento por curso relevante."""
    tbl = doc.add_table(rows=1, cols=4)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    hdr = tbl.rows[0].cells
    hdr[0].width = Inches(2.2)
    hdr[1].width = Inches(0.9)
    hdr[2].width = Inches(1.0)
    hdr[3].width = Inches(2.4)
    
    for c in hdr:
        set_cell_background(c, "003366")
        set_cell_margins(c, top=80, bottom=80, left=100, right=100)
        
    p0 = hdr[0].paragraphs[0]
    p0.add_run("Curso Prioritário").font.bold = True
    p0.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p0.runs[0].font.size = Pt(9)
    
    p1 = hdr[1].paragraphs[0]
    p1.add_run("Inscritos").font.bold = True
    p1.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p1.runs[0].font.size = Pt(9)
    
    p2 = hdr[2].paragraphs[0]
    p2.add_run("Abertos (%)").font.bold = True
    p2.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p2.runs[0].font.size = Pt(9)
    
    p3 = hdr[3].paragraphs[0]
    p3.add_run("Relevância Técnica para a Empresa").font.bold = True
    p3.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p3.runs[0].font.size = Pt(9)
    
    for item in cursos_detalhe:
        row = tbl.add_row().cells
        row[0].width = Inches(2.2)
        row[1].width = Inches(0.9)
        row[2].width = Inches(1.0)
        row[3].width = Inches(2.4)
        
        set_cell_background(row[0], "F9FAFB")
        set_cell_background(row[1], "FFFFFF")
        set_cell_background(row[2], "FFFFFF")
        set_cell_background(row[3], "FFFFFF")
        
        for c in row:
            set_cell_margins(c, top=60, bottom=60, left=100, right=100)
            
        p_c = row[0].paragraphs[0]
        r_c = p_c.add_run(item.get("curso", ""))
        r_c.font.bold = True
        r_c.font.size = Pt(8.5)
        
        p_ins = row[1].paragraphs[0]
        r_ins = p_ins.add_run(str(item.get("inscritos", 0)))
        r_ins.font.size = Pt(8.5)
        r_ins.font.bold = True
        
        p_ab = row[2].paragraphs[0]
        r_ab = p_ab.add_run(f"{item.get('pct_abertos', 0)}%")
        r_ab.font.size = Pt(8.5)
        r_ab.font.bold = True
        r_ab.font.color.rgb = RGBColor(0x28, 0xA7, 0x45)
        
        p_rel = row[3].paragraphs[0]
        r_rel = p_rel.add_run(item.get("relevancia", ""))
        r_rel.font.size = Pt(8.5)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def add_graduation_pipeline_table(doc, pipeline_data):
    """Gera a tabela estruturada de formatura por ano."""
    tbl = doc.add_table(rows=1, cols=4)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    hdr = tbl.rows[0].cells
    hdr[0].width = Inches(1.5)
    hdr[1].width = Inches(1.0)
    hdr[2].width = Inches(1.2)
    hdr[3].width = Inches(2.8)
    
    for c in hdr:
        set_cell_background(c, "003366")
        set_cell_margins(c, top=80, bottom=80, left=100, right=100)
        
    hdr[0].paragraphs[0].add_run("Ano de Formatura").font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    hdr[0].paragraphs[0].runs[0].font.bold = True
    hdr[0].paragraphs[0].runs[0].font.size = Pt(9)
    
    hdr[1].paragraphs[0].add_run("Alunos").font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    hdr[1].paragraphs[0].runs[0].font.bold = True
    hdr[1].paragraphs[0].runs[0].font.size = Pt(9)
    
    hdr[2].paragraphs[0].add_run("% Público-Alvo").font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    hdr[2].paragraphs[0].runs[0].font.bold = True
    hdr[2].paragraphs[0].runs[0].font.size = Pt(9)
    
    hdr[3].paragraphs[0].add_run("Perfil de Contratação Recomendado").font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    hdr[3].paragraphs[0].runs[0].font.bold = True
    hdr[3].paragraphs[0].runs[0].font.size = Pt(9)
    
    for item in pipeline_data:
        row = tbl.add_row().cells
        row[0].width = Inches(1.5)
        row[1].width = Inches(1.0)
        row[2].width = Inches(1.2)
        row[3].width = Inches(2.8)
        
        set_cell_background(row[0], "F9FAFB")
        set_cell_background(row[1], "FFFFFF")
        set_cell_background(row[2], "FFFFFF")
        set_cell_background(row[3], "FFFFFF")
        
        for c in row:
            set_cell_margins(c, top=60, bottom=60, left=100, right=100)
            
        r0 = row[0].paragraphs[0].add_run(str(item.get("ano", "")))
        r0.font.bold = True
        r0.font.size = Pt(8.5)
        
        r1 = row[1].paragraphs[0].add_run(str(item.get("alunos", 0)))
        r1.font.bold = True
        r1.font.size = Pt(8.5)
        
        r2 = row[2].paragraphs[0].add_run(f"{item.get('pct', 0)}%")
        r2.font.bold = True
        r2.font.size = Pt(8.5)
        
        r3 = row[3].paragraphs[0].add_run(str(item.get("perfil", "")))
        r3.font.size = Pt(8.5)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def generate_post_meeting_docx(company_data, ai_analysis, student_stats=None, output_dir=OUTPUT_DIR, template_path=TEMPLATE_DOCX_PATH):
    """Gera o dossiê avançado de PÓS-REUNIÃO com inteligência de público filtrada, pipeline de estágio e iniciativas UFMG."""
    nome = company_data["nome"]
    
    if student_stats is None:
        from student_analyzer import analyze_student_base
        student_stats = analyze_student_base(nome)
        
    if Path(template_path).exists():
        doc = docx.Document(template_path)
        for p in list(doc.paragraphs):
            p._element.getparent().remove(p._element)
        for t in list(doc.tables):
            t._element.getparent().remove(t._element)
    else:
        doc = docx.Document()
        
    # Cabeçalho Principal Executivo
    add_title(doc, f"INTELIGÊNCIA DE PÚBLICO & DOSSIÊ PÓS-REUNIÃO: {nome.upper()}")
    add_subtitle(doc, "Mercado em Conexão — UFMG Hub · Dados Filtrados da Base Universitária e Pipeline de Contratação")
    
    # Ficha Técnica de Metadados da Reunião
    table = doc.add_table(rows=4, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    labels_data = [
        ("Empresa / Organização", f"{nome} (Operações em MG e Brasil)"),
        ("Interlocutor / Ponto Focal", f"{company_data.get('nome_contato') or company_data.get('responsavel_2026') or 'Representante Técnico/Comercial'} ({company_data.get('email') or 'Sem e-mail cadastrado'})"),
        ("Momento Negocial", "Pós-Reunião Comercial — Apresentação de Dados de Público & Fechamento de Cota"),
        ("Status na Feira UFMG", f"Histórico: 2024 ({company_data.get('participou_2024', 'Não')}) | 2025 ({company_data.get('participou_2025', 'Não')}) | 2026 ({company_data.get('cota_2026') or 'Em negociação'})")
    ]
    
    for idx, (label, val) in enumerate(labels_data):
        row = table.rows[idx]
        cell_lbl, cell_val = row.cells[0], row.cells[1]
        cell_lbl.width = Inches(2.2)
        cell_val.width = Inches(4.3)
        
        set_cell_background(cell_lbl, "EBF3FA")
        set_cell_background(cell_val, "FAFAFA")
        set_cell_margins(cell_lbl, top=70, bottom=70, left=100, right=100)
        set_cell_margins(cell_val, top=70, bottom=70, left=100, right=100)
        
        p0 = cell_lbl.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(label)
        r0.font.bold = True
        r0.font.size = Pt(9)
        r0.font.color.rgb = COLOR_HEADER
        
        p1 = cell_val.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        r1.font.size = Pt(9)
        r1.font.color.rgb = COLOR_TEXT
        
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    
    # 01. Dimensão do Público-Alvo na Base UFMG
    add_section_header(doc, "01", "Dimensão do Público-Alvo na Base Universitária da UFMG")
    add_body_p(doc, f"Os dados abaixo foram extraídos diretamente da base oficial de estudantes inscritos na Feira de Carreiras da UFMG (Mercado em Conexão), filtrados com base no perfil de contratação técnica e corporativa da {nome}. Representa a mensuração exata do alcance presencial que a empresa atinge no campus.")
    add_student_kpis_table(doc, student_stats)
    
    # 02. Detalhe por Curso
    add_section_header(doc, "02", f"Detalhamento por Curso Prioritário — Engajamento e Relevância Técnica")
    add_body_p(doc, f"A distribuição abaixo demonstra a densidade de estudantes nos cursos prioritários para a {nome}, bem como a taxa de alunos ativamente abertos a receber propostas de estágio e trabalho:")
    add_target_courses_table(doc, student_stats.get("cursos_detalhe", []))
    
    # 03. Pipeline de Formatura, Estágio & Trainee
    add_section_header(doc, "03", "Pipeline de Formatura & Estrutura dos Programas (Estágio & Trainee)")
    add_body_p(doc, "Mapeamento temporal de formatura dos estudantes no perfil da empresa, fundamental para calibrar o funil de estagiários de curto prazo versus pipeline de aceleração/trainee:")
    add_graduation_pipeline_table(doc, student_stats.get("pipeline_formatura", []))
    
    # Respostas para as 3 perguntas estruturantes
    estagio_txt = ai_analysis.get("duracao_estagio", "")
    trainee_txt = ai_analysis.get("duracao_trainee", "")
    ciclos_txt = ai_analysis.get("ciclos_processo_seletivo", "")
    
    add_callout(doc, "Duração do Programa de Estágio & Modelo de Trabalho", estagio_txt, bg_hex="F4F6F9", border_hex="003366", icon="⏳")
    add_callout(doc, "Duração do Programa de Trainee & Aceleração Executiva", trainee_txt, bg_hex="F4F6F9", border_hex="006699", icon="🚀")
    add_callout(doc, "Ciclos de Abertura dos Processos Seletivos (Estágio & Trainee)", ciclos_txt, bg_hex="FFFDF0", border_hex="B8860B", icon="📅")
    
    # 04. Atuação Prévia dentro da UFMG
    add_section_header(doc, "04", f"Atuação Prévia da {nome} dentro do Campus da UFMG")
    add_body_p(doc, ai_analysis.get("atuacao_previa_ufmg", f"Histórico de relacionamento e atração com a Escola de Engenharia da UFMG."))
    
    # 05. Iniciativas da UFMG que Mais Agregam para a Empresa
    add_section_header(doc, "05", f"Iniciativas da UFMG que Mais Agregam para a {nome} (Arena de Iniciativas)")
    add_body_p(doc, ai_analysis.get("iniciativas_ufmg_agregadoras", ""))
    
    # 06. Inteligência de Marca & Top of Mind
    add_section_header(doc, "06", f"Inteligência de Marca & Onde a {nome} Está no Radar dos Alunos")
    add_body_p(doc, ai_analysis.get("inteligencia_marca_top_of_mind", ""))
    
    # 07. Roteiro Tático de Fechamento Pós-Reunião
    add_section_header(doc, "07", "Roteiro Tático de Fechamento Pós-Reunião & Proposta de Cotas")
    add_callout(doc, "Argumento Pronto para o Fechamento / Upsell", ai_analysis.get("roteiro_fechamento_cotas", ""), bg_hex="F0FDF4", border_hex="16A34A", icon="🎯")
    
    # 08. Matriz de Objeções Pós-Reunião
    add_section_header(doc, "08", "Matriz Tática de Objeções de Pós-Reunião & Respostas Prontas")
    add_objections_table(doc, ai_analysis.get("matriz_objecoes_pos", []))
    
    clean_filename = "".join(c for c in nome if c.isalnum() or c in (' ', '_', '-')).strip()
    output_filename = Path(output_dir) / f"Dossie_PosReuniao_{clean_filename}.docx"
    doc.save(output_filename)
    return output_filename
