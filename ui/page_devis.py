"""ui/page_devis.py — Liste des devis"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QHeaderView,
    QComboBox, QMessageBox, QLabel, QWidget
)
from PySide6.QtCore import Qt
from ui.base_page import BasePage
from core.i18n import t


def fmt(val):
    try: return f"{float(val):,.2f} €".replace(",","\u202f").replace(".",",")
    except: return "0,00 €"


def _open_pdf_preview(db, doc_id, parent=None):
    """Génère le PDF et l'ouvre directement. Affiche une erreur si ReportLab manque."""
    import os, sys, subprocess
    from core.pdf_generator import generate_pdf
    from PySide6.QtWidgets import QMessageBox

    doc      = db.get_document(doc_id)
    lignes   = db.get_document_lignes(doc_id)
    bilan    = db.get_bilan(doc_id)
    settings = db.get_all_settings()

    # Enrichir avec les données client et guitare
    doc_dict = dict(doc)
    if doc_dict.get("client_id"):
        c = db.get_client(doc_dict["client_id"])
        if c:
            for field in ["nom","prenom","societe","adresse","cp","ville","email","telephone"]:
                doc_dict[f"client_{field}"] = c[field] or ""
    if doc_dict.get("guitare_id"):
        g = db.get_guitare(doc_dict["guitare_id"])
        if g:
            doc_dict["guitare_marque"] = g["marque"] or ""
            doc_dict["guitare_modele"] = g["modele"] or ""
            doc_dict["guitare_serie"]  = g["serie"]  or ""

    docs_dir = os.path.join(os.path.expanduser("~"), "LuthierPro", "PDF")
    os.makedirs(docs_dir, exist_ok=True)
    numero_safe = doc_dict["numero"].replace("/","-").replace("\\","-")
    pdf_path = os.path.join(docs_dir, f"{numero_safe}.pdf")

    try:
        path = generate_pdf(doc_dict, [dict(l) for l in lignes], bilan, settings, pdf_path)
        if sys.platform == "win32":    os.startfile(path)
        elif sys.platform == "darwin": subprocess.run(["open", path])
        else:                          subprocess.run(["xdg-open", path])
    except ImportError:
        QMessageBox.warning(parent, "Module manquant",
            "ReportLab n'est pas installé.\n\nLancez dans un terminal :\n  pip install reportlab")
    except Exception as e:
        QMessageBox.warning(parent, "Erreur PDF",
            f"Impossible de générer le PDF :\n\n{str(e)}")


class DevisPage(BasePage):
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        header, _ = self.make_header(t("page.devis.h1"), t("page.devis.h2"), t("btn.new_devis"), self.open_new)
        layout.addWidget(header)

        toolbar = QHBoxLayout()
        self.search = self.make_search_bar("Rechercher un devis...")
        self.search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search)

        self.statut_filter = QComboBox(); self.statut_filter.setFixedWidth(160)
        self.statut_filter.addItem("Tous les statuts", "")
        for s in ["brouillon","envoyé","accepté","refusé"]:
            self.statut_filter.addItem(s.capitalize(), s)
        self.statut_filter.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(self.statut_filter)
        toolbar.addStretch()

        self.count_lbl = QLabel("0 devis")
        self.count_lbl.setStyleSheet("color:#6a6050;font-size:9pt")
        toolbar.addWidget(self.count_lbl)
        layout.addLayout(toolbar)

        self.table = self.make_table(["Numéro", "Date", "Client", "Objet", "Total HT", "Statut", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 100); self.table.setColumnWidth(1, 90)
        self.table.setColumnWidth(4, 110); self.table.setColumnWidth(5, 110)
        self.table.doubleClicked.connect(lambda idx: self.open_edit(self.table.item(idx.row(), 0).data(Qt.UserRole)))
        layout.addWidget(self.table)

    def refresh(self):
        q = self.search.text() if hasattr(self,'search') else ""
        statut = self.statut_filter.currentData() if hasattr(self,'statut_filter') else ""
        docs = self.db.get_documents("devis", q, statut)
        self.count_lbl.setText(f"{len(docs)} devis")
        self.table.setRowCount(len(docs))

        for i, d in enumerate(docs):
            client = " — ".join(filter(None,[d["client_societe"] or "",
                                             " ".join(filter(None,[d["client_prenom"] or "", d["client_nom"] or ""]))]))
            self.table.setItem(i, 0, self.cell(d["numero"]))
            self.table.item(i, 0).setData(Qt.UserRole, d["id"])
            self.table.setItem(i, 1, self.cell(d["date_doc"] or ""))
            self.table.setItem(i, 2, self.cell(client))
            self.table.setItem(i, 3, self.cell(d["objet"] or ""))
            self.table.setItem(i, 4, self.cell_mono(fmt(d["total_ht"])))
            self.table.setItem(i, 5, self.cell(self.status_badge_text(d["statut"] or "")))

            btn_voir   = QPushButton("👁");   btn_voir.setObjectName("btn-flat"); btn_voir.setFixedSize(32,28)
            btn_edit   = QPushButton("✏️");   btn_edit.setObjectName("btn-flat"); btn_edit.setFixedSize(32,28)
            btn_conv   = QPushButton("🧾");   btn_conv.setObjectName("btn-flat"); btn_conv.setFixedSize(32,28)
            btn_conv.setToolTip("Convertir en facture")
            btn_email  = QPushButton("📧");   btn_email.setObjectName("btn-flat"); btn_email.setFixedSize(32,28)
            btn_del    = QPushButton("🗑");   btn_del.setObjectName("btn-flat"); btn_del.setFixedSize(32,28)

            btn_voir.clicked.connect(lambda _, did=d["id"]: self._preview(did))
            btn_edit.clicked.connect(lambda _, did=d["id"]: self.open_edit(did))
            btn_conv.clicked.connect(lambda _, did=d["id"]: self._convert(did))
            btn_email.clicked.connect(lambda _, did=d["id"]: self._email(did))
            btn_del.clicked.connect(lambda _, did=d["id"]: self._delete(did))

            w = QWidget(); h = QHBoxLayout(w); h.setContentsMargins(4,0,4,0); h.setSpacing(1)
            for b in [btn_voir, btn_edit, btn_conv, btn_email, btn_del]: h.addWidget(b)
            self.table.setCellWidget(i, 6, w)
        self.table.resizeRowsToContents()

    def open_new(self):
        from ui.dialog_document import DocumentDialog
        dlg = DocumentDialog(self.db, "devis", parent=self)
        if dlg.exec(): self.refresh()

    def open_edit(self, doc_id):
        from ui.dialog_document import DocumentDialog
        dlg = DocumentDialog(self.db, "devis", doc_id=doc_id, parent=self)
        if dlg.exec(): self.refresh()

    def _preview(self, doc_id):
        _open_pdf_preview(self.db, doc_id, parent=self)
        self.refresh()

    def _convert(self, doc_id):
        doc = self.db.get_document(doc_id)
        if QMessageBox.question(self, "Convertir", f"Convertir le devis {doc['numero']} en facture ?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            new_id = self.db.convert_devis_to_facture(doc_id)
            self.refresh()
            QMessageBox.information(self, "Facture créée",
                f"Facture créée avec succès !\nLe devis {doc['numero']} est maintenant marqué 'accepté'.")
            self.main_window.navigate("factures")

    def _email(self, doc_id):
        from ui.dialog_email import EmailDialog
        dlg = EmailDialog(self.db, doc_id, parent=self)
        dlg.exec()

    def _delete(self, doc_id):
        if QMessageBox.question(self, "Supprimer", "Supprimer ce devis ?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.db.delete_document(doc_id)
            self.refresh()
