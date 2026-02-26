"""ui/dialog_catalog.py — Sélecteur d'articles du catalogue"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QListWidget, QListWidgetItem, QLabel, QPushButton, QDialogButtonBox
)
from PySide6.QtCore import Qt


class CatalogDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.selected_article = None
        self.setWindowTitle("Choisir dans le catalogue")
        self.setMinimumSize(460, 420)
        self._build()
        self._load()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher un article...")
        self.search.setFixedHeight(34)
        self.search.textChanged.connect(self._load)
        layout.addWidget(self.search)

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.doubleClicked.connect(self._select)
        layout.addWidget(self.list_widget)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Choisir")
        btns.button(QDialogButtonBox.Ok).setObjectName("btn-primary")
        btns.accepted.connect(self._select)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _load(self):
        q = self.search.text()
        articles = self.db.get_articles(q)
        self.list_widget.clear()
        for a in articles:
            label = f"{a['nom']}"
            if a["reference"]: label += f"  [{a['reference']}]"
            price = f"{float(a['prix_ht']):,.2f}".replace(",","\u202f").replace(".",",")
            label += f"  —  {price} € HT / {a['unite']}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, dict(a))
            self.list_widget.addItem(item)

    def _select(self):
        current = self.list_widget.currentItem()
        if current:
            self.selected_article = current.data(Qt.UserRole)
            self.accept()
