"""ui/page_guitares.py — Gestion guitares + fiche historique"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QTextEdit, QDialogButtonBox,
    QMessageBox, QLabel, QComboBox, QDoubleSpinBox, QWidget,
    QTabWidget, QScrollArea, QFrame, QGridLayout, QSplitter
)
from PySide6.QtCore import Qt
from ui.base_page import BasePage
from core.i18n import t
from core.styles import TYPES_GUITARE, BILAN_FIELDS


def fmt(val):
    try: return f"{float(val):,.2f} €".replace(",","\u202f").replace(".",",")
    except: return "0,00 €"


class GuitaresPage(BasePage):
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        header, _ = self.make_header(t("page.guitares.h1"), t("page.guitares.h2"), t("btn.new_guitare"), self.open_new)
        layout.addWidget(header)

        toolbar = QHBoxLayout()
        self.search = self.make_search_bar("Rechercher une guitare...")
        self.search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search)

        self.client_filter = QComboBox()
        self.client_filter.setFixedWidth(200)
        self.client_filter.addItem("Tous les clients", None)
        self.client_filter.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(self.client_filter)
        toolbar.addStretch()

        self.count_lbl = QLabel("0 guitares")
        self.count_lbl.setStyleSheet("color:#6a6050;font-size:9pt")
        toolbar.addWidget(self.count_lbl)
        layout.addLayout(toolbar)

        self.table = self.make_table(["Marque / Modèle", "Type", "N° Série", "Propriétaire", "Année", "Couleur", "Interv.", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setColumnWidth(6, 70)
        self.table.doubleClicked.connect(lambda idx: self.open_fiche(self.table.item(idx.row(), 0).data(Qt.UserRole)))
        layout.addWidget(self.table)

    def refresh(self):
        # Refresh client filter
        clients = self.db.get_clients()
        current_client = self.client_filter.currentData()
        self.client_filter.blockSignals(True)
        self.client_filter.clear()
        self.client_filter.addItem("Tous les clients", None)
        for c in clients:
            name = " — ".join(filter(None, [c["societe"], " ".join(filter(None,[c["prenom"],c["nom"]]))]))
            self.client_filter.addItem(name, c["id"])
        # Restore selection
        for i in range(self.client_filter.count()):
            if self.client_filter.itemData(i) == current_client:
                self.client_filter.setCurrentIndex(i); break
        self.client_filter.blockSignals(False)

        q = self.search.text() if hasattr(self, 'search') else ""
        client_id = self.client_filter.currentData()
        guitares = self.db.get_guitares(q, client_id)
        self.count_lbl.setText(f"{len(guitares)} guitare{'s' if len(guitares)>1 else ''}")
        self.table.setRowCount(len(guitares))

        for i, g in enumerate(guitares):
            client_name = " — ".join(filter(None,[g["client_societe"],
                                                   " ".join(filter(None,[g["client_prenom"] or "", g["client_nom"] or ""]))]))
            interventions = self.db.get_guitare_interventions(g["id"])
            nb = len(interventions)

            self.table.setItem(i, 0, self.cell(f'{g["marque"]} {g["modele"]}'))
            self.table.item(i, 0).setData(Qt.UserRole, g["id"])
            self.table.setItem(i, 1, self.cell(g["type"] or "—"))
            self.table.setItem(i, 2, self.cell(g["serie"] or "—"))
            self.table.setItem(i, 3, self.cell(client_name or "—"))
            self.table.setItem(i, 4, self.cell(g["annee"] or "—"))
            self.table.setItem(i, 5, self.cell(g["couleur"] or "—"))
            self.table.setItem(i, 6, self.cell(f"{'🔧' if nb>0 else ''} {nb}" if nb else "—", Qt.AlignCenter))

            btn_fiche = QPushButton("📋 Fiche")
            btn_fiche.setObjectName("btn-flat")
            btn_fiche.setFixedHeight(28)
            btn_fiche.clicked.connect(lambda _, gid=g["id"]: self.open_fiche(gid))

            btn_edit = QPushButton("✏️")
            btn_edit.setObjectName("btn-flat")
            btn_edit.setFixedSize(32, 28)
            btn_edit.clicked.connect(lambda _, gid=g["id"]: self.open_edit(gid))

            btn_del = QPushButton("🗑")
            btn_del.setObjectName("btn-flat")
            btn_del.setFixedSize(32, 28)
            btn_del.clicked.connect(lambda _, gid=g["id"]: self.delete(gid))

            w = QWidget(); h = QHBoxLayout(w)
            h.setContentsMargins(4,0,4,0); h.setSpacing(2)
            h.addWidget(btn_fiche); h.addWidget(btn_edit); h.addWidget(btn_del)
            self.table.setCellWidget(i, 7, w)
        self.table.resizeRowsToContents()

    def open_new(self):
        dlg = GuitareDialog(self.db, parent=self)
        if dlg.exec(): self.refresh()

    def open_edit(self, guitare_id):
        dlg = GuitareDialog(self.db, guitare_id=guitare_id, parent=self)
        if dlg.exec(): self.refresh()

    def open_fiche(self, guitare_id):
        if not guitare_id: return
        dlg = GuitareFicheDialog(self.db, guitare_id, self.main_window, parent=self)
        dlg.exec()
        self.refresh()

    def delete(self, guitare_id):
        if QMessageBox.question(self, "Supprimer", "Supprimer cette guitare ?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.db.delete_guitare(guitare_id)
            self.refresh()


class GuitareDialog(QDialog):
    def __init__(self, db, guitare_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.guitare_id = guitare_id
        self.setWindowTitle("Modifier la guitare" if guitare_id else "Nouvelle guitare")
        self.setMinimumWidth(460)
        self._build()
        if guitare_id:
            self._load()

    def _build(self):
        layout = QVBoxLayout(self)
        form = QFormLayout(); form.setSpacing(10); form.setLabelAlignment(Qt.AlignRight)

        self.marque  = QLineEdit(); self.marque.setFixedHeight(32); self.marque.setPlaceholderText("Gibson, Fender, Martin...")
        self.modele  = QLineEdit(); self.modele.setFixedHeight(32); self.modele.setPlaceholderText("Les Paul, Stratocaster...")
        self.type_cb = QComboBox(); self.type_cb.addItems(TYPES_GUITARE)
        self.serie   = QLineEdit(); self.serie.setFixedHeight(32)
        self.annee   = QLineEdit(); self.annee.setFixedHeight(32); self.annee.setPlaceholderText("1975")
        self.couleur = QLineEdit(); self.couleur.setFixedHeight(32); self.couleur.setPlaceholderText("Sunburst, Natural...")

        self.client_cb = QComboBox()
        self.client_cb.addItem("— Aucun client —", None)
        for c in self.db.get_clients():
            name = " — ".join(filter(None,[c["societe"], " ".join(filter(None,[c["prenom"],c["nom"]]))]))
            self.client_cb.addItem(name, c["id"])

        self.valeur = QDoubleSpinBox(); self.valeur.setMaximum(9999999); self.valeur.setDecimals(2); self.valeur.setSuffix(" €")
        self.notes  = QTextEdit(); self.notes.setFixedHeight(80); self.notes.setPlaceholderText("Historique, observations...")

        form.addRow("Marque *",      self.marque)
        form.addRow("Modèle *",      self.modele)
        form.addRow("Type",          self.type_cb)
        form.addRow("N° de série",   self.serie)
        form.addRow("Année",         self.annee)
        form.addRow("Couleur",       self.couleur)
        form.addRow("Propriétaire",  self.client_cb)
        form.addRow("Valeur estimée",self.valeur)
        form.addRow("Notes",         self.notes)
        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Enregistrer")
        btns.button(QDialogButtonBox.Ok).setObjectName("btn-primary")
        btns.accepted.connect(self._save); btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _load(self):
        g = self.db.get_guitare(self.guitare_id)
        if g:
            self.marque.setText(g["marque"] or ""); self.modele.setText(g["modele"] or "")
            idx = self.type_cb.findText(g["type"] or "électrique")
            if idx >= 0: self.type_cb.setCurrentIndex(idx)
            self.serie.setText(g["serie"] or ""); self.annee.setText(g["annee"] or "")
            self.couleur.setText(g["couleur"] or "")
            for i in range(self.client_cb.count()):
                if self.client_cb.itemData(i) == g["client_id"]:
                    self.client_cb.setCurrentIndex(i); break
            self.valeur.setValue(float(g["valeur"] or 0))
            self.notes.setPlainText(g["notes"] or "")

    def _save(self):
        if not self.marque.text().strip() or not self.modele.text().strip():
            QMessageBox.warning(self, "Requis", "Marque et modèle sont obligatoires.")
            return
        data = {
            "marque": self.marque.text().strip(), "modele": self.modele.text().strip(),
            "type": self.type_cb.currentText(), "serie": self.serie.text().strip(),
            "annee": self.annee.text().strip(), "couleur": self.couleur.text().strip(),
            "client_id": self.client_cb.currentData(), "valeur": self.valeur.value(),
            "notes": self.notes.toPlainText().strip(),
        }
        self.db.save_guitare(data, self.guitare_id)
        self.accept()


class GuitareFicheDialog(QDialog):
    def __init__(self, db, guitare_id, main_window, parent=None):
        super().__init__(parent)
        self.db = db
        self.guitare_id = guitare_id
        self.main_window = main_window
        g = db.get_guitare(guitare_id)
        self.setWindowTitle(f"Fiche guitare — {g['marque']} {g['modele']}")
        self.setMinimumSize(860, 600)
        self.resize(960, 680)
        self._build(g)

    def _build(self, g):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QFrame()
        header.setStyleSheet("background:#111009;border-bottom:1px solid #2a2820;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 14, 20, 14)

        title = QLabel(f"🎸  {g['marque']} {g['modele']}")
        title.setStyleSheet("color:#d4a853;font-size:14pt;font-weight:bold;")
        sub_parts = [g["type"] or "", g["annee"] or "", f'N°{g["serie"]}' if g["serie"] else ""]
        sub = QLabel(" · ".join(filter(None, sub_parts)))
        sub.setStyleSheet("color:#6a6050;font-size:9pt;margin-top:2px")

        info_col = QVBoxLayout()
        info_col.addWidget(title); info_col.addWidget(sub)
        h_layout.addLayout(info_col)
        h_layout.addStretch()

        btn_edit = QPushButton("✏️  Modifier")
        btn_edit.setFixedHeight(32)
        btn_edit.clicked.connect(self._edit)
        h_layout.addWidget(btn_edit)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("btn-flat")
        close_btn.setFixedSize(32, 32)
        close_btn.clicked.connect(self.accept)
        h_layout.addWidget(close_btn)
        layout.addWidget(header)

        # Info cards
        interventions = self.db.get_guitare_interventions(self.guitare_id)
        client_name = " — ".join(filter(None,[g["client_societe"] or "",
                                              " ".join(filter(None,[g["client_prenom"] or "", g["client_nom"] or ""]))]))
        total_facture = sum(float(d["total_ttc"] or 0) for d in interventions if d["type"]=="facture" and d["statut"]=="payé")

        cards_row = QHBoxLayout()
        cards_row.setContentsMargins(20, 14, 20, 0)
        cards_row.setSpacing(10)
        infos = [
            ("Type", g["type"] or "—"),
            ("Propriétaire", client_name or "—"),
            ("N° de série", g["serie"] or "—"),
            ("Interventions", str(len(interventions))),
            ("CA total (payé)", fmt(total_facture)),
            ("Valeur estimée", fmt(g["valeur"]) if g["valeur"] else "—"),
        ]
        for label, value in infos:
            card = QFrame()
            card.setObjectName("card")
            card.setMinimumWidth(120)
            cl = QVBoxLayout(card); cl.setContentsMargins(12,10,12,10); cl.setSpacing(3)
            cl.addWidget(QLabel(label) if False else self._mini_label(label))
            vl = QLabel(value)
            vl.setStyleSheet("color:#e8e0d0;font-size:11pt;font-weight:bold;")
            vl.setWordWrap(True)
            cl.addWidget(vl)
            cards_row.addWidget(card)
        layout.addLayout(cards_row)

        # Tabs
        tabs = QTabWidget()
        tabs.setContentsMargins(0, 0, 0, 0)

        # Tab historique
        tab_hist = QWidget()
        th_layout = QVBoxLayout(tab_hist)
        th_layout.setContentsMargins(16, 16, 16, 16)
        th_layout.setSpacing(10)

        if not interventions:
            empty = QLabel("Aucune intervention enregistrée.\nAssociez cette guitare à un devis ou une facture.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color:#6a6050;font-size:10pt;padding:40px")
            th_layout.addWidget(empty)
        else:
            for d in interventions:
                self._add_intervention_card(th_layout, d)
        th_layout.addStretch()

        scroll1 = QScrollArea(); scroll1.setWidget(tab_hist)
        scroll1.setWidgetResizable(True); scroll1.setFrameShape(QFrame.NoFrame)
        tabs.addTab(scroll1, "📋  Historique")

        # Tab bilans
        tab_bilan = QWidget()
        tb_layout = QVBoxLayout(tab_bilan)
        tb_layout.setContentsMargins(16, 16, 16, 16)
        tb_layout.setSpacing(16)

        bilans_docs = [d for d in interventions if self._has_bilan(d["id"])]
        if not bilans_docs:
            empty2 = QLabel("Aucun bilan technique enregistré.")
            empty2.setAlignment(Qt.AlignCenter)
            empty2.setStyleSheet("color:#6a6050;font-size:10pt;padding:40px")
            tb_layout.addWidget(empty2)
        else:
            for d in bilans_docs:
                self._add_bilan_card(tb_layout, d)
        tb_layout.addStretch()

        scroll2 = QScrollArea(); scroll2.setWidget(tab_bilan)
        scroll2.setWidgetResizable(True); scroll2.setFrameShape(QFrame.NoFrame)
        tabs.addTab(scroll2, "🔧  Bilans techniques")

        # Tab notes
        tab_notes = QWidget()
        tn_layout = QVBoxLayout(tab_notes)
        tn_layout.setContentsMargins(16, 16, 16, 16)
        tn_layout.setSpacing(10)
        tn_layout.addWidget(QLabel("Notes internes sur cet instrument :"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlainText(self.db.get_guitare(self.guitare_id)["notes"] or "")
        self.notes_edit.setMinimumHeight(150)
        tn_layout.addWidget(self.notes_edit)
        btn_save_notes = QPushButton("💾  Sauvegarder")
        btn_save_notes.setObjectName("btn-primary")
        btn_save_notes.setFixedWidth(160)
        btn_save_notes.clicked.connect(self._save_notes)
        tn_layout.addWidget(btn_save_notes)
        tn_layout.addStretch()
        tabs.addTab(tab_notes, "📝  Notes")

        layout.addWidget(tabs)

    def _mini_label(self, text):
        l = QLabel(text)
        l.setStyleSheet("color:#6a6050;font-size:8pt;font-weight:bold;letter-spacing:1px;")
        return l

    def _add_intervention_card(self, layout, d):
        card = QFrame(); card.setObjectName("card")
        c_layout = QVBoxLayout(card); c_layout.setContentsMargins(14,12,14,12); c_layout.setSpacing(6)

        row1 = QHBoxLayout()
        is_facture = d["type"] == "facture"
        icon = "🧾" if is_facture else "📋"
        numero_lbl = QLabel(f'{icon}  <b style="color:#d4a853">{d["numero"]}</b>')
        numero_lbl.setTextFormat(Qt.RichText)

        statut_color = {"payé":"#6bbf8e","accepté":"#6bbf8e","envoyé":"#6090d4","refusé":"#d46060","en retard":"#d46060"}.get(d["statut"],"#8a8070")
        statut_lbl = QLabel(d["statut"].capitalize())
        statut_lbl.setStyleSheet(f"color:{statut_color};font-size:8pt;padding:2px 8px;border:1px solid {statut_color};border-radius:8px;")

        date_lbl = QLabel(d["date_doc"] or "")
        date_lbl.setStyleSheet("color:#6a6050;font-size:9pt;")

        amount_color = "#6bbf8e" if is_facture else "#e8e0d0"
        amount_val = d["total_ttc"] if is_facture else d["total_ht"]
        amount_lbl = QLabel(fmt(amount_val))
        amount_lbl.setStyleSheet(f"color:{amount_color};font-weight:bold;font-size:11pt;")

        row1.addWidget(numero_lbl); row1.addWidget(statut_lbl); row1.addWidget(date_lbl)
        row1.addStretch(); row1.addWidget(amount_lbl)
        c_layout.addLayout(row1)

        objet_lbl = QLabel(d["objet"] or "—")
        objet_lbl.setStyleSheet("color:#e8e0d0;font-size:10pt;")
        c_layout.addWidget(objet_lbl)

        # Lignes résumées
        lignes = self.db.get_document_lignes(d["id"])
        if lignes:
            items_text = " · ".join([l["designation"] for l in lignes[:3] if l["designation"]])
            if len(lignes) > 3: items_text += " …"
            items_lbl = QLabel(items_text)
            items_lbl.setStyleSheet("color:#6a6050;font-size:9pt;")
            c_layout.addWidget(items_lbl)

        row2 = QHBoxLayout()
        btn_voir = QPushButton("👁  Voir le document")
        btn_voir.setFixedHeight(28)
        btn_voir.clicked.connect(lambda _, did=d["id"], dtype=d["type"]: self._open_doc(did, dtype))
        row2.addWidget(btn_voir); row2.addStretch()
        c_layout.addLayout(row2)

        layout.addWidget(card)

    def _add_bilan_card(self, layout, d):
        bilan = self.db.get_bilan(d["id"])
        card = QFrame(); card.setObjectName("card")
        c_layout = QVBoxLayout(card); c_layout.setContentsMargins(14,12,14,12); c_layout.setSpacing(8)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel(f'<b style="color:#d4a853">{d["numero"]}</b> — {d["date_doc"] or ""}' +
                              (f' — {d["objet"]}' if d["objet"] else "")))
        hdr.addStretch()
        btn_voir = QPushButton("👁  Voir")
        btn_voir.setFixedHeight(26)
        btn_voir.clicked.connect(lambda _, did=d["id"], dtype=d["type"]: self._open_doc(did, dtype))
        hdr.addWidget(btn_voir)
        lbl_hdr = QLabel()
        lbl_hdr.setTextFormat(Qt.RichText)
        lbl_hdr.setText(f'<b style="color:#d4a853">{d["numero"]}</b>  {d["date_doc"] or ""}')
        c_layout.addLayout(hdr)

        # Tableau bilan
        from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
        tbl = QTableWidget()
        tbl.setColumnCount(3)
        tbl.setHorizontalHeaderLabels(["Point de contrôle", "AVANT", "APRÈS"])
        tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.verticalHeader().setVisible(False)
        tbl.setAlternatingRowColors(True)
        tbl.setShowGrid(False)

        rows_data = [(key, label) for key, label in BILAN_FIELDS
                     if bilan.get(key,{}).get("avant","") or bilan.get(key,{}).get("apres","")]
        tbl.setRowCount(len(rows_data))
        for i, (key, label) in enumerate(rows_data):
            av = bilan.get(key,{}).get("avant","") or "—"
            ap = bilan.get(key,{}).get("apres","") or "—"
            tbl.setItem(i, 0, QTableWidgetItem(label))
            tbl.setItem(i, 1, QTableWidgetItem(av))
            item_ap = QTableWidgetItem(ap)
            item_ap.setForeground(Qt.green if ap != "—" else Qt.gray)
            tbl.setItem(i, 2, item_ap)
        tbl.setMaximumHeight(min(len(rows_data) * 34 + 36, 280))
        c_layout.addWidget(tbl)

        obs = bilan.get("_observations","")
        if obs:
            obs_lbl = QLabel(f"Observations : {obs}")
            obs_lbl.setStyleSheet("color:#a09070;font-size:9pt;padding:6px;background:#252215;border-radius:4px;border-left:3px solid #d4a853;")
            obs_lbl.setWordWrap(True)
            c_layout.addWidget(obs_lbl)

        layout.addWidget(card)

    def _has_bilan(self, doc_id):
        bilan = self.db.get_bilan(doc_id)
        for key, _ in BILAN_FIELDS:
            if bilan.get(key,{}).get("avant","") or bilan.get(key,{}).get("apres",""):
                return True
        return bool(bilan.get("_observations",""))

    def _open_doc(self, doc_id, doc_type):
        self.accept()
        page = "devis" if doc_type == "devis" else "factures"
        self.main_window.navigate(page)
        self.main_window.pages[page].open_edit(doc_id)

    def _edit(self):
        dlg = GuitareDialog(self.db, guitare_id=self.guitare_id, parent=self)
        dlg.exec()

    def _save_notes(self):
        g_data = dict(self.db.get_guitare(self.guitare_id))
        data = {
            "marque": g_data["marque"], "modele": g_data["modele"], "type": g_data["type"],
            "serie": g_data["serie"], "annee": g_data["annee"], "couleur": g_data["couleur"],
            "client_id": g_data["client_id"], "valeur": g_data["valeur"],
            "notes": self.notes_edit.toPlainText().strip(),
        }
        self.db.save_guitare(data, self.guitare_id)
        QMessageBox.information(self, "Sauvegardé", "Notes sauvegardées ✓")
