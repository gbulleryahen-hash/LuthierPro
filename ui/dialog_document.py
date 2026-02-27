"""ui/dialog_document.py — Dialogue création/édition devis ou facture"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox,
    QSpinBox, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialogButtonBox, QMessageBox, QWidget, QScrollArea, QFrame,
    QSizePolicy, QTabWidget, QAbstractItemView, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from core.styles import STATUTS_DEVIS, STATUTS_FACTURE, TVA_RATES, BILAN_FIELDS, TYPES_ARTICLE
from core.i18n import t, bilan_fields_translated
from datetime import date as _date


def fmt(val):
    try: return f"{float(val):,.2f} €".replace(",","\u202f").replace(".",",")
    except: return "0,00 €"


class DocumentDialog(QDialog):
    def __init__(self, db, doc_type, doc_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.doc_type = doc_type
        self.doc_id = doc_id
        label = t("nav.devis") if doc_type == "devis" else t("nav.factures")
        self.setWindowTitle(
            (t("dlg.edit_devis") if doc_type == "devis" else t("dlg.edit_facture")) if doc_id
            else (t("dlg.new_devis") if doc_type == "devis" else t("dlg.new_facture"))
        )
        self.setMinimumSize(860, 700)
        self.resize(940, 780)
        self._build()
        if doc_id:
            self._load()
        else:
            self._set_defaults()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(24, 20, 24, 20)
        inner_layout.setSpacing(16)

        # ── SECTION 1 : Infos générales ──────────────────────
        grp1 = QGroupBox("Informations générales")
        f1 = QGridLayout(grp1); f1.setSpacing(10)

        self.client_cb = QComboBox(); self.client_cb.setMinimumWidth(220)
        self.client_cb.currentIndexChanged.connect(self._update_guitares)
        self.date_edit = QDateEdit(); self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.objet_edit = QLineEdit()
        self.objet_edit.setPlaceholderText("Ex: Réglage complet guitare électrique")
        self.echeance_edit = QDateEdit(); self.echeance_edit.setCalendarPopup(True)
        self.statut_cb = QComboBox()
        statuts = STATUTS_DEVIS if self.doc_type == "devis" else STATUTS_FACTURE
        self.statut_cb.addItems(statuts)
        self.guitare_cb = QComboBox()

        f1.addWidget(QLabel("Client *"), 0, 0); f1.addWidget(self.client_cb, 0, 1)
        f1.addWidget(QLabel("Date *"), 0, 2); f1.addWidget(self.date_edit, 0, 3)
        f1.addWidget(QLabel("Objet"), 1, 0); f1.addWidget(self.objet_edit, 1, 1, 1, 3)
        f1.addWidget(QLabel("Échéance"), 2, 0); f1.addWidget(self.echeance_edit, 2, 1)
        f1.addWidget(QLabel("Statut"), 2, 2); f1.addWidget(self.statut_cb, 2, 3)
        f1.addWidget(QLabel("Guitare associée"), 3, 0); f1.addWidget(self.guitare_cb, 3, 1, 1, 3)
        inner_layout.addWidget(grp1)

        self._load_clients()

        # ── SECTION 2 : Lignes ───────────────────────────────
        grp2 = QGroupBox("Lignes du document")
        g2l = QVBoxLayout(grp2); g2l.setSpacing(8)

        # Table avec 7 colonnes : Désignation | Type | Qté | PU HT | Total HT | ✕
        self.lignes_table = QTableWidget()
        self.lignes_table.setColumnCount(6)
        self.lignes_table.setHorizontalHeaderLabels(
            ["Désignation", "Type", "Qté", "PU HT (€)", "Total HT", ""]
        )
        self.lignes_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.lignes_table.setColumnWidth(1, 95)   # Type
        self.lignes_table.setColumnWidth(2, 60)   # Qté
        self.lignes_table.setColumnWidth(3, 110)  # PU HT
        self.lignes_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.lignes_table.setColumnWidth(5, 36)   # ✕
        self.lignes_table.verticalHeader().setVisible(False)
        self.lignes_table.setShowGrid(False)
        self.lignes_table.setAlternatingRowColors(True)
        self.lignes_table.setMinimumHeight(150)
        self.lignes_table.setMaximumHeight(300)
        g2l.addWidget(self.lignes_table)

        btn_row = QHBoxLayout()
        btn_add = QPushButton("+ Ajouter une ligne")
        btn_add.setFixedHeight(30)
        btn_add.clicked.connect(lambda: self._add_ligne())
        btn_catalog = QPushButton("📦  Catalogue")
        btn_catalog.setFixedHeight(30)
        btn_catalog.clicked.connect(self._open_catalog)
        btn_row.addWidget(btn_add); btn_row.addWidget(btn_catalog); btn_row.addStretch()
        g2l.addLayout(btn_row)

        # TVA
        tva_row = QHBoxLayout()
        tva_row.addStretch()
        tva_row.addWidget(QLabel("TVA globale :"))
        self.tva_cb = QComboBox(); self.tva_cb.setFixedWidth(90)
        for r in TVA_RATES: self.tva_cb.addItem(f"{r:g}%", r)
        self.tva_cb.setCurrentIndex(3)  # 20%
        self.tva_cb.currentIndexChanged.connect(self._recalc)
        tva_row.addWidget(self.tva_cb)
        g2l.addLayout(tva_row)

        totals_frame = QFrame(); totals_frame.setObjectName("card-accent")
        tl = QVBoxLayout(totals_frame); tl.setContentsMargins(14,10,14,10); tl.setSpacing(4)
        self.lbl_ht  = self._total_row(tl, "Sous-total HT", "0,00 €")
        self.lbl_tva = self._total_row(tl, "TVA (20%)", "0,00 €")
        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background:#3a3525;max-height:1px;border:none;")
        tl.addWidget(sep)
        self.lbl_ttc = self._total_row(tl, "TOTAL TTC", "0,00 €", bold=True, big=True)
        g2l.addWidget(totals_frame)
        inner_layout.addWidget(grp2)

        # ── SECTION 3 : Notes ────────────────────────────────
        grp3 = QGroupBox("Notes / Conditions")
        g3l = QVBoxLayout(grp3)
        self.notes_edit = QTextEdit(); self.notes_edit.setFixedHeight(70)
        self.notes_edit.setPlaceholderText("Conditions de règlement, remarques...")
        g3l.addWidget(self.notes_edit)
        inner_layout.addWidget(grp3)

        # ── SECTION 4 : Bilan technique — bouton-bascule visible ─

        # Bouton toggle doré bien visible
        self.btn_bilan_toggle = QPushButton(t("bilan.toggle_on"))
        self.btn_bilan_toggle.setFixedHeight(38)
        self.btn_bilan_toggle.setStyleSheet(
            "QPushButton { background:#252215; border:1px solid #d4a853;"
            "border-radius:6px; color:#d4a853; font-size:10pt; font-weight:bold;"
            "padding:0 16px; text-align:left; }"
            "QPushButton:hover { background:#2e2a18; border-color:#e0b860; color:#e0b860; }"
        )
        self.btn_bilan_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_bilan_toggle.clicked.connect(self._toggle_bilan)
        inner_layout.addWidget(self.btn_bilan_toggle)

        # Panneau bilan (masqué par défaut)
        self.bilan_panel = QFrame()
        self.bilan_panel.setObjectName("card-accent")
        self.bilan_panel.setVisible(False)
        bilan_panel_layout = QVBoxLayout(self.bilan_panel)
        bilan_panel_layout.setContentsMargins(16, 14, 16, 14)
        bilan_panel_layout.setSpacing(8)

        bilan_widget = QWidget()
        bilan_grid = QGridLayout(bilan_widget)
        bilan_grid.setSpacing(6)

        hdr_av = QLabel(t("bilan.before"))
        hdr_av.setAlignment(Qt.AlignCenter)
        hdr_av.setStyleSheet("color:#b8860b;font-size:8pt;font-weight:bold;letter-spacing:1px;"
                             "padding:6px;background:rgba(212,168,83,0.12);border-radius:4px;")
        hdr_ap = QLabel(t("bilan.after"))
        hdr_ap.setAlignment(Qt.AlignCenter)
        hdr_ap.setStyleSheet("color:#2e7d52;font-size:8pt;font-weight:bold;letter-spacing:1px;"
                             "padding:6px;background:rgba(107,191,142,0.12);border-radius:4px;")
        bilan_grid.addWidget(QLabel(""), 0, 0)
        bilan_grid.addWidget(hdr_av, 0, 1)
        bilan_grid.addWidget(hdr_ap, 0, 2)

        self.bilan_fields = {}
        for row_i, (key, label) in enumerate(bilan_fields_translated(), start=1):
            lbl = QLabel(label)
            lbl.setStyleSheet("color:#c0b090;font-size:9pt;font-weight:500;")
            lbl.setMinimumWidth(150)
            inp_av = QLineEdit(); inp_av.setFixedHeight(28); inp_av.setPlaceholderText("—")
            inp_ap = QLineEdit(); inp_ap.setFixedHeight(28); inp_ap.setPlaceholderText("—")
            bilan_grid.addWidget(lbl, row_i, 0)
            bilan_grid.addWidget(inp_av, row_i, 1)
            bilan_grid.addWidget(inp_ap, row_i, 2)
            self.bilan_fields[key] = (inp_av, inp_ap)

        row_obs = len(self.bilan_fields) + 1
        obs_lbl = QLabel(t("bilan.observations"))
        obs_lbl.setStyleSheet("color:#c0b090;font-size:9pt;")
        self.bilan_obs = QTextEdit(); self.bilan_obs.setFixedHeight(55)
        self.bilan_obs.setPlaceholderText(t("bilan.obs_ph"))
        bilan_grid.addWidget(obs_lbl, row_obs, 0)
        bilan_grid.addWidget(self.bilan_obs, row_obs, 1, 1, 2)

        bilan_grid.setColumnStretch(1, 1); bilan_grid.setColumnStretch(2, 1)
        bilan_panel_layout.addWidget(bilan_widget)
        inner_layout.addWidget(self.bilan_panel)

        # Alias pour compatibilité avec le reste du code (_load, _get_data)
        self.grp_bilan = self.bilan_panel
        self.grp_bilan.isChecked = lambda: self.bilan_panel.isVisible()
        self.grp_bilan.setChecked = self._set_bilan_checked

        scroll.setWidget(inner)
        layout.addWidget(scroll)

        # Footer
        footer = QWidget()
        footer.setStyleSheet("background:#1a1814;border-top:1px solid #2a2820;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 10, 16, 10)
        btn_cancel = QPushButton(t("btn.cancel")); btn_cancel.clicked.connect(self.reject)
        btn_preview = QPushButton(t("btn.preview"))
        btn_preview.clicked.connect(self._preview)
        btn_save = QPushButton(t("btn.save"))
        btn_save.setObjectName("btn-primary")
        btn_save.setFixedHeight(36)
        btn_save.clicked.connect(self._save)
        footer_layout.addStretch()
        footer_layout.addWidget(btn_cancel)
        footer_layout.addWidget(btn_preview)
        footer_layout.addWidget(btn_save)
        layout.addWidget(footer)

    def _total_row(self, parent_layout, label, value, bold=False, big=False):
        row = QHBoxLayout()
        lbl = QLabel(label)
        if bold: lbl.setStyleSheet("font-weight:bold;")
        val = QLabel(value)
        try:
            from core.qt_fonts import mono as _mono
            mf = _mono()
        except Exception:
            mf = "Courier New"
        if big:
            val.setStyleSheet(f"color:#d4a853;font-size:13pt;font-weight:bold;font-family:'{mf}';")
        else:
            val.setStyleSheet(f"color:#c0b090;font-family:'{mf}';")
        row.addWidget(lbl); row.addStretch(); row.addWidget(val)
        parent_layout.addLayout(row)
        return val

    def _toggle_bilan(self):
        """Bascule la visibilité du panneau bilan technique."""
        visible = not self.bilan_panel.isVisible()
        self.bilan_panel.setVisible(visible)
        self.btn_bilan_toggle.setText(
            t("bilan.toggle_off") if visible else t("bilan.toggle_on")
        )
        if visible:
            self.btn_bilan_toggle.setStyleSheet(
                "QPushButton { background:#1e3d2a; border:1px solid #2e6b4a;"
                "border-radius:6px; color:#6bbf8e; font-size:10pt; font-weight:bold;"
                "padding:0 16px; text-align:left; }"
                "QPushButton:hover { background:#253f2d; border-color:#6bbf8e; }"
            )
        else:
            self.btn_bilan_toggle.setStyleSheet(
                "QPushButton { background:#252215; border:1px solid #d4a853;"
                "border-radius:6px; color:#d4a853; font-size:10pt; font-weight:bold;"
                "padding:0 16px; text-align:left; }"
                "QPushButton:hover { background:#2e2a18; border-color:#e0b860; color:#e0b860; }"
            )

    def _set_bilan_checked(self, checked: bool):
        """Appelé depuis _load() pour afficher le bilan si des données existent."""
        self.bilan_panel.setVisible(checked)
        if checked:
            self.btn_bilan_toggle.setText(t("bilan.toggle_off"))
            self.btn_bilan_toggle.setStyleSheet(
                "QPushButton { background:#1e3d2a; border:1px solid #2e6b4a;"
                "border-radius:6px; color:#6bbf8e; font-size:10pt; font-weight:bold;"
                "padding:0 16px; text-align:left; }"
                "QPushButton:hover { background:#253f2d; border-color:#6bbf8e; }"
            )
        else:
            self.btn_bilan_toggle.setText(t("bilan.toggle_on"))
            self.btn_bilan_toggle.setStyleSheet(
                "QPushButton { background:#252215; border:1px solid #d4a853;"
                "border-radius:6px; color:#d4a853; font-size:10pt; font-weight:bold;"
                "padding:0 16px; text-align:left; }"
                "QPushButton:hover { background:#2e2a18; border-color:#e0b860; color:#e0b860; }"
            )

    def _load_clients(self):
        self.client_cb.clear()
        self.client_cb.addItem("— Sélectionner un client —", None)
        for c in self.db.get_clients():
            name = " — ".join(filter(None,[c["societe"], " ".join(filter(None,[c["prenom"],c["nom"]]))]))
            self.client_cb.addItem(name, c["id"])

    def _update_guitares(self):
        client_id = self.client_cb.currentData()
        self.guitare_cb.clear()
        self.guitare_cb.addItem("— Aucune guitare —", None)
        guitares = self.db.get_guitares(client_id=client_id) if client_id else self.db.get_guitares()
        for g in guitares:
            label = f'{g["marque"]} {g["modele"]}'
            if g["serie"]: label += f' (N°{g["serie"]})'
            self.guitare_cb.addItem(label, g["id"])

    def _add_ligne(self, designation="", qte=1, prix=0.0, type_article="service"):
        row = self.lignes_table.rowCount()
        self.lignes_table.insertRow(row)

        desc_edit = QLineEdit(designation); desc_edit.setFixedHeight(26)
        desc_edit.textChanged.connect(self._recalc)

        # Colonne Type
        type_cb = QComboBox(); type_cb.setFixedHeight(26)
        for t in TYPES_ARTICLE:
            type_cb.addItem(t, t)
        idx = type_cb.findData(type_article)
        if idx >= 0: type_cb.setCurrentIndex(idx)
        # Couleur selon type
        type_cb.currentIndexChanged.connect(lambda: self._color_type_cb(type_cb))
        self._color_type_cb(type_cb)

        qte_spin = QDoubleSpinBox(); qte_spin.setValue(qte)
        qte_spin.setMinimum(0); qte_spin.setMaximum(9999)
        qte_spin.setDecimals(2); qte_spin.setFixedHeight(26); qte_spin.setFixedWidth(58)
        qte_spin.valueChanged.connect(self._recalc)

        prix_spin = QDoubleSpinBox(); prix_spin.setValue(prix)
        prix_spin.setMinimum(0); prix_spin.setMaximum(9999999)
        prix_spin.setDecimals(2); prix_spin.setSuffix(" €")
        prix_spin.setFixedHeight(26); prix_spin.setFixedWidth(108)
        prix_spin.valueChanged.connect(self._recalc)

        try:
            from core.qt_fonts import mono as _mono
            mf = _mono()
        except Exception:
            mf = "Courier New"
        total_lbl = QLabel("0,00 €"); total_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_lbl.setStyleSheet(f"color:#c0b090;font-family:'{mf}';padding-right:6px;")

        btn_del = QPushButton("✕"); btn_del.setObjectName("btn-flat"); btn_del.setFixedSize(28, 26)
        btn_del.clicked.connect(lambda: (
            self.lignes_table.removeRow(self.lignes_table.indexAt(btn_del.pos()).row()),
            self._recalc()
        ))

        self.lignes_table.setCellWidget(row, 0, desc_edit)
        self.lignes_table.setCellWidget(row, 1, type_cb)
        self.lignes_table.setCellWidget(row, 2, qte_spin)
        self.lignes_table.setCellWidget(row, 3, prix_spin)
        self.lignes_table.setCellWidget(row, 4, total_lbl)
        self.lignes_table.setCellWidget(row, 5, btn_del)
        self.lignes_table.setRowHeight(row, 32)
        self._recalc()

    def _color_type_cb(self, cb):
        t = cb.currentData()
        if t == "service":
            cb.setStyleSheet("color:#6090d4;font-size:8pt;")
        elif t == "produit":
            cb.setStyleSheet("color:#6bbf8e;font-size:8pt;")
        else:
            cb.setStyleSheet("color:#d4a853;font-size:8pt;")

    def _open_catalog(self):
        from ui.dialog_catalog import CatalogDialog
        dlg = CatalogDialog(self.db, parent=self)
        if dlg.exec():
            article = dlg.selected_article
            if article:
                # Récupère le type depuis l'article du catalogue
                type_art = article.get("type", "service") or "service"
                self._add_ligne(article["nom"], 1, float(article["prix_ht"] or 0), type_art)
                tva_val = float(article["tva"] or 20)
                for i in range(self.tva_cb.count()):
                    if self.tva_cb.itemData(i) == tva_val:
                        self.tva_cb.setCurrentIndex(i); break

    def _recalc(self):
        total_ht = 0
        for row in range(self.lignes_table.rowCount()):
            qte_w   = self.lignes_table.cellWidget(row, 2)
            prix_w  = self.lignes_table.cellWidget(row, 3)
            total_w = self.lignes_table.cellWidget(row, 4)
            if qte_w and prix_w and total_w:
                line_total = qte_w.value() * prix_w.value()
                total_ht += line_total
                total_w.setText(fmt(line_total))
        tva_rate = self.tva_cb.currentData() or 0
        tva = total_ht * tva_rate / 100
        ttc = total_ht + tva
        self.lbl_ht.setText(fmt(total_ht))
        self.lbl_tva.setText(fmt(tva))
        self.lbl_tva.parent().layout().itemAt(1).layout().itemAt(0).widget().setText(f"TVA ({tva_rate:g}%)")
        self.lbl_ttc.setText(fmt(ttc))

    def _set_defaults(self):
        self._update_guitares()
        tva_default = float(self.db.get_setting("tva_defaut", "20") or 20)
        for i in range(self.tva_cb.count()):
            if self.tva_cb.itemData(i) == tva_default:
                self.tva_cb.setCurrentIndex(i); break
        self._add_ligne()

    def _load(self):
        doc = self.db.get_document(self.doc_id)
        if not doc: return

        for i in range(self.client_cb.count()):
            if self.client_cb.itemData(i) == doc["client_id"]:
                self.client_cb.setCurrentIndex(i); break

        self._update_guitares()
        for i in range(self.guitare_cb.count()):
            if self.guitare_cb.itemData(i) == doc["guitare_id"]:
                self.guitare_cb.setCurrentIndex(i); break

        if doc["date_doc"]:
            self.date_edit.setDate(QDate.fromString(doc["date_doc"], "yyyy-MM-dd"))
        if doc["date_echeance"]:
            self.echeance_edit.setDate(QDate.fromString(doc["date_echeance"], "yyyy-MM-dd"))

        self.objet_edit.setText(doc["objet"] or "")
        idx = self.statut_cb.findText(doc["statut"] or "brouillon")
        if idx >= 0: self.statut_cb.setCurrentIndex(idx)
        self.notes_edit.setPlainText(doc["notes"] or "")

        raw_tva = doc["tva_rate"]
        tva_val = float(raw_tva) if raw_tva is not None else 20.0
        matched = False
        for i in range(self.tva_cb.count()):
            if self.tva_cb.itemData(i) == tva_val:
                self.tva_cb.setCurrentIndex(i); matched = True; break
        if not matched:
            for i in range(self.tva_cb.count()):
                if self.tva_cb.itemData(i) == 20.0:
                    self.tva_cb.setCurrentIndex(i); break

        lignes = self.db.get_document_lignes(self.doc_id)
        for l in lignes:
            l = dict(l)  # sqlite3.Row → dict pour pouvoir appeler .get()
            type_art = l.get("type_article", "service") or "service"
            self._add_ligne(l.get("designation") or "", float(l.get("quantite") or 1),
                            float(l.get("prix_ht") or 0), type_art)

        bilan = self.db.get_bilan(self.doc_id)
        has_bilan = any(bilan.get(k,{}).get("avant","") or bilan.get(k,{}).get("apres","") for k,_ in BILAN_FIELDS)
        if has_bilan or bilan.get("_observations"):
            self.grp_bilan.setChecked(True)
        for key, (inp_av, inp_ap) in self.bilan_fields.items():
            inp_av.setText(bilan.get(key,{}).get("avant",""))
            inp_ap.setText(bilan.get(key,{}).get("apres",""))
        self.bilan_obs.setPlainText(bilan.get("_observations",""))

        self._recalc()

    def _get_data(self):
        total_ht = sum(
            self.lignes_table.cellWidget(r,2).value() * self.lignes_table.cellWidget(r,3).value()
            for r in range(self.lignes_table.rowCount())
            if self.lignes_table.cellWidget(r,2) and self.lignes_table.cellWidget(r,3)
        )
        tva_rate = self.tva_cb.currentData() or 0
        tva = total_ht * tva_rate / 100
        numero = self.db.next_numero(self.doc_type) if not self.doc_id else \
                 self.db.get_document(self.doc_id)["numero"]

        data = {
            "type": self.doc_type,
            "numero": numero,
            "client_id": self.client_cb.currentData(),
            "guitare_id": self.guitare_cb.currentData(),
            "date_doc": self.date_edit.date().toString("yyyy-MM-dd"),
            "date_echeance": self.echeance_edit.date().toString("yyyy-MM-dd"),
            "objet": self.objet_edit.text().strip(),
            "statut": self.statut_cb.currentText(),
            "tva_rate": tva_rate,
            "total_ht": total_ht,
            "total_tva": tva,
            "total_ttc": total_ht + tva,
            "notes": self.notes_edit.toPlainText().strip(),
            "devis_ref": self.db.get_document(self.doc_id)["devis_ref"] if self.doc_id else None,
        }

        lignes = []
        for r in range(self.lignes_table.rowCount()):
            dw = self.lignes_table.cellWidget(r, 0)
            tw = self.lignes_table.cellWidget(r, 1)
            qw = self.lignes_table.cellWidget(r, 2)
            pw = self.lignes_table.cellWidget(r, 3)
            if dw and tw and qw and pw:
                lignes.append({
                    "designation": dw.text(),
                    "type_article": tw.currentData() or "service",
                    "quantite": qw.value(),
                    "prix_ht": pw.value(),
                })

        bilan = {}
        if self.grp_bilan.isChecked():
            for key, (inp_av, inp_ap) in self.bilan_fields.items():
                bilan[key] = {"avant": inp_av.text().strip(), "apres": inp_ap.text().strip()}
            bilan["_observations"] = self.bilan_obs.toPlainText().strip()

        return data, lignes, bilan

    def _save(self):
        data, lignes, bilan = self._get_data()
        if not data["client_id"]:
            QMessageBox.warning(self, "Client requis", "Veuillez sélectionner un client.")
            return
        self.doc_id = self.db.save_document(data, lignes, bilan, self.doc_id)
        self.accept()

    def _preview(self):
        data, lignes, bilan = self._get_data()
        if not data["client_id"]:
            QMessageBox.warning(self, "Client requis", "Sélectionnez un client avant l'aperçu.")
            return
        if data.get("client_id"):
            c = self.db.get_client(data["client_id"])
            if c:
                for field in ["nom","prenom","societe","adresse","cp","ville","email","telephone"]:
                    data[f"client_{field}"] = c[field] or ""
        if data.get("guitare_id"):
            g = self.db.get_guitare(data["guitare_id"])
            if g:
                data["guitare_marque"] = g["marque"] or ""
                data["guitare_modele"] = g["modele"] or ""
                data["guitare_serie"]  = g["serie"]  or ""

        from core.pdf_generator import generate_pdf
        import os, subprocess, sys as _sys
        settings = self.db.get_all_settings()
        docs_dir = os.path.join(os.path.expanduser("~"), "LuthierPro", "PDF")
        os.makedirs(docs_dir, exist_ok=True)
        numero_safe = data["numero"].replace("/","-")
        pdf_path = os.path.join(docs_dir, f"apercu-{numero_safe}.pdf")
        try:
            path = generate_pdf(data, lignes, bilan, settings, pdf_path)
            if _sys.platform == "win32":    os.startfile(path)
            elif _sys.platform == "darwin": subprocess.run(["open", path])
            else:                           subprocess.run(["xdg-open", path])
        except ImportError:
            QMessageBox.warning(self, "Module manquant",
                "ReportLab n'est pas installé.\n\nInstallez-le avec :\n  pip install reportlab")
        except Exception as e:
            QMessageBox.warning(self, "Erreur PDF", f"Impossible de générer le PDF :\n\n{str(e)}")

    def get_doc_id(self):
        return self.doc_id
