"""
core/fonts.py — Gestion des polices pour le générateur PDF.

Polices utilisées (par ordre de préférence) :
  TITRES  : Playfair Display (Google) → LiberationSerif (inclus) → Times-Roman
  TEXTE   : DM Sans (Google)          → LiberationSans (inclus)  → Helvetica
  NUMÉROS : DM Mono (Google)          → LiberationMono (inclus)  → Courier

Pour les vraies polices Google (meilleur rendu) :
  1. Télécharger sur https://fonts.google.com :
       Playfair Display  → PlayfairDisplay-Regular.ttf + PlayfairDisplay-Bold.ttf
       DM Sans           → DMSans-Regular.ttf + DMSans-Bold.ttf + DMSans-Italic.ttf
       DM Mono           → DMMono-Regular.ttf
  2. Copier dans  lutherpro/resources/fonts/
  3. Relancer LuthierPro — détection automatique.
"""
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_FONTS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "resources", "fonts")
)

_font_map = {}   # logical_name → reportlab_name
_initialized = False


def _reg(logical, filename, fallback):
    path = os.path.join(_FONTS_DIR, filename)
    if os.path.exists(path):
        try:
            pdfmetrics.registerFont(TTFont(logical, path))
            _font_map[logical] = logical
            return True
        except Exception:
            pass
    _font_map[logical] = fallback
    return False


def init_fonts():
    global _initialized
    if _initialized:
        return
    _initialized = True

    # ── SERIF (titres) ────────────────────────────────────────
    if not _reg("F-Serif",      "PlayfairDisplay-Regular.ttf", "Times-Roman"):
        _reg("F-Serif",         "LiberationSerif-Regular.ttf", "Times-Roman")
    if not _reg("F-Serif-Bold", "PlayfairDisplay-Bold.ttf",    "Times-Bold"):
        # Playfair est une variable font, on peut réutiliser le Regular en Bold
        if not _reg("F-Serif-Bold", "PlayfairDisplay-Regular.ttf", "Times-Bold"):
            _reg("F-Serif-Bold",    "LiberationSerif-Bold.ttf",    "Times-Bold")

    # ── SANS (corps de texte) ─────────────────────────────────
    if not _reg("F-Sans",       "DMSans-Regular.ttf",          "Helvetica"):
        _reg("F-Sans",          "LiberationSans-Regular.ttf",  "Helvetica")
    if not _reg("F-Sans-Bold",  "DMSans-Bold.ttf",             "Helvetica-Bold"):
        _reg("F-Sans-Bold",     "LiberationSans-Bold.ttf",     "Helvetica-Bold")
    if not _reg("F-Sans-Italic","DMSans-Italic.ttf",           "Helvetica-Oblique"):
        _reg("F-Sans-Italic",   "LiberationSans-Italic.ttf",   "Helvetica-Oblique")

    # ── MONO (numéros, codes) ─────────────────────────────────
    if not _reg("F-Mono",       "DMMono-Regular.ttf",          "Courier"):
        _reg("F-Mono",          "LiberationMono-Regular.ttf",  "Courier")


def F(name):
    """Retourne le nom ReportLab à utiliser pour un nom logique."""
    init_fonts()
    return _font_map.get(name, "Helvetica")


def font_info():
    """Dict résumant les polices actives (utile pour debug)."""
    init_fonts()
    return dict(_font_map)
