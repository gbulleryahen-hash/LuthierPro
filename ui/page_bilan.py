"""ui/page_bilan.py — Bilan périodique des factures (par trimestre, période libre, etc.)"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QDateEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox, QGridLayout, QWidget, QSizePolicy,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from ui.base_page import BasePage
from core.i18n import t
from core.qt_fonts import mono as _mono, serif as _serif


def _fmt(val):
    try:
        return f"{float(val):,.2f} €".replace(",", "\u202f").replace(".", ",")
    except Exception:
        return "0,00 €"


def _fmt_date(d):
    if not d:
        return "—"
    try:
        p = d.split("-")
        return f"{p[2]}/{p[1]}/{p[0]}"
    except Exception:
        return d


class BilanPage(BasePage):
    def setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(16)

        # ── En-tête ──────────────────────────────────────────
        header, _ = self.make_header(t("page.bilan.h1"), t("page.bilan.h2"))
        outer.addWidget(header)

        # ── Barre de filtres ─────────────────────────────────
        filter_frame = QFrame()
        filter_frame.setObjectName("card")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(14)

        lbl_period = QLabel("Période :")
        lbl_period.setStyleSheet("color:#b0a888;font-size:9pt;")
        filter_layout.addWidget(lbl_period)

        self.period_cb = QComboBox()
        self.period_cb.setFixedWidth(200)
        self._populate_periods()
        self.period_cb.currentIndexChanged.connect(self._on_period_changed)
        filter_layout.addWidget(self.period_cb)

        sep = QFrame(); sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("background:#2a2820;max-width:1px;")
        filter_layout.addWidget(sep)

        lbl_from = QLabel("Du :")
        lbl_from.setStyleSheet("color:#b0a888;font-size:9pt;")
        filter_layout.addWidget(lbl_from)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_from.setFixedWidth(120)
        filter_layout.addWidget(self.date_from)

        lbl_to = QLabel("Au :")
        lbl_to.setStyleSheet("color:#b0a888;font-size:9pt;")
        filter_layout.addWidget(lbl_to)

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setFixedWidth(120)
        filter_layout.addWidget(self.date_to)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.VLine)
        sep2.setStyleSheet("background:#2a2820;max-width:1px;")
        filter_layout.addWidget(sep2)

        lbl_statut = QLabel("Statuts :")
        lbl_statut.setStyleSheet("color:#b0a888;font-size:9pt;")
        filter_layout.addWidget(lbl_statut)

        self.chk_paye   = QCheckBox("Payé");     self.chk_paye.setChecked(True)
        self.chk_envoye = QCheckBox("Envoyé");   self.chk_envoye.setChecked(True)
        self.chk_retard = QCheckBox("En retard");self.chk_retard.setChecked(True)
        filter_layout.addWidget(self.chk_paye)
        filter_layout.addWidget(self.chk_envoye)
        filter_layout.addWidget(self.chk_retard)

        filter_layout.addStretch()

        btn_calc = QPushButton("📊  Calculer")
        btn_calc.setObjectName("btn-primary")
        btn_calc.setFixedHeight(34)
        btn_calc.clicked.connect(self.compute)
        filter_layout.addWidget(btn_calc)

        outer.addWidget(filter_frame)

        # ── Zone scrollable de résultats ─────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content_widget = QWidget()
        self.results_layout = QVBoxLayout(content_widget)
        self.results_layout.setContentsMargins(0, 0, 0, 20)
        self.results_layout.setSpacing(16)
        scroll.setWidget(content_widget)
        outer.addWidget(scroll, 1)

        self.placeholder = QLabel("👆  Choisissez une période et cliquez sur Calculer")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("color:#706858;font-size:12pt;padding:60px;")
        self.results_layout.addWidget(self.placeholder)
        self.results_layout.addStretch()

        self._on_period_changed()

    def _populate_periods(self):
        from datetime import date
        today = date.today()
        year  = today.year
        q     = (today.month - 1) // 3 + 1

        self.period_cb.clear()
        items = [
            ("— Période libre —", None, None),
            (f"T{q} {year}  (en cours)",
             QDate(year, (q-1)*3+1, 1),
             QDate(year, min(q*3, 12), _last_day(year, min(q*3, 12)))),
        ]
        for prev_q in range(q-1, 0, -1):
            m_s, m_e = (prev_q-1)*3+1, prev_q*3
            items.append((f"T{prev_q} {year}", QDate(year, m_s, 1),
                          QDate(year, m_e, _last_day(year, m_e))))

        items.append((f"Année {year}",   QDate(year,   1, 1), QDate(year,   12, 31)))
        items.append((f"Année {year-1}", QDate(year-1, 1, 1), QDate(year-1, 12, 31)))

        for prev_q in range(4, 0, -1):
            m_s, m_e = (prev_q-1)*3+1, prev_q*3
            items.append((f"T{prev_q} {year-1}", QDate(year-1, m_s, 1),
                          QDate(year-1, m_e, _last_day(year-1, m_e))))

        for label, d_from, d_to in items:
            self.period_cb.addItem(label, (d_from, d_to))

    def _on_period_changed(self):
        data = self.period_cb.currentData()
        if data and data[0] is not None:
            self.date_from.setDate(data[0])
            self.date_to.setDate(data[1])
            self.date_from.setEnabled(False)
            self.date_to.setEnabled(False)
        else:
            self.date_from.setEnabled(True)
            self.date_to.setEnabled(True)

    def compute(self):
        statuts = []
        if self.chk_paye.isChecked():   statuts.append("payé")
        if self.chk_envoye.isChecked(): statuts.append("envoyé")
        if self.chk_retard.isChecked(): statuts.append("en retard")
        if not statuts:
            statuts = ["payé", "envoyé", "en retard"]

        d_from = self.date_from.date().toString("yyyy-MM-dd")
        d_to   = self.date_to.date().toString("yyyy-MM-dd")

        result = self.db.get_bilan_periode(d_from, d_to, statuts)
        self._render_results(result, d_from, d_to)

    def _render_results(self, result, d_from, d_to):
        # Vider
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        mf = _mono()
        sf = _serif()

        # ── Titre période ─────────────────────────────────────
        period_lbl = QLabel()
        period_lbl.setTextFormat(Qt.RichText)
        period_lbl.setText(
            f'<span style="font-family:\'{sf}\',Georgia,serif;font-size:15pt;font-weight:bold;">'
            f'<span style="color:#b0a888;">Résultats du </span>'
            f'<span style="color:#d4a853;">{_fmt_date(d_from)}</span>'
            f'<span style="color:#b0a888;"> au </span>'
            f'<span style="color:#d4a853;">{_fmt_date(d_to)}</span>'
            f'</span>'
        )
        self.results_layout.addWidget(period_lbl)

        if result["nb_factures"] == 0:
            empty = QLabel("Aucune facture trouvée pour cette période.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color:#706858;font-size:11pt;padding:40px;")
            self.results_layout.addWidget(empty)
            self.results_layout.addStretch()
            return

        # ── Cartes récap ──────────────────────────────────────
        def stat_card(title, value, color):
            card = QFrame(); card.setObjectName("card")
            card.setMinimumHeight(84)
            vl = QVBoxLayout(card)
            vl.setContentsMargins(18, 12, 18, 12); vl.setSpacing(4)
            t = QLabel(title)
            t.setStyleSheet("color:#908870;font-size:8pt;letter-spacing:1px;text-transform:uppercase;")
            v = QLabel(value)
            v.setFont(QFont(mf, 16, QFont.Bold))
            v.setStyleSheet(f"color:{color};")
            vl.addWidget(t); vl.addWidget(v)
            return card

        cards_row = QHBoxLayout(); cards_row.setSpacing(12)
        cards_row.addWidget(stat_card("Nb factures",  str(result["nb_factures"]), "#6090d4"))
        cards_row.addWidget(stat_card("Total HT",     _fmt(result["total_ht"]),   "#d4a853"))
        cards_row.addWidget(stat_card("TVA collectée",_fmt(result["total_tva"]),  "#d48653"))
        cards_row.addWidget(stat_card("Total TTC",    _fmt(result["total_ttc"]),  "#6bbf8e"))
        cw = QWidget(); cw.setLayout(cards_row)
        self.results_layout.addWidget(cw)

        # ── Ventilation services / produits / frais ───────────
        vent_frame = QFrame(); vent_frame.setObjectName("card-accent")
        vl = QVBoxLayout(vent_frame)
        vl.setContentsMargins(20, 16, 20, 16); vl.setSpacing(14)

        title_v = QLabel("VENTILATION PAR TYPE")
        title_v.setStyleSheet(
            "color:#d4a853;font-size:8pt;font-weight:bold;letter-spacing:2px;"
        )
        vl.addWidget(title_v)

        types_data = [
            ("🔧  Services",  result["total_services_ht"], "#6090d4"),
            ("📦  Produits",  result["total_produits_ht"], "#6bbf8e"),
            ("💸  Frais",     result["total_frais_ht"],   "#d48653"),
        ]
        total_ht = max(result["total_ht"], 0.01)

        for label, val, color in types_data:
            row_h = QHBoxLayout(); row_h.setSpacing(12)

            lbl_n = QLabel(label)
            lbl_n.setFixedWidth(110)
            lbl_n.setStyleSheet(f"color:{color};font-size:10pt;font-weight:bold;")

            # Barre de progression
            bar_bg = QFrame()
            bar_bg.setFixedHeight(10)
            bar_bg.setStyleSheet("background:#1a1814;border-radius:5px;")
            bar_fg = QFrame(bar_bg)
            bar_fg.setFixedHeight(10)
            bar_fg.setStyleSheet(f"background:{color};border-radius:5px;")
            pct = min(val / total_ht, 1.0)
            bar_fg.setFixedWidth(max(4, int(pct * 220)))

            lbl_v = QLabel(_fmt(val))
            lbl_v.setFixedWidth(110)
            lbl_v.setFont(QFont(mf, 10))
            lbl_v.setStyleSheet(f"color:{color};")
            lbl_v.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            pct_lbl = QLabel(f"{pct*100:.1f}%")
            pct_lbl.setFixedWidth(48)
            pct_lbl.setStyleSheet("color:#8a7c60;font-size:9pt;")
            pct_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            row_h.addWidget(lbl_n)
            row_h.addWidget(bar_bg, 1)
            row_h.addWidget(lbl_v)
            row_h.addWidget(pct_lbl)
            vl.addLayout(row_h)

        # Ligne totale
        sep_line = QFrame(); sep_line.setFrameShape(QFrame.HLine)
        sep_line.setStyleSheet("background:#3a3020;max-height:1px;")
        vl.addWidget(sep_line)
        tot_row = QHBoxLayout()
        lbl_tot = QLabel("TOTAL HT")
        lbl_tot.setStyleSheet("color:#b0a888;font-size:9pt;font-weight:bold;letter-spacing:1px;")
        lbl_ht = QLabel(_fmt(result["total_ht"]))
        lbl_ht.setFont(QFont(mf, 12, QFont.Bold))
        lbl_ht.setStyleSheet("color:#d4a853;")
        tot_row.addWidget(lbl_tot)
        tot_row.addStretch()
        tot_row.addWidget(lbl_ht)
        vl.addLayout(tot_row)

        self.results_layout.addWidget(vent_frame)

        # ── Récap déclaration TVA (micro-entrepreneur) ────────
        tva_frame = QFrame(); tva_frame.setObjectName("card")
        tl = QVBoxLayout(tva_frame)
        tl.setContentsMargins(20, 16, 20, 16); tl.setSpacing(10)

        tva_title = QLabel("📋  RÉCAPITULATIF DÉCLARATION")
        tva_title.setStyleSheet(
            "color:#b0a888;font-size:8pt;font-weight:bold;letter-spacing:2px;"
        )
        tl.addWidget(tva_title)

        # Grille déclaration
        decl_grid = QGridLayout(); decl_grid.setSpacing(6)
        decl_grid.setColumnMinimumWidth(1, 20)

        rows_decl = [
            ("CA total encaissé (TTC)",  result["total_ttc"], "#e8e0d0"),
            ("dont CA Services HT",      result["total_services_ht"], "#6090d4"),
            ("dont CA Produits HT",      result["total_produits_ht"], "#6bbf8e"),
            ("dont Frais HT",            result["total_frais_ht"],   "#d48653"),
            ("TVA collectée",            result["total_tva"], "#d46060"),
        ]

        for i, (label, val, color) in enumerate(rows_decl):
            # Séparateur avant TVA
            if i == len(rows_decl) - 1:
                sep = QFrame(); sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet("background:#2a2820;max-height:1px;margin:4px 0;")
                decl_grid.addWidget(sep, i*2, 0, 1, 3)

            lbl_d = QLabel(label)
            lbl_d.setStyleSheet(f"color:#b0a888;font-size:9pt;")
            val_lbl = QLabel(_fmt(val))
            val_lbl.setFont(QFont(mf, 10))
            val_lbl.setStyleSheet(f"color:{color};")
            val_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            decl_grid.addWidget(lbl_d,   i*2+1 if i == len(rows_decl)-1 else i, 0)
            decl_grid.addWidget(val_lbl, i*2+1 if i == len(rows_decl)-1 else i, 2)

        tl.addLayout(decl_grid)

        hint = QLabel(
            f"💡 Période : {result['nb_factures']} facture{'s' if result['nb_factures']>1 else ''} "
            f"— Retournez l'excédent de TVA collectée sur votre déclaration CA12/CA3."
        )
        hint.setStyleSheet("color:#706858;font-size:8pt;font-style:italic;")
        hint.setWordWrap(True)
        tl.addWidget(hint)

        self.results_layout.addWidget(tva_frame)

        # ── Top clients ───────────────────────────────────────
        if result["par_client"]:
            client_frame = QFrame(); client_frame.setObjectName("card")
            cl = QVBoxLayout(client_frame)
            cl.setContentsMargins(20, 14, 20, 14); cl.setSpacing(8)
            cl_title = QLabel("TOP CLIENTS")
            cl_title.setStyleSheet(
                "color:#908870;font-size:8pt;font-weight:bold;letter-spacing:2px;"
            )
            cl.addWidget(cl_title)
            for i, (client, total) in enumerate(result["par_client"][:5]):
                row_h = QHBoxLayout()
                rank  = QLabel(f"#{i+1}")
                rank.setStyleSheet("color:#706858;font-size:9pt;min-width:28px;")
                cname = QLabel(client)
                cname.setStyleSheet("color:#c8c0b0;font-size:10pt;")
                cval  = QLabel(_fmt(total))
                cval.setFont(QFont(mf, 10))
                cval.setStyleSheet("color:#d4a853;")
                row_h.addWidget(rank); row_h.addWidget(cname)
                row_h.addStretch(); row_h.addWidget(cval)
                cl.addLayout(row_h)
            self.results_layout.addWidget(client_frame)

        # ── Détail des factures ───────────────────────────────
        detail_lbl = QLabel("DÉTAIL DES FACTURES")
        detail_lbl.setStyleSheet(
            "color:#908870;font-size:8pt;font-weight:bold;letter-spacing:2px;margin-top:4px;"
        )
        self.results_layout.addWidget(detail_lbl)

        tbl = self.make_table(["Numéro", "Date", "Client", "Objet", "HT", "TTC", "Statut"])
        tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        tbl.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        tbl.setColumnWidth(0, 110)
        tbl.setColumnWidth(1, 90)
        tbl.setColumnWidth(4, 110)
        tbl.setColumnWidth(5, 110)
        tbl.setColumnWidth(6, 120)
        tbl.setRowCount(len(result["factures"]))

        STATUS_COLORS = {
            "payé":      "#6bbf8e",
            "envoyé":    "#6090d4",
            "en retard": "#d46060",
            "brouillon": "#908870",
            "annulé":    "#4a4035",
        }

        for ri, f in enumerate(result["factures"]):
            tbl.setItem(ri, 0, self.cell_mono(f.get("numero",""), Qt.AlignLeft))
            tbl.setItem(ri, 1, self.cell(_fmt_date(f.get("date_doc",""))))

            parts = []
            if f.get("client_societe"): parts.append(f["client_societe"])
            n = f'{f.get("client_prenom","") or ""} {f.get("client_nom","") or ""}'.strip()
            if n: parts.append(n)
            tbl.setItem(ri, 2, self.cell(" — ".join(parts) if parts else "—"))
            tbl.setItem(ri, 3, self.cell(f.get("objet","") or ""))
            tbl.setItem(ri, 4, self.cell_mono(_fmt(f.get("total_ht",0))))
            tbl.setItem(ri, 5, self.cell_mono(_fmt(f.get("total_ttc",0))))

            statut = f.get("statut","")
            icon = {"payé":"✅","envoyé":"🔵","en retard":"🔴","annulé":"⛔"}.get(statut,"⬜")
            si = QTableWidgetItem(f"{icon} {statut.capitalize()}")
            si.setForeground(QColor(STATUS_COLORS.get(statut, "#b0a888")))
            tbl.setItem(ri, 6, si)

        tbl.setFixedHeight(min(44 + len(result["factures"]) * 34, 420))
        self.results_layout.addWidget(tbl)
        self.results_layout.addStretch()

    def refresh(self):
        self._populate_periods()
        self._on_period_changed()


def _last_day(year, month):
    import calendar
    return calendar.monthrange(year, month)[1]
