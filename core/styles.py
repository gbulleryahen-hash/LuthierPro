"""core/styles.py — Feuille de style globale thème sombre doré — contraste amélioré"""

STYLESHEET = """
QMainWindow, QDialog, QWidget {
    background-color: #1e1c14;
    color: #ede5d4;
    font-size: 10pt;
}
QWidget#sidebar {
    background-color: #1e1b10;
    border-right: 2px solid #4a4228;
}

/* ── Sidebar header ────────────────────────────── */
QLabel#sidebar-title {
    color: #f2c84a;
    font-size: 15pt;
    font-weight: bold;
    padding: 2px 0 0 0;
    letter-spacing: 1px;
}
QLabel#sidebar-sub {
    color: #908258;
    font-size: 8pt;
    padding: 0 0 10px 0;
    letter-spacing: 2px;
}
QLabel#sidebar-section {
    /* ★ Beaucoup plus visible — était #3a3428 quasi invisible */
    color: #d4a040;
    font-size: 7pt;
    font-weight: 900;
    letter-spacing: 3px;
    padding: 14px 20px 5px 20px;
}

/* ── Navigation buttons ────────────────────────── */
QPushButton.nav-btn {
    background: transparent;
    border: none;
    border-left: 3px solid transparent;
    /* ★ Texte nav inactif relevé : #7a7060 → #a09880 */
    color: #a09880;
    text-align: left;
    padding: 9px 16px 9px 20px;
    font-size: 10pt;
    border-radius: 0;
}
QPushButton.nav-btn:hover {
    background-color: #242110;
    /* ★ Hover bien visible */
    color: #ddd5c0;
    border-left: 3px solid #4a4535;
}
QPushButton.nav-btn[active=true] {
    background-color: #28240e;
    color: #e0b860;
    border-left: 3px solid #e0b860;
    font-weight: bold;
}

/* ── Titres de pages ────────────────────────────── */
QLabel#page-title {
    font-size: 20pt;
    font-weight: bold;
    color: #ede5d4;
}

/* ── Tableaux ──────────────────────────────────── */
QTableWidget {
    background-color: #221f16;
    /* ★ Alternance plus visible */
    alternate-background-color: #1e1c14;
    border: 1px solid #332f1e;
    border-radius: 6px;
    gridline-color: #2a2820;
    selection-background-color: #33300e;
    selection-color: #f0e8d0;
    outline: none;
}
QTableWidget::item {
    padding: 6px 10px;
    border: none;
    /* ★ Texte tableau relevé */
    color: #d8d0c0;
}
QTableWidget::item:selected {
    background-color: #33300e;
    color: #e0b860;
}
QHeaderView::section {
    /* ★★ Header tableau : fond doré sombre + texte très lisible */
    background-color: #2c2610;
    color: #e8d090;
    font-size: 7pt;
    font-weight: bold;
    letter-spacing: 2px;
    padding: 10px 10px;
    border: none;
    border-bottom: 2px solid #e0b840;
    border-right: 1px solid #3a3418;
}

/* ── Champs de saisie ──────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit,
QSpinBox, QDoubleSpinBox, QDateEdit, QComboBox {
    /* ★ Fond légèrement plus clair pour contraste avec le fond page */
    background-color: #282410;
    border: 1px solid #443e28;
    border-radius: 5px;
    color: #ede5d4;
    padding: 6px 10px;
    selection-background-color: #d4a853;
    selection-color: #1a1814;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus,
QDateEdit:focus, QComboBox:focus {
    border: 1px solid #e0b860;
    background-color: #2e2a12;
    /* ★ Glow doré subtil au focus */
    border-width: 2px;
}
QComboBox::drop-down { border: none; padding-right: 6px; }
QComboBox::down-arrow { width: 10px; }
QComboBox QAbstractItemView {
    background-color: #282410;
    border: 1px solid #443e28;
    color: #ede5d4;
    selection-background-color: #d4a853;
    selection-color: #1a1814;
}

/* ── Labels formulaires ────────────────────────── */
QFormLayout QLabel {
    /* ★ Labels de formulaire plus lisibles */
    color: #b0a890;
}

/* ── Boutons ───────────────────────────────────── */
QPushButton {
    /* ★ Boutons standard : fond plus clair, texte plus lumineux */
    background-color: #302c18;
    border: 1px solid #504838;
    border-radius: 5px;
    color: #ede5d4;
    padding: 7px 16px;
    font-size: 10pt;
}
QPushButton:hover {
    background-color: #3c3820;
    border-color: #6a6040;
    color: #ffffff;
}
QPushButton:pressed { background-color: #252214; }
QPushButton:disabled { color: #5a5242; border-color: #2e2c1e; }

QPushButton#btn-primary {
    background-color: #d4a853;
    border-color: #e0b860;
    color: #141209;
    font-weight: bold;
}
QPushButton#btn-primary:hover {
    background-color: #e8c070;
    border-color: #e8c070;
    color: #0e0d08;
}
QPushButton#btn-danger {
    background-color: #6b2020; border-color: #8a3030; color: #ffd0d0;
}
QPushButton#btn-danger:hover { background-color: #7a2828; border-color: #a03030; }
QPushButton#btn-success {
    background-color: #1a4a30; border-color: #2e6b4a; color: #c8f0dc;
}
QPushButton#btn-success:hover { background-color: #226040; border-color: #3a8060; }
QPushButton#btn-flat {
    background: transparent; border: none;
    /* ★ Boutons icônes plus visibles */
    color: #908878; padding: 5px 10px;
}
QPushButton#btn-flat:hover {
    color: #e0b860;
    background: rgba(212,168,83,0.12);
    border-radius: 4px;
}

/* ── GroupBox ───────────────────────────────────── */
QGroupBox {
    border: 1px solid #332f1e;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 10px;
    /* ★ Titre GroupBox relevé : #5a5040 → #9a8c6c */
    color: #9a8c6c;
    font-size: 9pt;
    font-weight: bold;
    letter-spacing: 0.5px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    color: #9a8c6c;
    /* ★ Fond du titre pour lisibilité */
    background-color: #1e1c14;
}

/* ── Onglets ────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #332f1e; border-radius: 6px; background-color: #221f16;
}
QTabBar::tab {
    background-color: #1e1c14;
    /* ★ Onglet inactif : texte plus visible */
    color: #9a9080;
    padding: 8px 20px; border: 1px solid #332f1e;
    border-bottom: none; border-radius: 5px 5px 0 0; margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #221f16;
    color: #e0b860;
    border-bottom: 2px solid #e0b860;
}
QTabBar::tab:hover { color: #ede5d4; background-color: #282410; }

/* ── Scrollbars ────────────────────────────────── */
QScrollBar:vertical   { background: #1a1810; width: 9px; border-radius: 4px; }
QScrollBar::handle:vertical {
    /* ★ Scrollbar plus visible */
    background: #504838; border-radius: 4px; min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #d4a853; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #1a1810; height: 9px; border-radius: 4px; }
QScrollBar::handle:horizontal {
    background: #504838; border-radius: 4px; min-width: 24px;
}
QScrollBar::handle:horizontal:hover { background: #d4a853; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Cards ─────────────────────────────────────── */
QStatusBar {
    background-color: #0f0e09; color: #6a6248;
    font-size: 9pt; border-top: 1px solid #2a2820;
}
QFrame#card {
    /* ★ Cards : fond distinct + bordure plus visible */
    background-color: #242118; border: 1px solid #3a3625; border-radius: 8px;
}
QFrame#card-accent {
    background-color: #242118;
    border: 1px solid #c09040;
    border-left: 3px solid #d4a853;
    border-radius: 8px;
}

/* ── Labels stats ──────────────────────────────── */
QLabel#stat-value {
    font-size: 22pt; font-weight: bold; color: #e0b860;
}
QLabel#stat-value-green {
    font-size: 22pt; font-weight: bold; color: #7dd4a4;
}
QLabel#stat-value-red {
    font-size: 22pt; font-weight: bold; color: #e07070;
}
/* ★ Label stat : texte relevé */
QLabel#stat-label { font-size: 9pt; color: #907868; }

/* ── Badges de statut ──────────────────────────── */
/* ★ Badges : opacité et bordures renforcées pour bien les distinguer */
QLabel#badge-payé, QLabel#badge-accepté {
    color: #88d4a8;
    background: rgba(107,191,142,0.20);
    border: 1px solid rgba(107,191,142,0.50);
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 8pt;
    font-weight: bold;
}
QLabel#badge-envoyé {
    color: #80aae0;
    background: rgba(96,144,212,0.20);
    border: 1px solid rgba(96,144,212,0.50);
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 8pt;
    font-weight: bold;
}
QLabel#badge-refusé, QLabel#badge-en\\ retard, QLabel#badge-annulé {
    color: #e08080;
    background: rgba(212,96,96,0.20);
    border: 1px solid rgba(212,96,96,0.50);
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 8pt;
    font-weight: bold;
}
QLabel#badge-brouillon {
    color: #b0a890;
    background: rgba(160,152,132,0.18);
    border: 1px solid rgba(160,152,132,0.40);
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 8pt;
}

QSplitter::handle { background-color: #2e2c1e; }
QMessageBox { background-color: #221f16; }
QMessageBox QPushButton { min-width: 80px; }
QToolTip {
    background-color: #302c18;
    color: #ede5d4;
    border: 1px solid #c09040;
    padding: 4px 8px;
    border-radius: 4px;
}
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
