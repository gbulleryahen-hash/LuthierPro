"""ui/page_articles.py — Gestion articles/services"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QTextEdit, QDialogButtonBox,
    QMessageBox, QLabel, QComboBox, QDoubleSpinBox, QWidget
)
from PySide6.QtCore import Qt
from ui.base_page import BasePage
from core.i18n import t
from core.styles import TYPES_ARTICLE, UNITES, TVA_RATES


def fmt(val):
    try: return f"{float(val):,.2f} €".replace(",","\u202f").replace(".",",")
    except: return "0,00 €"


class ArticlesPage(BasePage):
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        header, _ = self.make_header(t("page.articles.h1"), t("page.articles.h2"), t("btn.new_article"), self.open_new)
        layout.addWidget(header)

        toolbar = QHBoxLayout()
        self.search = self.make_search_bar("Rechercher un article...")
        self.search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search)
        toolbar.addStretch()

        btn_import = QPushButton("📥 Importer CSV")
        btn_import.setFixedHeight(30)
        btn_import.clicked.connect(self._import_csv)
        btn_export = QPushButton("📤 Exporter CSV")
        btn_export.setFixedHeight(30)
        btn_export.clicked.connect(self._export_csv)
        btn_tmpl = QPushButton("📄 Modèle CSV")
        btn_tmpl.setFixedHeight(30)
        btn_tmpl.clicked.connect(self._download_template)

        toolbar.addWidget(btn_import)
        toolbar.addWidget(btn_export)
        toolbar.addWidget(btn_tmpl)

        self.count_lbl = QLabel("0 articles")
        self.count_lbl.setStyleSheet("color:#6a6050;font-size:9pt;margin-left:8px")
        toolbar.addWidget(self.count_lbl)
        layout.addLayout(toolbar)

        self.table = self.make_table(["Désignation", "Référence", "Type", "Prix HT", "TVA", "Unité", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.doubleClicked.connect(lambda idx: self.open_edit(self.table.item(idx.row(), 0).data(Qt.UserRole)))
        layout.addWidget(self.table)

    def refresh(self):
        q = self.search.text() if hasattr(self, 'search') else ""
        articles = self.db.get_articles(q)
        self.count_lbl.setText(f"{len(articles)} article{'s' if len(articles)>1 else ''}")
        self.table.setRowCount(len(articles))
        for i, a in enumerate(articles):
            self.table.setItem(i, 0, self.cell(a["nom"]))
            self.table.item(i, 0).setData(Qt.UserRole, a["id"])
            self.table.setItem(i, 1, self.cell(a["reference"] or "—"))
            self.table.setItem(i, 2, self.cell(a["type"] or "—"))
            self.table.setItem(i, 3, self.cell(fmt(a["prix_ht"]), Qt.AlignRight))
            self.table.setItem(i, 4, self.cell(f'{a["tva"]:g}%', Qt.AlignCenter))
            self.table.setItem(i, 5, self.cell(a["unite"] or "—"))

            btn_edit = QPushButton("✏️"); btn_edit.setObjectName("btn-flat"); btn_edit.setFixedSize(32,28)
            btn_edit.clicked.connect(lambda _, aid=a["id"]: self.open_edit(aid))
            btn_del = QPushButton("🗑"); btn_del.setObjectName("btn-flat"); btn_del.setFixedSize(32,28)
            btn_del.clicked.connect(lambda _, aid=a["id"]: self.delete(aid))
            w = QWidget(); h = QHBoxLayout(w); h.setContentsMargins(4,0,4,0); h.setSpacing(2)
            h.addWidget(btn_edit); h.addWidget(btn_del)
            self.table.setCellWidget(i, 6, w)
        self.table.resizeRowsToContents()

    def open_new(self):
        dlg = ArticleDialog(self.db, parent=self)
        if dlg.exec(): self.refresh()

    def open_edit(self, article_id):
        dlg = ArticleDialog(self.db, article_id=article_id, parent=self)
        if dlg.exec(): self.refresh()

    def delete(self, article_id):
        if QMessageBox.question(self, "Supprimer", "Supprimer cet article ?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.db.delete_article(article_id)
            self.refresh()

    def _export_csv(self):
        from PySide6.QtWidgets import QFileDialog
        from core.csv_io import export_articles_csv
        articles = self.db.get_articles()
        if not articles:
            QMessageBox.information(self, "Vide", "Aucun article à exporter.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Exporter les articles", "articles.csv", "CSV (*.csv)")
        if path:
            content = export_articles_csv(articles)
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                f.write(content)
            QMessageBox.information(self, "Exporté ✓", f"{len(articles)} articles exportés vers :\n{path}")

    def _import_csv(self):
        from PySide6.QtWidgets import QFileDialog
        from core.csv_io import import_articles_csv
        path, _ = QFileDialog.getOpenFileName(self, "Importer des articles", "", "CSV (*.csv *.txt)")
        if not path:
            return
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            content = f.read()
        nb, skipped, errors = import_articles_csv(content, self.db)
        self.refresh()
        msg = f"✅ {nb} article(s) importé(s)"
        if skipped: msg += f"\n⏭ {skipped} doublon(s) ignoré(s)"
        if errors:  msg += f"\n⚠️ {len(errors)} erreur(s) :\n" + "\n".join(errors[:5])
        QMessageBox.information(self, "Import terminé", msg)

    def _download_template(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "Sauvegarder le modèle", "modele_articles.csv", "CSV (*.csv)")
        if path:
            template = "Désignation;Référence;Type;Prix HT;TVA %;Unité;Description\n"
            template += "Réglage complet;REG-001;service;80;20;unité;Réglage action, intonation et truss rod\n"
            template += "Changement cordes;COR-001;service;15;20;unité;Pose de cordes fournies par le client\n"
            template += "Cordes D'Addario 10-46;COR-010;produit;12.50;20;jeu;Cordes électrique\n"
            template += "Frette EVO Gold;FRE-001;produit;2.50;20;unité;Frette en alliage EVO Gold\n"
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                f.write(template)
            QMessageBox.information(self, "Modèle créé ✓", f"Modèle CSV enregistré :\n{path}")


class ArticleDialog(QDialog):
    def __init__(self, db, article_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.article_id = article_id
        self.setWindowTitle("Modifier l'article" if article_id else "Nouvel article")
        self.setMinimumWidth(440)
        self._build()
        if article_id:
            self._load()

    def _build(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.nom = QLineEdit(); self.nom.setFixedHeight(32)
        self.ref = QLineEdit(); self.ref.setFixedHeight(32)
        self.type_cb = QComboBox(); self.type_cb.addItems(TYPES_ARTICLE)
        self.prix = QDoubleSpinBox(); self.prix.setMaximum(999999); self.prix.setDecimals(2); self.prix.setSuffix(" €")
        self.tva_cb = QComboBox()
        for r in TVA_RATES: self.tva_cb.addItem(f"{r:g}%", r)
        self.tva_cb.setCurrentIndex(3)  # 20%
        self.unite_cb = QComboBox(); self.unite_cb.addItems(UNITES)
        self.desc = QTextEdit(); self.desc.setFixedHeight(70); self.desc.setPlaceholderText("Description...")

        form.addRow("Désignation *", self.nom)
        form.addRow("Référence",     self.ref)
        form.addRow("Type",          self.type_cb)
        form.addRow("Prix HT",       self.prix)
        form.addRow("TVA",           self.tva_cb)
        form.addRow("Unité",         self.unite_cb)
        form.addRow("Description",   self.desc)
        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Enregistrer")
        btns.button(QDialogButtonBox.Ok).setObjectName("btn-primary")
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _load(self):
        a = self.db.get_article(self.article_id)
        if a:
            self.nom.setText(a["nom"] or "")
            self.ref.setText(a["reference"] or "")
            idx = self.type_cb.findText(a["type"] or "service")
            if idx >= 0: self.type_cb.setCurrentIndex(idx)
            self.prix.setValue(float(a["prix_ht"] or 0))
            for i in range(self.tva_cb.count()):
                if self.tva_cb.itemData(i) == float(a["tva"] or 20):
                    self.tva_cb.setCurrentIndex(i); break
            idx2 = self.unite_cb.findText(a["unite"] or "unité")
            if idx2 >= 0: self.unite_cb.setCurrentIndex(idx2)
            self.desc.setPlainText(a["description"] or "")

    def _save(self):
        if not self.nom.text().strip():
            QMessageBox.warning(self, "Champ requis", "La désignation est obligatoire.")
            return
        data = {
            "nom": self.nom.text().strip(),
            "reference": self.ref.text().strip(),
            "type": self.type_cb.currentText(),
            "prix_ht": self.prix.value(),
            "tva": self.tva_cb.currentData(),
            "unite": self.unite_cb.currentText(),
            "description": self.desc.toPlainText().strip(),
        }
        self.db.save_article(data, self.article_id)
        self.accept()
