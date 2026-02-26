"""ui/base_page.py — Classe de base pour toutes les pages"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QSizePolicy, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor


def _serif_family():
    try:
        from core.qt_fonts import serif
        return serif()
    except Exception:
        return "Georgia"


def _mono_family():
    try:
        from core.qt_fonts import mono
        return mono()
    except Exception:
        return "Courier New"


class BasePage(QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        pass

    def refresh(self):
        pass

    def make_header(self, title_first: str, title_second: str = None,
                    btn_label: str = None, btn_callback=None,
                    extra_widgets: list = None):
        """
        En-tête de page avec titre bicolore en Playfair Display.
          title_first  : mot(s) en blanc   (ex: "Mes")
          title_second : mot(s) en doré    (ex: "Devis")
          Si title_second est None, tout title_first est en doré.
        """
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 20)
        row.setSpacing(12)

        sf = _serif_family()

        if title_second:
            lbl = QLabel()
            lbl.setObjectName("page-title")
            lbl.setTextFormat(Qt.RichText)
            lbl.setText(
                f'<span style="font-family:\'{sf}\',Georgia,serif;'
                f'font-size:22pt;font-weight:bold;letter-spacing:-0.5px;">'
                f'<span style="color:#d8d0c0;">{title_first}&nbsp;</span>'
                f'<span style="color:#d4a853;">{title_second}</span>'
                f'</span>'
            )
        else:
            lbl = QLabel()
            lbl.setObjectName("page-title")
            lbl.setTextFormat(Qt.RichText)
            lbl.setText(
                f'<span style="font-family:\'{sf}\',Georgia,serif;'
                f'font-size:22pt;font-weight:bold;color:#d4a853;">'
                f'{title_first}</span>'
            )

        row.addWidget(lbl)
        row.addStretch()

        if extra_widgets:
            for w in extra_widgets:
                row.addWidget(w)

        btn = None
        if btn_label:
            btn = QPushButton(btn_label)
            btn.setObjectName("btn-primary")
            btn.setFixedHeight(36)
            if btn_callback:
                btn.clicked.connect(btn_callback)
            row.addWidget(btn)

        container = QWidget()
        container.setLayout(row)
        return container, btn

    def make_search_bar(self, placeholder="Rechercher..."):
        search = QLineEdit()
        search.setPlaceholderText(placeholder)
        search.setFixedHeight(34)
        search.setMaximumWidth(320)
        return search

    def make_table(self, headers: list):
        tbl = QTableWidget()
        tbl.setColumnCount(len(headers))
        tbl.setHorizontalHeaderLabels(headers)
        tbl.setAlternatingRowColors(True)
        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)
        tbl.verticalHeader().setVisible(False)
        tbl.horizontalHeader().setStretchLastSection(True)
        tbl.setShowGrid(False)
        tbl.setFocusPolicy(Qt.NoFocus)
        tbl.verticalHeader().setDefaultSectionSize(34)
        return tbl

    def make_stat_card(self, label: str, value: str, value_style="accent"):
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(90)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        lbl = QLabel(label)
        lbl.setObjectName("stat-label")

        val_id = {"accent": "stat-value", "green": "stat-value-green",
                  "red": "stat-value-red"}.get(value_style, "stat-value")
        val = QLabel(value)
        val.setObjectName(val_id)
        # Chiffres en monospace
        val.setFont(QFont(_mono_family(), 18, QFont.Bold))

        layout.addWidget(lbl)
        layout.addWidget(val)
        return card, val

    def cell(self, text, align=Qt.AlignLeft):
        item = QTableWidgetItem(str(text) if text is not None else "")
        item.setTextAlignment(align | Qt.AlignVCenter)
        return item

    def cell_mono(self, text, align=Qt.AlignRight):
        """Cellule avec police monospace — pour les montants et numéros."""
        item = QTableWidgetItem(str(text) if text is not None else "")
        item.setTextAlignment(align | Qt.AlignVCenter)
        item.setFont(QFont(_mono_family(), 9))
        return item

    def cell_colored(self, text, color_hex, align=Qt.AlignLeft):
        """Cellule colorée (pour statuts, badges...)."""
        item = QTableWidgetItem(str(text) if text is not None else "")
        item.setTextAlignment(align | Qt.AlignVCenter)
        item.setForeground(QColor(color_hex))
        return item

    def cell_mono_colored(self, text, color_hex, align=Qt.AlignRight):
        """Cellule mono + colorée — pour les montants avec couleur."""
        item = QTableWidgetItem(str(text) if text is not None else "")
        item.setTextAlignment(align | Qt.AlignVCenter)
        item.setFont(QFont(_mono_family(), 9))
        item.setForeground(QColor(color_hex))
        return item

    def status_badge_text(self, statut):
        icons = {
            "brouillon": "⬜", "envoyé": "🔵", "accepté": "✅",
            "refusé": "❌", "payé": "✅", "en retard": "🔴", "annulé": "⛔"
        }
        return f'{icons.get(statut,"•")} {statut.capitalize()}'
