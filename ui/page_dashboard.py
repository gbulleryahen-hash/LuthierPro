"""ui/page_dashboard.py — Tableau de bord"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QPushButton, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.base_page import BasePage
from core.i18n import t


def fmt(val):
    try:
        return f"{float(val):,.2f} €".replace(",", "\u202f").replace(".", ",")
    except Exception:
        return "0,00 €"


class DashboardPage(BasePage):
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        btn_devis = QPushButton(t("btn.new_devis"))
        btn_devis.setFixedHeight(36)
        btn_devis.clicked.connect(lambda: (
            self.main_window.navigate("devis"),
            self.main_window.pages["devis"].open_new()
        ))
        btn_facture = QPushButton(t("btn.new_facture"))
        btn_facture.setObjectName("btn-primary")
        btn_facture.setFixedHeight(36)
        btn_facture.clicked.connect(lambda: (
            self.main_window.navigate("factures"),
            self.main_window.pages["factures"].open_new()
        ))

        header, _ = self.make_header(t("page.dashboard.h1"), t("page.dashboard.h2"),
                                     extra_widgets=[btn_devis, btn_facture])
        layout.addWidget(header)

        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(14)
        self.card_ca,     self.lbl_ca     = self.make_stat_card(t("dash.ca_month"),       "0,00 €", "accent")
        self.card_enc,    self.lbl_enc    = self.make_stat_card(t("dash.invoices_unpaid"), "0,00 €", "green")
        self.card_retard, self.lbl_retard = self.make_stat_card(t("dash.quotes_pending"),  "0,00 €", "red")
        self.card_devis,  self.lbl_devis  = self.make_stat_card(t("dash.active_clients"),  "0",      "accent")
        self.stats_grid.addWidget(self.card_ca,     0, 0)
        self.stats_grid.addWidget(self.card_enc,    0, 1)
        self.stats_grid.addWidget(self.card_retard, 0, 2)
        self.stats_grid.addWidget(self.card_devis,  0, 3)
        layout.addLayout(self.stats_grid)

        lbl_recent = QLabel(t("dash.recent"))
        lbl_recent.setStyleSheet("color:#908870;font-size:8pt;font-weight:bold;letter-spacing:2px;margin-top:4px;")
        layout.addWidget(lbl_recent)

        self.recent_table = self.make_table([
            t("doc.numero"), t("doc.type") if False else "Type",
            t("doc.client"), t("doc.object"),
            t("doc.amount"), t("doc.status"), t("doc.date")
        ])
        self.recent_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.recent_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.recent_table.setMaximumHeight(300)
        layout.addWidget(self.recent_table)
        layout.addStretch()

    def refresh(self):
        stats = self.db.get_dashboard_stats()
        self.lbl_ca.setText(fmt(stats["ca_mois"]))
        self.lbl_enc.setText(fmt(stats["a_encaisser"]))
        self.lbl_retard.setText(fmt(stats["en_retard"]))
        self.lbl_devis.setText(str(stats["devis_en_cours"]))

        docs = stats["derniers_docs"]
        self.recent_table.setRowCount(len(docs))
        type_labels = {"devis": t("nav.devis"), "facture": t("nav.factures").rstrip("s")}
        for i, d in enumerate(docs):
            parts = []
            if d["client_societe"]: parts.append(d["client_societe"])
            n = " ".join(filter(None, [
                d["client_prenom"] if "client_prenom" in d.keys() else "",
                d["client_nom"]    if "client_nom"    in d.keys() else ""
            ]))
            if n: parts.append(n)
            self.recent_table.setItem(i, 0, self.cell(d["numero"]))
            self.recent_table.setItem(i, 1, self.cell(type_labels.get(d["type"], d["type"])))
            self.recent_table.setItem(i, 2, self.cell(" — ".join(parts)))
            self.recent_table.setItem(i, 3, self.cell(d["objet"]))
            self.recent_table.setItem(i, 4, self.cell_mono(fmt(d["total_ttc"]), Qt.AlignRight))
            self.recent_table.setItem(i, 5, self.cell(self.status_badge_text(d["statut"])))
            self.recent_table.setItem(i, 6, self.cell(d["date_doc"]))
        self.recent_table.resizeColumnsToContents()
