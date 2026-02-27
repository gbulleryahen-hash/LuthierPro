"""ui/main_window.py — Fenêtre principale avec sidebar"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

from ui.page_dashboard import DashboardPage
from ui.page_clients    import ClientsPage
from ui.page_articles   import ArticlesPage
from ui.page_guitares   import GuitaresPage
from ui.page_devis      import DevisPage
from ui.page_factures   import FacturesPage
from ui.page_settings   import SettingsPage
from ui.page_bilan      import BilanPage
from core.i18n import t


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("LuthierPro")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        import os
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "logo.png")
        if os.path.exists(logo_path):
            from PySide6.QtGui import QIcon
            self.setWindowIcon(QIcon(logo_path))

        self._build_ui()
        self._build_sidebar()
        self._build_pages()
        self.navigate("dashboard")

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage(f"LuthierPro v1.0 — Base : {self.db.db_path}")

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        self.root_layout = QHBoxLayout(central)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

    def _build_sidebar(self):
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(218)
        sb = QVBoxLayout(self.sidebar)
        sb.setContentsMargins(0, 0, 0, 0)
        sb.setSpacing(0)

        # ── Logo + titre centré ──────────────────────────────
        from core.qt_fonts import serif as _serif, init_qt_fonts
        init_qt_fonts()

        header_w = QWidget()
        header_w.setStyleSheet("background: transparent;")
        hl = QVBoxLayout(header_w)
        hl.setContentsMargins(0, 22, 0, 16)
        hl.setSpacing(8)
        hl.setAlignment(Qt.AlignHCenter)

        logo_lbl = QLabel()
        logo_lbl.setAlignment(Qt.AlignCenter)
        import os
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "logo.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_lbl.setPixmap(pix)
        hl.addWidget(logo_lbl, alignment=Qt.AlignHCenter)

        sf = _serif()
        title = QLabel("LuthierPro")
        title.setObjectName("sidebar-title")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont(sf, 15, QFont.Bold))
        hl.addWidget(title, alignment=Qt.AlignHCenter)

        sub = QLabel("ATELIER")
        sub.setObjectName("sidebar-sub")
        sub.setStyleSheet("color:#a09060;font-size:8pt;letter-spacing:2px;")
        sub.setAlignment(Qt.AlignCenter)
        hl.addWidget(sub, alignment=Qt.AlignHCenter)

        sb.addWidget(header_w)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background:#2a2820;max-height:1px;border:none;")
        sb.addWidget(sep)

        # ── Boutons de navigation ────────────────────────────
        nav_items = [
            ("section", t("nav.principal")),
            ("page", "dashboard",  f"📊  {t('nav.dashboard')}"),
            ("section", t("nav.documents")),
            ("page", "devis",      f"📋  {t('nav.devis')}"),
            ("page", "factures",   f"🧾  {t('nav.factures')}"),
            ("section", t("nav.database")),
            ("page", "clients",    f"👥  {t('nav.clients')}"),
            ("page", "articles",   f"📦  {t('nav.articles')}"),
            ("page", "guitares",   f"🎸  {t('nav.guitares')}"),
            ("section", t("nav.analysis")),
            ("page", "bilan",      f"📈  {t('nav.bilan')}"),
            ("section", ""),
        ]

        self.nav_buttons = {}
        for item in nav_items:
            if item[0] == "section":
                lbl = QLabel(item[1])
                lbl.setObjectName("sidebar-section")
                sb.addWidget(lbl)
            else:
                _, page_id, label = item
                btn = QPushButton(label)
                btn.setProperty("active", False)
                btn.setStyleSheet(self._nav_style(False))
                btn.setCursor(Qt.PointingHandCursor)
                btn.setFixedHeight(38)
                btn.clicked.connect(lambda checked, p=page_id: self.navigate(p))
                self.nav_buttons[page_id] = btn
                sb.addWidget(btn)

        sb.addStretch()

        # ── Pied de sidebar ──────────────────────────────────
        self.sb_company_lbl = QLabel(self.db.get_setting("name", "Mon atelier"))
        self.sb_company_lbl.setStyleSheet("color:#706858;font-size:9pt;padding:8px 16px 2px 20px;")
        self.sb_company_lbl.setWordWrap(True)
        sb.addWidget(self.sb_company_lbl)

        settings_btn = QPushButton(f"⚙️  {t('nav.settings')}")
        settings_btn.setStyleSheet(self._nav_style(False))
        settings_btn.setFixedHeight(38)
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.clicked.connect(lambda: self.navigate("settings"))
        self.nav_buttons["settings"] = settings_btn
        sb.addWidget(settings_btn)

        about_btn = QPushButton(f"ℹ️  {t('nav.about')}")
        about_btn.setStyleSheet(self._nav_style(False))
        about_btn.setFixedHeight(38)
        about_btn.setCursor(Qt.PointingHandCursor)
        about_btn.clicked.connect(self._open_about)
        sb.addWidget(about_btn)

        self.root_layout.addWidget(self.sidebar)

    def _nav_style(self, active):
        if active:
            return (
                "QPushButton { background-color:#2e2a0c; color:#f2c840; border:none;"
                "border-left:4px solid #f2c840; text-align:left; padding:9px 16px 9px 19px; font-weight:bold; }"
            )
        return (
            "QPushButton { background:transparent; color:#c8bc96; border:none;"
            "border-left:4px solid transparent; text-align:left; padding:9px 16px 9px 19px; }"
            "QPushButton:hover { background-color:#28240c; color:#f0e8d0;"
            "border-left:4px solid #c8a840; }"
        )

    def _build_pages(self):
        self.stack = QStackedWidget()
        self.root_layout.addWidget(self.stack)
        self.pages = {
            "dashboard": DashboardPage(self.db, self),
            "devis":     DevisPage(self.db, self),
            "factures":  FacturesPage(self.db, self),
            "clients":   ClientsPage(self.db, self),
            "articles":  ArticlesPage(self.db, self),
            "guitares":  GuitaresPage(self.db, self),
            "bilan":     BilanPage(self.db, self),
            "settings":  SettingsPage(self.db, self),
        }
        for page in self.pages.values():
            self.stack.addWidget(page)

    def navigate(self, page_id):
        for pid, btn in self.nav_buttons.items():
            btn.setStyleSheet(self._nav_style(pid == page_id))
        if page_id in self.pages:
            self.stack.setCurrentWidget(self.pages[page_id])
            self.pages[page_id].refresh()

    def _open_about(self):
        from ui.dialog_about import AboutDialog
        dlg = AboutDialog(self)
        dlg.exec()

    def refresh_sidebar_name(self):
        name = self.db.get_setting("name", "Mon atelier")
        self.sb_company_lbl.setText(name)
