"""ui/dialog_preview.py — Aperçu PDF et envoi"""
import os, sys, subprocess, tempfile
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QFrame, QWidget, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class PreviewDialog(QDialog):
    def __init__(self, db, doc_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.doc_id = doc_id
        self.pdf_path = None
        doc = db.get_document(doc_id)
        self.setWindowTitle(f"Aperçu — {doc['numero']}")
        self.setMinimumSize(700, 600)
        self.resize(800, 700)
        self._build(doc)

    def _build(self, doc):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        toolbar = QWidget()
        toolbar.setStyleSheet("background:#111009;border-bottom:1px solid #2a2820;")
        tb_layout = QHBoxLayout(toolbar); tb_layout.setContentsMargins(14,10,14,10)

        lbl = QLabel(f"{'Facture' if doc['type']=='facture' else 'Devis'} — {doc['numero']}")
        lbl.setStyleSheet("color:#d4a853;font-weight:bold;font-size:11pt;")
        tb_layout.addWidget(lbl); tb_layout.addStretch()

        btn_gen = QPushButton("⬇️  Générer PDF")
        btn_gen.setObjectName("btn-primary"); btn_gen.setFixedHeight(32)
        btn_gen.clicked.connect(self._generate_and_open)
        tb_layout.addWidget(btn_gen)

        btn_email = QPushButton("📧  Envoyer par email")
        btn_email.setFixedHeight(32)
        btn_email.clicked.connect(self._send_email)
        tb_layout.addWidget(btn_email)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("btn-flat"); btn_close.setFixedSize(32, 32)
        btn_close.clicked.connect(self.accept)
        tb_layout.addWidget(btn_close)
        layout.addWidget(toolbar)

        # Résumé du document
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        cl = QVBoxLayout(content); cl.setContentsMargins(30, 24, 30, 24); cl.setSpacing(12)

        # Info card
        card = QFrame(); card.setObjectName("card-accent")
        card_l = QVBoxLayout(card); card_l.setContentsMargins(16,14,16,14); card_l.setSpacing(6)

        lignes = self.db.get_document_lignes(doc_id)
        bilan  = self.db.get_bilan(doc_id)

        def fmt(v):
            try: return f"{float(v):,.2f} €".replace(",","\u202f").replace(".",",")
            except: return "0,00 €"

        client = " — ".join(filter(None,[doc["client_societe"] or "",
                                          " ".join(filter(None,[doc["client_prenom"] or "", doc["client_nom"] or ""]))]))
        rows = [
            ("Client", client or "—"),
            ("Date", doc["date_doc"] or "—"),
            ("Objet", doc["objet"] or "—"),
            ("Statut", doc["statut"] or "—"),
            ("Total HT", fmt(doc["total_ht"])),
            ("TVA", f'{doc["tva_rate"]:g}% — {fmt(doc["total_tva"])}'),
            ("TOTAL TTC", fmt(doc["total_ttc"])),
        ]
        if doc["guitare_marque"]:
            rows.insert(1, ("Instrument", f'🎸 {doc["guitare_marque"]} {doc["guitare_modele"]}'))
        if doc["devis_ref"]:
            rows.append(("Réf. devis", doc["devis_ref"]))

        for label, value in rows:
            row = QHBoxLayout()
            l1 = QLabel(label); l1.setFixedWidth(120)
            l1.setStyleSheet("color:#908870;font-size:9pt;font-weight:bold;")
            l2 = QLabel(value); l2.setStyleSheet("color:#e8e0d0;font-size:10pt;")
            l2.setWordWrap(True)
            row.addWidget(l1); row.addWidget(l2); row.addStretch()
            card_l.addLayout(row)

        cl.addWidget(card)

        # Lignes
        if lignes:
            lbl2 = QLabel("LIGNES")
            lbl2.setStyleSheet("color:#908870;font-size:8pt;font-weight:bold;letter-spacing:2px;margin-top:8px")
            cl.addWidget(lbl2)
            for l in lignes:
                total = float(l["quantite"] or 1) * float(l["prix_ht"] or 0)
                row = QHBoxLayout()
                desc = QLabel(l["designation"] or ""); desc.setStyleSheet("color:#e8e0d0;")
                amt = QLabel(fmt(total)); amt.setStyleSheet("color:#d4a853;font-family:'Courier New';")
                amt.setAlignment(Qt.AlignRight)
                row.addWidget(desc); row.addStretch(); row.addWidget(amt)
                cl.addLayout(row)

        # Bilan
        has_bilan = any(bilan.get(k,{}).get("avant","") or bilan.get(k,{}).get("apres","") for k in bilan if k != "_observations")
        if has_bilan:
            lbl3 = QLabel("BILAN TECHNIQUE")
            lbl3.setStyleSheet("color:#908870;font-size:8pt;font-weight:bold;letter-spacing:2px;margin-top:8px")
            cl.addWidget(lbl3)
            from core.styles import BILAN_FIELDS
            for key, label in BILAN_FIELDS:
                av = bilan.get(key,{}).get("avant","")
                ap = bilan.get(key,{}).get("apres","")
                if av or ap:
                    row = QHBoxLayout()
                    row.addWidget(QLabel(label + ":"))
                    row.addWidget(QLabel(f"Avant: {av or '—'}"))
                    row.addWidget(QLabel(f"→  Après: {ap or '—'}"))
                    row.addStretch()
                    cl.addLayout(row)

        cl.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _generate_and_open(self):
        from core.pdf_generator import generate_pdf
        doc      = self.db.get_document(self.doc_id)
        lignes   = self.db.get_document_lignes(self.doc_id)
        bilan    = self.db.get_bilan(self.doc_id)
        settings = self.db.get_all_settings()

        # Convertir en dict mutable et enrichir avec les données client/guitare
        doc_dict = dict(doc)
        if doc_dict.get("client_id"):
            c = self.db.get_client(doc_dict["client_id"])
            if c:
                for field in ["nom","prenom","societe","adresse","cp","ville","email","telephone"]:
                    doc_dict[f"client_{field}"] = c[field] or ""
        if doc_dict.get("guitare_id"):
            g = self.db.get_guitare(doc_dict["guitare_id"])
            if g:
                doc_dict["guitare_marque"] = g["marque"] or ""
                doc_dict["guitare_modele"] = g["modele"] or ""
                doc_dict["guitare_serie"]  = g["serie"]  or ""

        docs_dir = os.path.join(os.path.expanduser("~"), "LuthierPro", "PDF")
        os.makedirs(docs_dir, exist_ok=True)
        # Nettoyer le numéro pour le nom de fichier (évite les / dans FAC-0001)
        numero_safe = doc_dict["numero"].replace("/", "-").replace("\\", "-")
        pdf_path = os.path.join(docs_dir, f"{numero_safe}.pdf")

        try:
            path = generate_pdf(doc_dict, [dict(l) for l in lignes], bilan, settings, pdf_path)
            self.pdf_path = path
            self._open_file(path)
        except ImportError:
            QMessageBox.warning(self, "Module manquant",
                "ReportLab n'est pas installé.\n\nInstallez-le avec :\n  pip install reportlab")
        except Exception as e:
            QMessageBox.warning(self, "Erreur PDF", f"Impossible de générer le PDF :\n\n{str(e)}")

    def _send_email(self):
        from ui.dialog_email import EmailDialog
        dlg = EmailDialog(self.db, self.doc_id, parent=self)
        dlg.exec()

    def _open_file(self, path):
        try:
            if sys.platform == "win32": os.startfile(path)
            elif sys.platform == "darwin": subprocess.run(["open", path])
            else: subprocess.run(["xdg-open", path])
        except Exception: pass
