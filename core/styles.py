"""core/styles.py — Feuille de style globale thème sombre doré"""

STYLESHEET = """
QMainWindow, QDialog, QWidget {
    background-color: #1a1814;
    color: #e8e0d0;
    font-size: 10pt;
}
QWidget#sidebar {
    background-color: #111009;
    border-right: 1px solid #2a2820;
}

/* ── Sidebar header ────────────────────────────── */
QLabel#sidebar-title {
    color: #d4a853;
    font-size: 15pt;
    font-weight: bold;
    padding: 2px 0 0 0;
    letter-spacing: 1px;
}
QLabel#sidebar-sub {
    color: #4a4535;
    font-size: 8pt;
    padding: 0 0 10px 0;
    letter-spacing: 2px;
    text-transform: uppercase;
}
QLabel#sidebar-section {
    color: #3a3428;
    font-size: 7pt;
    font-weight: bold;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 10px 20px 4px 20px;
}

/* ── Navigation buttons ────────────────────────── */
QPushButton.nav-btn {
    background: transparent;
    border: none;
    border-left: 3px solid transparent;
    color: #7a7060;
    text-align: left;
    padding: 9px 16px 9px 20px;
    font-size: 10pt;
    border-radius: 0;
}
QPushButton.nav-btn:hover {
    background-color: #1c1a12;
    color: #c8c0b0;
}
QPushButton.nav-btn[active=true] {
    background-color: #201d10;
    color: #d4a853;
    border-left: 3px solid #d4a853;
    font-weight: bold;
}

/* ── Titres de pages ────────────────────────────── */
QLabel#page-title {
    font-size: 20pt;
    font-weight: bold;
    color: #e8e0d0;
}

/* ── Tableaux ──────────────────────────────────── */
QTableWidget {
    background-color: #1e1c15;
    alternate-background-color: #1a1814;
    border: 1px solid #2a2820;
    border-radius: 6px;
    gridline-color: #222118;
    selection-background-color: #2c2812;
    selection-color: #e8e0d0;
    outline: none;
}
QTableWidget::item {
    padding: 5px 10px;
    border: none;
}
QTableWidget::item:selected {
    background-color: #2c2812;
    color: #d4a853;
}
QHeaderView::section {
    background-color: #111009;
    color: #5a5040;
    font-size: 7pt;
    font-weight: bold;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid #2a2820;
    border-right: 1px solid #1e1c14;
}

/* ── Champs de saisie ──────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit,
QSpinBox, QDoubleSpinBox, QDateEdit, QComboBox {
    background-color: #232111;
    border: 1px solid #353220;
    border-radius: 5px;
    color: #e8e0d0;
    padding: 6px 10px;
    selection-background-color: #d4a853;
    selection-color: #1a1814;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus,
QDateEdit:focus, QComboBox:focus {
    border: 1px solid #d4a853;
    background-color: #272512;
}
QComboBox::drop-down { border: none; padding-right: 6px; }
QComboBox::down-arrow { width: 10px; }
QComboBox QAbstractItemView {
    background-color: #232111;
    border: 1px solid #353220;
    color: #e8e0d0;
    selection-background-color: #d4a853;
    selection-color: #1a1814;
}

/* ── Boutons ───────────────────────────────────── */
QPushButton {
    background-color: #2a2820;
    border: 1px solid #3a3525;
    border-radius: 5px;
    color: #e8e0d0;
    padding: 7px 16px;
    font-size: 10pt;
}
QPushButton:hover { background-color: #333020; border-color: #4a4535; }
QPushButton:pressed { background-color: #1f1d16; }
QPushButton:disabled { color: #4a4535; border-color: #2a2820; }

QPushButton#btn-primary {
    background-color: #d4a853;
    border-color: #d4a853;
    color: #1a1814;
    font-weight: bold;
}
QPushButton#btn-primary:hover { background-color: #e0b860; border-color: #e0b860; }
QPushButton#btn-danger {
    background-color: #6b2020; border-color: #7a2525; color: #ffcccc;
}
QPushButton#btn-danger:hover { background-color: #7a2525; }
QPushButton#btn-success {
    background-color: #1a5232; border-color: #2e6b4a; color: #ccffe0;
}
QPushButton#btn-success:hover { background-color: #2e6b4a; }
QPushButton#btn-flat {
    background: transparent; border: none; color: #7a7060; padding: 5px 10px;
}
QPushButton#btn-flat:hover {
    color: #d4a853;
    background: rgba(212,168,83,0.08);
    border-radius: 4px;
}

/* ── Onglets ────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #2a2820; border-radius: 6px; background-color: #1e1c15;
}
QTabBar::tab {
    background-color: #1a1814; color: #6a6050;
    padding: 8px 18px; border: 1px solid #2a2820;
    border-bottom: none; border-radius: 5px 5px 0 0; margin-right: 2px;
}
QTabBar::tab:selected { background-color: #1e1c15; color: #d4a853; }
QTabBar::tab:hover    { color: #e8e0d0; }

/* ── Scrollbars ────────────────────────────────── */
QScrollBar:vertical   { background: #1a1814; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #3a3525; border-radius: 4px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #d4a853; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #1a1814; height: 8px; border-radius: 4px; }
QScrollBar::handle:horizontal { background: #3a3525; border-radius: 4px; min-width: 20px; }
QScrollBar::handle:horizontal:hover { background: #d4a853; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Cards ─────────────────────────────────────── */
QGroupBox {
    border: 1px solid #2a2820; border-radius: 6px;
    margin-top: 12px; padding-top: 8px;
    color: #5a5040; font-size: 9pt; font-weight: bold; letter-spacing: 1px;
}
QGroupBox::title {
    subcontrol-origin: margin; subcontrol-position: top left;
    padding: 0 8px; color: #5a5040;
}
QStatusBar {
    background-color: #0f0e0b; color: #4a4535;
    font-size: 9pt; border-top: 1px solid #222118;
}
QFrame#card {
    background-color: #201e14; border: 1px solid #2a2820; border-radius: 8px;
}
QFrame#card-accent {
    background-color: #201e14; border: 1px solid #d4a853;
    border-left: 3px solid #d4a853; border-radius: 8px;
}

/* ── Labels stats (chiffres en Mono) ───────────── */
QLabel#stat-value {
    font-size: 22pt; font-weight: bold; color: #d4a853;
}
QLabel#stat-value-green {
    font-size: 22pt; font-weight: bold; color: #6bbf8e;
}
QLabel#stat-value-red {
    font-size: 22pt; font-weight: bold; color: #d46060;
}
QLabel#stat-label { font-size: 9pt; color: #6a6050; }

/* ── Badges de statut ──────────────────────────── */
QLabel#badge-payé, QLabel#badge-accepté {
    color: #6bbf8e; background: rgba(107,191,142,0.12);
    border: 1px solid rgba(107,191,142,0.3); border-radius: 8px;
    padding: 2px 8px; font-size: 8pt;
}
QLabel#badge-envoyé {
    color: #6090d4; background: rgba(96,144,212,0.12);
    border: 1px solid rgba(96,144,212,0.3); border-radius: 8px;
    padding: 2px 8px; font-size: 8pt;
}
QLabel#badge-refusé, QLabel#badge-en\\ retard {
    color: #d46060; background: rgba(212,96,96,0.12);
    border: 1px solid rgba(212,96,96,0.3); border-radius: 8px;
    padding: 2px 8px; font-size: 8pt;
}
QLabel#badge-brouillon {
    color: #8a8070; background: rgba(138,128,112,0.12);
    border: 1px solid rgba(138,128,112,0.3); border-radius: 8px;
    padding: 2px 8px; font-size: 8pt;
}

QSplitter::handle { background-color: #2a2820; }
QMessageBox { background-color: #1e1c15; }
QMessageBox QPushButton { min-width: 80px; }
"""

BILAN_FIELDS = [
    ("courbure",     "Courbure du manche"),
    ("hauteur",      "Hauteur des cordes"),
    ("tirant",       "Tirant des cordes"),
    ("tete",         "Tête"),
    ("mecaniques",   "Mécaniques"),
    ("sillet",       "Sillet"),
    ("touche",       "Touche"),
    ("frettes",      "Frettes"),
    ("manche",       "Manche"),
    ("corps",        "Corps"),
    ("chevalet",     "Chevalet"),
    ("cordes",       "Cordes"),
    ("electronique", "Électronique"),
]

STATUTS_DEVIS   = ["brouillon", "envoyé", "accepté", "refusé"]
STATUTS_FACTURE = ["brouillon", "envoyé", "payé", "en retard", "annulé"]
TYPES_GUITARE   = ["électrique", "acoustique", "semi-acoustique", "classique", "basse", "folk", "autre"]
TYPES_ARTICLE   = ["service", "produit", "frais"]
UNITES          = ["unité", "heure", "jour", "forfait", "mois", "km"]
TVA_RATES       = [0, 5.5, 10, 20]
