"""core/pdf_generator.py — Génération PDF professionnelle avec ReportLab"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
import os
from pathlib import Path
import tempfile
from core.styles import BILAN_FIELDS
from core.fonts import F, init_fonts

# ── Couleurs ──────────────────────────────────────────────────
OR      = colors.HexColor("#d4a853")
NOIR    = colors.HexColor("#1a1814")
GRIS    = colors.HexColor("#666666")
GRIS_L  = colors.HexColor("#f5f4f0")
GRIS_LL = colors.HexColor("#faf9f7")
VERT    = colors.HexColor("#2e6b4a")
BLANC   = colors.white
AMBER   = colors.HexColor("#fff8ec")
VERT_L  = colors.HexColor("#ecfbf4")
BORDER  = colors.HexColor("#dddddd")


def fmt_money(val):
    try:
        return f"{float(val):,.2f} \u20ac".replace(",", "\u202f").replace(".", ",")
    except Exception:
        return "0,00 \u20ac"


def generate_pdf(doc_data, lignes, bilan, settings, output_path=None):
    init_fonts()  # charge les polices TTF une seule fois

    if not output_path:
        numero = doc_data.get("numero", "document")
        output_path = str(Path(tempfile.gettempdir()) / f"{numero}.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=18*mm,  bottomMargin=18*mm,
        title=doc_data.get("numero", "Document"),
    )

    story = []
    W = A4[0] - 36*mm

    # ── Styles ────────────────────────────────────────────────
    def S(name, font, size, color=NOIR, align=TA_LEFT, leading=None, **kw):
        return ParagraphStyle(name, fontName=font, fontSize=size,
                              textColor=color, alignment=align,
                              leading=leading or size*1.4, **kw)

    s_body   = S("body",   F("F-Sans"),        9,  colors.HexColor("#333333"))
    s_small  = S("small",  F("F-Sans"),        8,  GRIS)
    s_bold   = S("bold",   F("F-Sans-Bold"),   9,  NOIR)
    s_italic = S("italic", F("F-Sans-Italic"), 8,  GRIS)
    s_center = S("center", F("F-Sans"),        8,  GRIS,  align=TA_CENTER)

    # Nom entreprise — Playfair + grand
    s_company= S("company",F("F-Serif-Bold"), 14,  NOIR,  leading=17)
    # Type document (FACTURE / DEVIS) — Playfair doré, grand
    s_doctype= S("dtype",  F("F-Serif-Bold"), 28,  OR,    align=TA_RIGHT, leading=32)
    # Numéro document — mono
    s_num    = S("num",    F("F-Mono"),       11,  GRIS,  align=TA_RIGHT)
    s_right  = S("right",  F("F-Sans"),        9,  GRIS,  align=TA_RIGHT)
    # Étiquettes et valeurs dans le bloc client
    s_lbl    = S("lbl",    F("F-Sans-Bold"),   7,  GRIS,  spaceAfter=3, leading=9)
    s_cname  = S("cname",  F("F-Sans-Bold"),  12,  NOIR,  leading=15)
    s_caddr  = S("caddr",  F("F-Sans"),        9,  colors.HexColor("#444444"))
    s_gname  = S("gname",  F("F-Sans-Bold"),  10,  NOIR)
    # Tableau lignes
    s_th     = S("th",     F("F-Sans-Bold"),   8,  BLANC)
    s_th_r   = S("th_r",   F("F-Sans-Bold"),   8,  BLANC, align=TA_RIGHT)
    s_td     = S("td",     F("F-Sans"),         9,  NOIR)
    s_td_r   = S("td_r",   F("F-Mono"),        9,  NOIR,  align=TA_RIGHT)
    s_total  = S("total",  F("F-Sans-Bold"),  11,  NOIR,  align=TA_RIGHT)
    s_total_l= S("total_l",F("F-Sans-Bold"),  10,  NOIR)
    s_mono_r = S("monor",  F("F-Mono"),        9,  GRIS,  align=TA_RIGHT)
    # Objet
    s_objet  = S("objet",  F("F-Sans"),        9,  NOIR)
    # Bilan
    s_bh_av  = S("bhav",   F("F-Sans-Bold"),   7,  colors.HexColor("#b8860b"), align=TA_CENTER, leading=9)
    s_bh_ap  = S("bhap",   F("F-Sans-Bold"),   7,  colors.HexColor("#2e7d52"), align=TA_CENTER, leading=9)
    s_bpt    = S("bpt",    F("F-Sans-Bold"),   7,  colors.HexColor("#555555"), leading=9)
    s_bval   = S("bval",   F("F-Sans"),         8,  NOIR)
    s_bem    = S("bem",    F("F-Sans-Italic"),  8,  colors.HexColor("#999999"))
    s_btitle = S("btitle", F("F-Serif-Bold"),  10,  NOIR)
    s_obs    = S("obs",    F("F-Sans"),         8,  GRIS)

    is_facture = doc_data.get("type") == "facture"
    doc_label  = "FACTURE" if is_facture else "DEVIS"
    numero     = doc_data.get("numero", "\u2014")

    # ── EN-TÊTE ───────────────────────────────────────────────
    company_lines = []
    if settings.get("name"):
        company_lines.append(Paragraph(settings["name"], s_company))
    for field, label in [("address",""), ("city",""), ("phone","T\u00e9l : "),
                          ("email",""), ("siret","SIRET : "), ("tva","N\u00b0 TVA : ")]:
        val = settings.get(field, "")
        if val:
            company_lines.append(Paragraph(f"{label}{val}", s_small))

    doc_info = [
        Paragraph(doc_label, s_doctype),
        Paragraph(f'N\u00b0 {numero}', s_num),
        Spacer(1, 4),
        Paragraph(f'Date : {_fmt_date(doc_data.get("date_doc",""))}', s_right),
    ]
    if doc_data.get("date_echeance"):
        doc_info.append(Paragraph(f'\u00c9ch\u00e9ance : {_fmt_date(doc_data["date_echeance"])}', s_right))
    if doc_data.get("devis_ref"):
        doc_info.append(Paragraph(f'R\u00e9f. devis : {doc_data["devis_ref"]}', s_right))

    # Logo
    logo_img = None
    lp = settings.get("logo_path", "")
    if lp and os.path.exists(lp):
        try:
            from reportlab.platypus import Image as RLImage
            logo_img = RLImage(lp, width=45*mm, height=20*mm, kind='proportional')
        except Exception:
            pass

    left = ([logo_img, Spacer(1, 6)] if logo_img else []) + company_lines

    hdr = Table([[left, doc_info]], colWidths=[W*0.55, W*0.45])
    hdr.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 8*mm))

    # ── BLOC CLIENT ───────────────────────────────────────────
    cname = _client_name(doc_data)
    caddr = "<br/>".join(filter(None, [
        doc_data.get("client_adresse", ""),
        " ".join(filter(None, [doc_data.get("client_cp",""), doc_data.get("client_ville","")])),
        doc_data.get("client_email", ""),
        doc_data.get("client_tel", "") or doc_data.get("client_telephone",""),
    ]))

    client_block = [Paragraph("FACTUR\u00c9 \u00c0" if is_facture else "DESTINATAIRE", s_lbl),
                    Paragraph(cname, s_cname)]
    if caddr:
        client_block.append(Paragraph(caddr, s_caddr))

    if doc_data.get("guitare_marque"):
        gn = f'{doc_data["guitare_marque"]} {doc_data.get("guitare_modele","")}'
        if doc_data.get("guitare_serie"):
            gn += f'  \u2014  N\u00b0 {doc_data["guitare_serie"]}'
        instr = [Paragraph("INSTRUMENT", s_lbl), Paragraph(f"\U0001f3b8  {gn}", s_gname)]
        meta = Table([[client_block, instr]], colWidths=[W*0.55, W*0.45])
        meta.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), GRIS_LL),
            ("BOX",           (0,0), (-1,-1), 0.5, OR),
            ("LINEBEFORE",    (1,0), (1,-1),  0.5, BORDER),
            ("LEFTPADDING",   (0,0), (-1,-1), 14),
            ("RIGHTPADDING",  (0,0), (-1,-1), 14),
            ("TOPPADDING",    (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 10),
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ]))
    else:
        meta = Table([[client_block]], colWidths=[W])
        meta.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), GRIS_LL),
            ("BOX",           (0,0), (-1,-1), 0.5, OR),
            ("LEFTPADDING",   (0,0), (-1,-1), 14),
            ("RIGHTPADDING",  (0,0), (-1,-1), 14),
            ("TOPPADDING",    (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 10),
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ]))
    story.append(meta)
    story.append(Spacer(1, 6*mm))

    # Objet
    if doc_data.get("objet"):
        story.append(Paragraph(f'<b>Objet :</b> {doc_data["objet"]}', s_objet))
        story.append(Spacer(1, 4*mm))

    # ── LIGNES ────────────────────────────────────────────────
    col_w = [W*0.5, W*0.1, W*0.2, W*0.2]
    rows = [[Paragraph("D\u00c9SIGNATION", s_th), Paragraph("QT\u00c9", s_th_r),
             Paragraph("PU HT", s_th_r), Paragraph("TOTAL HT", s_th_r)]]
    for i, l in enumerate(lignes):
        qte  = float(l.get("quantite", 1) or 1)
        pu   = float(l.get("prix_ht",  0) or 0)
        rows.append([
            Paragraph(str(l.get("designation","")), s_td),
            Paragraph(f'{qte:g}',      s_td_r),
            Paragraph(fmt_money(pu),   s_td_r),
            Paragraph(fmt_money(qte*pu), s_td_r),
        ])

    items = Table(rows, colWidths=col_w)
    ts = TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  NOIR),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ("LINEBELOW",     (0,0), (-1,-1), 0.5, BORDER),
        ("ALIGN",         (1,0), (-1,-1), "RIGHT"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ])
    for i in range(1, len(rows)):
        if i % 2 == 0:
            ts.add("BACKGROUND", (0,i), (-1,i), GRIS_LL)
    items.setStyle(ts)
    story.append(items)
    story.append(Spacer(1, 4*mm))

    # ── TOTAUX ────────────────────────────────────────────────
    tva_rate  = float(doc_data.get("tva_rate",  20) or 0)
    total_ht  = float(doc_data.get("total_ht",  0)  or 0)
    total_tva = float(doc_data.get("total_tva", 0)  or 0)
    total_ttc = float(doc_data.get("total_ttc", 0)  or 0)

    def mrow(label_p, val_p):
        return [label_p, val_p]

    tot_data = [
        mrow(Paragraph("Sous-total HT", s_body), Paragraph(fmt_money(total_ht), s_mono_r)),
        mrow(Paragraph(f'TVA ({tva_rate:g}%)', s_body), Paragraph(fmt_money(total_tva), s_mono_r)),
        mrow(Paragraph("TOTAL TTC", s_total_l), Paragraph(fmt_money(total_ttc), s_total)),
    ]
    tot_tbl = Table(tot_data, colWidths=[W*0.6, W*0.4], hAlign="RIGHT")
    tot_tbl.setStyle(TableStyle([
        ("ALIGN",         (1,0), (1,-1), "RIGHT"),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LINEABOVE",     (0,2), (-1,2), 1.5, NOIR),
        ("LINEBELOW",     (0,2), (-1,2), 1.5, NOIR),
        ("BACKGROUND",    (0,2), (-1,2), GRIS_LL),
    ]))
    story.append(tot_tbl)

    if tva_rate == 0:
        story.append(Spacer(1, 2*mm))
        story.append(Paragraph("TVA non applicable \u2014 art. 293B du CGI", s_small))

    # ── NOTES ─────────────────────────────────────────────────
    if doc_data.get("notes"):
        story.append(Spacer(1, 5*mm))
        n = Table([[Paragraph(doc_data["notes"], s_obs)]], colWidths=[W])
        n.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), GRIS_LL),
            ("BOX",           (0,0), (-1,-1), 0.5, BORDER),
            ("LEFTPADDING",   (0,0), (-1,-1), 10),
            ("RIGHTPADDING",  (0,0), (-1,-1), 10),
            ("TOPPADDING",    (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ]))
        story.append(n)

    # ── BILAN TECHNIQUE ───────────────────────────────────────
    bilan_rows = [(k, lbl) for k, lbl in BILAN_FIELDS
                  if bilan.get(k,{}).get("avant","") or bilan.get(k,{}).get("apres","")]
    if bilan_rows:
        story.append(Spacer(1, 6*mm))
        story.append(KeepTogether(
            _build_bilan(bilan, bilan_rows, W, s_btitle, s_bh_av, s_bh_ap, s_bpt, s_bval, s_bem, s_obs)
        ))

    # ── COORDONNÉES BANCAIRES ─────────────────────────────────
    if settings.get("iban"):
        story.append(Spacer(1, 5*mm))
        txt = f'<b>Coordonn\u00e9es bancaires :</b> IBAN : {settings["iban"]}'
        if settings.get("bic"):  txt += f' \u2014 BIC : {settings["bic"]}'
        if settings.get("bank"): txt += f' \u2014 {settings["bank"]}'
        ib = Table([[Paragraph(txt, s_obs)]], colWidths=[W])
        ib.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), GRIS_LL),
            ("LEFTPADDING",   (0,0), (-1,-1), 10),
            ("RIGHTPADDING",  (0,0), (-1,-1), 10),
            ("TOPPADDING",    (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LINELEFT",      (0,0), (0,-1),  3, OR),
        ]))
        story.append(ib)

    # ── MENTIONS LÉGALES ──────────────────────────────────────
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width=W, thickness=0.5, color=BORDER))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(settings.get("mentions",""), s_center))

    doc.build(story)
    return output_path


# ── Helpers ───────────────────────────────────────────────────

def _fmt_date(d):
    if not d: return "\u2014"
    try:
        p = d.split("-")
        return f"{p[2]}/{p[1]}/{p[0]}"
    except Exception:
        return d


def _client_name(doc_data):
    parts = []
    if doc_data.get("client_societe"): parts.append(doc_data["client_societe"])
    n = " ".join(filter(None, [doc_data.get("client_prenom",""), doc_data.get("client_nom","")]))
    if n: parts.append(n)
    return " \u2014 ".join(parts) if parts else "\u2014"


def _build_bilan(bilan, bilan_rows, W, s_title, s_bh_av, s_bh_ap, s_bpt, s_bval, s_bem, s_obs):
    from reportlab.lib import colors as C

    AMBER2 = colors.HexColor("#fff8ec")
    VERT2  = colors.HexColor("#ecfbf4")
    AMBERB = colors.HexColor("#f5dfa0")
    VERTB  = colors.HexColor("#a0d4b8")

    elements = []

    title_tbl = Table([[Paragraph("\U0001f3b8  BILAN TECHNIQUE DE LA GUITARE", s_title)]], colWidths=[W])
    title_tbl.setStyle(TableStyle([
        ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ("RIGHTPADDING",  (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LINEBELOW",     (0,0), (-1,0),  1.5, OR),
    ]))
    elements.append(title_tbl)
    elements.append(Spacer(1, 3*mm))

    header = [
        Paragraph("POINT DE CONTR\u00d4LE",
                  ParagraphStyle("bph", fontName=F("F-Sans-Bold"), fontSize=7,
                                 textColor=C.HexColor("#666666"), leading=9)),
        Paragraph("AVANT INTERVENTION", s_bh_av),
        Paragraph("APR\u00c8S INTERVENTION", s_bh_ap),
    ]
    rows = [header]
    for key, label in bilan_rows:
        av = bilan.get(key,{}).get("avant","") or ""
        ap = bilan.get(key,{}).get("apres","") or ""
        rows.append([
            Paragraph(label,    s_bpt),
            Paragraph(av or "\u2014", s_bval if av else s_bem),
            Paragraph(ap or "\u2014", s_bval if ap else s_bem),
        ])

    tbl = Table(rows, colWidths=[W*0.3, W*0.35, W*0.35])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,-1),  C.HexColor("#f5f4f0")),
        ("BACKGROUND",    (1,0), (1,-1),  AMBER2),
        ("BACKGROUND",    (2,0), (2,-1),  VERT2),
        ("BACKGROUND",    (1,0), (1,0),   AMBERB),
        ("BACKGROUND",    (2,0), (2,0),   VERTB),
        ("LINEBELOW",     (0,0), (-1,-1), 0.5, BORDER),
        ("LINEBETWEEN",   (0,0), (-1,-1), 0.5, BORDER),
        ("BOX",           (0,0), (-1,-1), 0.5, BORDER),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    elements.append(tbl)

    obs = bilan.get("_observations","")
    if obs:
        elements.append(Spacer(1, 2*mm))
        obs_t = Table([[Paragraph(f'<b>Observations :</b> {obs}', s_obs)]], colWidths=[W])
        obs_t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), C.HexColor("#f5f5f5")),
            ("LEFTPADDING",   (0,0), (-1,-1), 10),
            ("RIGHTPADDING",  (0,0), (-1,-1), 10),
            ("TOPPADDING",    (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LINELEFT",      (0,0), (0,-1),  3, OR),
        ]))
        elements.append(obs_t)

    return elements
