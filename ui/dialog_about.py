"""ui/dialog_about.py — Fenêtre "À propos de LuthierPro" """
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont, QDesktopServices
from PySide6.QtCore import QUrl
import os
from core.i18n import t
from core.qt_fonts import serif as _serif, mono as _mono


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("about.title"))
        self.setFixedSize(460, 540)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sf = _serif()
        mf = _mono()

        # ── Bandeau doré en haut ───────────────────────────────
        banner = QFrame()
        banner.setFixedHeight(180)
        banner.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
                             "stop:0 #2a2518, stop:1 #1a1814);")
        b_layout = QVBoxLayout(banner)
        b_layout.setContentsMargins(0, 24, 0, 20)
        b_layout.setSpacing(10)
        b_layout.setAlignment(Qt.AlignHCenter)

        # Logo
        logo_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "resources", "logo.png"
        )
        logo_lbl = QLabel()
        logo_lbl.setAlignment(Qt.AlignCenter)
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_lbl.setPixmap(pix)
        b_layout.addWidget(logo_lbl, alignment=Qt.AlignHCenter)

        # Nom
        name_lbl = QLabel("LuthierPro")
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setFont(QFont(sf, 22, QFont.Bold))
        name_lbl.setStyleSheet("color: #d4a853; background: transparent;")
        b_layout.addWidget(name_lbl, alignment=Qt.AlignHCenter)

        layout.addWidget(banner)

        # ── Ligne séparatrice or ───────────────────────────────
        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                          "stop:0 #1a1814, stop:0.3 #d4a853, stop:0.7 #d4a853, stop:1 #1a1814);")
        layout.addWidget(sep)

        # ── Corps ──────────────────────────────────────────────
        body = QFrame()
        body.setStyleSheet("background: #1a1814;")
        b2 = QVBoxLayout(body)
        b2.setContentsMargins(40, 28, 40, 28)
        b2.setSpacing(6)

        # Tagline
        tagline = QLabel(t("about.tagline"))
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setStyleSheet("color: #8a8070; font-size: 10pt;")
        tagline.setWordWrap(True)
        b2.addWidget(tagline)

        b2.addSpacing(20)

        # Infos tableau
        def info_row(label, value, mono=False, color="#e8e0d0"):
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #6a6050; font-size: 9pt;")
            lbl.setFixedWidth(130)
            val = QLabel(value)
            if mono:
                val.setFont(QFont(mf, 9))
            val.setStyleSheet(f"color: {color}; font-size: 9pt;")
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch()
            b2.addLayout(row)

        info_row(t("about.version"),     "1.0.0", mono=True, color="#d4a853")
        info_row(t("about.license"),     t("about.license_val"), color="#6bbf8e")
        info_row(t("about.built_with"),  "Python 3 · PySide6 · ReportLab")

        b2.addSpacing(20)

        # Stack technique (liens cliquables visuellement)
        stack_frame = QFrame()
        stack_frame.setStyleSheet(
            "background: #201e14; border: 1px solid #2a2820; border-radius: 8px;"
        )
        sf_l = QHBoxLayout(stack_frame)
        sf_l.setContentsMargins(16, 12, 16, 12)
        sf_l.setSpacing(0)

        for tech, color in [
            ("Python",       "#f5c542"),
            ("  ·  ", "#4a4535"),
            ("PySide6",      "#41cd52"),
            ("  ·  ", "#4a4535"),
            ("ReportLab",    "#6090d4"),
            ("  ·  ", "#4a4535"),
            ("SQLite",       "#d4a853"),
        ]:
            lbl = QLabel(tech)
            lbl.setFont(QFont(mf, 9))
            lbl.setStyleSheet(f"color: {color}; background: transparent;")
            sf_l.addWidget(lbl)
        sf_l.addStretch()
        b2.addWidget(stack_frame)

        b2.addSpacing(20)

        # Copyright
        copy_lbl = QLabel(t("about.copyright"))
        copy_lbl.setAlignment(Qt.AlignCenter)
        copy_lbl.setStyleSheet("color: #4a4535; font-size: 8pt;")
        copy_lbl.setWordWrap(True)
        b2.addWidget(copy_lbl)

        b2.addStretch()

        layout.addWidget(body, 1)

        # ── Boutons bas ────────────────────────────────────────
        btn_bar = QFrame()
        btn_bar.setStyleSheet("background: #111009; border-top: 1px solid #2a2820;")
        bb = QHBoxLayout(btn_bar)
        bb.setContentsMargins(20, 12, 20, 12)
        bb.setSpacing(10)

        btn_license = QPushButton("🔓  GNU GPL v3")
        btn_license.setStyleSheet(
            "background: transparent; border: 1px solid #3a3525; color: #6bbf8e;"
            "border-radius: 5px; padding: 6px 14px;"
        )
        btn_license.setCursor(Qt.PointingHandCursor)
        btn_license.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://www.gnu.org/licenses/gpl-3.0.html"))
        )

        btn_close = QPushButton(t("btn.close"))
        btn_close.setObjectName("btn-primary")
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(self.accept)

        bb.addWidget(btn_license)
        bb.addStretch()
        bb.addWidget(btn_close)

        layout.addWidget(btn_bar)
