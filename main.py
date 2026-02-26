"""
LuthierPro — Logiciel de gestion pour luthier
Entrée principale de l'application
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from ui.main_window import MainWindow
from core.database import Database
from core.styles import STYLESHEET
from core.qt_fonts import init_qt_fonts, sans, mono
from core.i18n import set_language


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LuthierPro")
    app.setApplicationVersion("1.0.0")
    app.setStyle("Fusion")

    # Charger les polices TTF
    init_qt_fonts()
    app.setFont(QFont(sans(), 10))
    app.setStyleSheet(STYLESHEET)

    # Base de données
    db = Database()
    db.initialize()

    # Charger la langue sauvegardée
    lang = db.get_setting("language", "fr") or "fr"
    set_language(lang)

    window = MainWindow(db)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
