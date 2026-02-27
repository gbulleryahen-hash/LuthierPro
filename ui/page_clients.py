"""ui/page_clients.py — Gestion des clients"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QTextEdit, QDialogButtonBox,
    QMessageBox, QLabel
)
from PySide6.QtCore import Qt
from ui.base_page import BasePage
from core.i18n import t


def fmt(val):
    try: return f"{float(val):,.2f} €".replace(",","\u202f").replace(".",",")
    except: return "0,00 €"


class ClientsPage(BasePage):
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        header, _ = self.make_header(t("page.clients.h1"), t("page.clients.h2"), t("btn.new_client"), self.open_new)
        layout.addWidget(header)

        # Toolbar
        toolbar = QHBoxLayout()
        self.search = self.make_search_bar("Rechercher un client...")
        self.search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search)
        toolbar.addStretch()

        btn_import = QPushButton("📥 Importer CSV")
        btn_import.setFixedHeight(30)
        btn_import.clicked.connect(self._import_csv)
        btn_export = QPushButton("📤 Exporter CSV")
        btn_export.setFixedHeight(30)
        btn_export.clicked.connect(self._export_csv)
        toolbar.addWidget(btn_import)
        toolbar.addWidget(btn_export)

        self.count_lbl = QLabel("0 clients")
        self.count_lbl.setStyleSheet("color:#908870;font-size:9pt;margin-left:8px")
        toolbar.addWidget(self.count_lbl)
        layout.addLayout(toolbar)

        # Table
        self.table = self.make_table(["Nom / Société", "Email", "Téléphone", "Ville", "Total facturé", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 100)
        self.table.doubleClicked.connect(lambda idx: self.open_edit(self.table.item(idx.row(), 0).data(Qt.UserRole)))
        layout.addWidget(self.table)

    def refresh(self):
        q = self.search.text() if hasattr(self, 'search') else ""
        clients = self.db.get_clients(q)
        self.count_lbl.setText(f"{len(clients)} client{'s' if len(clients)>1 else ''}")
        self.table.setRowCount(len(clients))
        for i, c in enumerate(clients):
            name = " — ".join(filter(None, [c["societe"], " ".join(filter(None, [c["prenom"], c["nom"]]))]))
            total = self.db.get_client_total(c["id"])
            self.table.setItem(i, 0, self.cell(name or "—"))
            self.table.item(i, 0).setData(Qt.UserRole, c["id"])
            self.table.setItem(i, 1, self.cell(c["email"] or "—"))
            self.table.setItem(i, 2, self.cell(c["telephone"] or "—"))
            self.table.setItem(i, 3, self.cell(c["ville"] or "—"))
            self.table.setItem(i, 4, self.cell(fmt(total), Qt.AlignRight))

            # Boutons actions
            btn_edit = QPushButton("✏️")
            btn_edit.setObjectName("btn-flat")
            btn_edit.setFixedSize(32, 28)
            btn_edit.clicked.connect(lambda _, cid=c["id"]: self.open_edit(cid))

            btn_del = QPushButton("🗑")
            btn_del.setObjectName("btn-flat")
            btn_del.setFixedSize(32, 28)
            btn_del.clicked.connect(lambda _, cid=c["id"]: self.delete(cid))

            from PySide6.QtWidgets import QWidget
            w = QWidget()
            h = QHBoxLayout(w)
            h.setContentsMargins(4, 0, 4, 0)
            h.setSpacing(2)
            h.addWidget(btn_edit)
            h.addWidget(btn_del)
            self.table.setCellWidget(i, 5, w)
        self.table.resizeRowsToContents()

    def open_new(self):
        dlg = ClientDialog(self.db, parent=self)
        if dlg.exec():
            self.refresh()

    def open_edit(self, client_id):
        dlg = ClientDialog(self.db, client_id=client_id, parent=self)
        if dlg.exec():
            self.refresh()

    def delete(self, client_id):
        c = self.db.get_client(client_id)
        name = f"{c['prenom']} {c['nom']}".strip() or c['societe'] or "ce client"
        if QMessageBox.question(self, "Supprimer", f"Supprimer {name} ?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.db.delete_client(client_id)
            self.refresh()

    def _export_csv(self):
        from PySide6.QtWidgets import QFileDialog
        from core.csv_io import export_clients_csv
        clients = self.db.get_clients()
        if not clients:
            QMessageBox.information(self, "Vide", "Aucun client à exporter.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Exporter les clients", "clients.csv", "CSV (*.csv)")
        if path:
            content = export_clients_csv(clients)
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                f.write(content)
            QMessageBox.information(self, "Exporté ✓", f"{len(clients)} clients exportés vers :\n{path}")

    def _import_csv(self):
        from PySide6.QtWidgets import QFileDialog
        from core.csv_io import import_clients_csv
        path, _ = QFileDialog.getOpenFileName(self, "Importer des clients", "", "CSV (*.csv *.txt)")
        if not path:
            return
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            content = f.read()
        nb, skipped, errors = import_clients_csv(content, self.db)
        self.refresh()
        msg = f"✅ {nb} client(s) importé(s)"
        if skipped: msg += f"\n⏭ {skipped} doublon(s) ignoré(s) (même email)"
        if errors:  msg += f"\n⚠️ {len(errors)} erreur(s) :\n" + "\n".join(errors[:5])
        QMessageBox.information(self, "Import terminé", msg)


class ClientDialog(QDialog):
    def __init__(self, db, client_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.client_id = client_id
        self.setWindowTitle("Modifier le client" if client_id else "Nouveau client")
        self.setMinimumWidth(480)
        self._build()
        if client_id:
            self._load()

    def _build(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.fields = {}
        field_defs = [
            ("prenom",   "Prénom"),
            ("nom",      "Nom *"),
            ("societe",  "Société"),
            ("email",    "Email"),
            ("telephone","Téléphone"),
            ("adresse",  "Adresse"),
            ("cp",       "Code postal"),
            ("ville",    "Ville"),
            ("siret",    "SIRET"),
            ("tva_intra","N° TVA"),
        ]
        for key, label in field_defs:
            w = QLineEdit()
            w.setFixedHeight(32)
            form.addRow(label, w)
            self.fields[key] = w

        # Notes
        self.notes = QTextEdit()
        self.notes.setFixedHeight(70)
        self.notes.setPlaceholderText("Notes internes...")
        form.addRow("Notes", self.notes)

        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Enregistrer")
        btns.button(QDialogButtonBox.Ok).setObjectName("btn-primary")
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _load(self):
        c = self.db.get_client(self.client_id)
        if c:
            for key, widget in self.fields.items():
                widget.setText(str(c[key] or ""))
            self.notes.setPlainText(c["notes"] or "")

    def _save(self):
        data = {key: w.text().strip() for key, w in self.fields.items()}
        data["notes"] = self.notes.toPlainText().strip()
        if not data.get("nom") and not data.get("societe"):
            QMessageBox.warning(self, "Champ requis", "Renseignez au moins un nom ou une société.")
            return
        self.db.save_client(data, self.client_id)
        self.accept()
