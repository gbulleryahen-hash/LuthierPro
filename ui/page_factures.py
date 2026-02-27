"""ui/page_factures.py — Liste des factures"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QHeaderView,
    QComboBox, QMessageBox, QLabel, QWidget
)
from PySide6.QtCore import Qt
from ui.base_page import BasePage
from ui.page_devis import _open_pdf_preview
from core.i18n import t


def fmt(val):
    try: return f"{float(val):,.2f} €".replace(",","\u202f").replace(".",",")
    except: return "0,00 €"


class FacturesPage(BasePage):
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        header, _ = self.make_header(t("page.factures.h1"), t("page.factures.h2"), t("btn.new_facture"), self.open_new)
        layout.addWidget(header)

        toolbar = QHBoxLayout()
        self.search = self.make_search_bar("Rechercher une facture...")
        self.search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search)

        self.statut_filter = QComboBox(); self.statut_filter.setFixedWidth(160)
        self.statut_filter.addItem("Tous les statuts", "")
        for s in ["brouillon","envoyé","payé","en retard","annulé"]:
            self.statut_filter.addItem(s.capitalize(), s)
        self.statut_filter.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(self.statut_filter)
        toolbar.addStretch()

        self.count_lbl = QLabel("0 factures")
        self.count_lbl.setStyleSheet("color:#908870;font-size:9pt")
        toolbar.addWidget(self.count_lbl)
        layout.addLayout(toolbar)

        self.table = self.make_table(["Numéro", "Date", "Échéance", "Client", "Objet", "Total TTC", "Statut", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 100); self.table.setColumnWidth(1, 90); self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(5, 110); self.table.setColumnWidth(6, 110)
        self.table.doubleClicked.connect(lambda idx: self.open_edit(self.table.item(idx.row(), 0).data(Qt.UserRole)))
        layout.addWidget(self.table)

    def refresh(self):
        q = self.search.text() if hasattr(self,'search') else ""
        statut = self.statut_filter.currentData() if hasattr(self,'statut_filter') else ""
        docs = self.db.get_documents("facture", q, statut)
        self.count_lbl.setText(f"{len(docs)} facture{'s' if len(docs)>1 else ''}")
        self.table.setRowCount(len(docs))

        for i, d in enumerate(docs):
            client = " — ".join(filter(None,[d["client_societe"] or "",
                                             " ".join(filter(None,[d["client_prenom"] or "", d["client_nom"] or ""]))]))
            self.table.setItem(i, 0, self.cell(d["numero"]))
            self.table.item(i, 0).setData(Qt.UserRole, d["id"])
            self.table.setItem(i, 1, self.cell(d["date_doc"] or ""))
            self.table.setItem(i, 2, self.cell(d["date_echeance"] or "—"))
            self.table.setItem(i, 3, self.cell(client))
            self.table.setItem(i, 4, self.cell(d["objet"] or ""))
            self.table.setItem(i, 5, self.cell_mono(fmt(d["total_ttc"])))
            self.table.setItem(i, 6, self.cell(self.status_badge_text(d["statut"] or "")))

            btn_voir  = QPushButton("👁");  btn_voir.setObjectName("btn-flat"); btn_voir.setFixedSize(32,28)
            btn_edit  = QPushButton("✏️"); btn_edit.setObjectName("btn-flat"); btn_edit.setFixedSize(32,28)
            btn_email = QPushButton("📧"); btn_email.setObjectName("btn-flat"); btn_email.setFixedSize(32,28)
            btn_del   = QPushButton("🗑");  btn_del.setObjectName("btn-flat"); btn_del.setFixedSize(32,28)

            btn_voir.clicked.connect(lambda _, did=d["id"]: self._preview(did))
            btn_edit.clicked.connect(lambda _, did=d["id"]: self.open_edit(did))
            btn_email.clicked.connect(lambda _, did=d["id"]: self._email(did))
            btn_del.clicked.connect(lambda _, did=d["id"]: self._delete(did))

            w = QWidget(); h = QHBoxLayout(w); h.setContentsMargins(4,0,4,0); h.setSpacing(1)
            for b in [btn_voir, btn_edit, btn_email, btn_del]: h.addWidget(b)
            self.table.setCellWidget(i, 7, w)
        self.table.resizeRowsToContents()

    def open_new(self):
        from ui.dialog_document import DocumentDialog
        dlg = DocumentDialog(self.db, "facture", parent=self)
        if dlg.exec(): self.refresh()

    def open_edit(self, doc_id):
        from ui.dialog_document import DocumentDialog
        dlg = DocumentDialog(self.db, "facture", doc_id=doc_id, parent=self)
        if dlg.exec(): self.refresh()

    def _preview(self, doc_id):
        _open_pdf_preview(self.db, doc_id, parent=self)

    def _email(self, doc_id):
        from ui.dialog_email import EmailDialog
        dlg = EmailDialog(self.db, doc_id, parent=self)
        dlg.exec()

    def _delete(self, doc_id):
        if QMessageBox.question(self, "Supprimer", "Supprimer cette facture ?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.db.delete_document(doc_id)
            self.refresh()
