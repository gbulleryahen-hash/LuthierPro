"""
core/qt_fonts.py — Chargement des polices TTF pour l'interface Qt (PySide6).

Polices utilisées :
  TITRES  : Playfair Display (serif élégant, Google Fonts)
  TEXTE   : DM Sans ou Noto Sans (au choix, voir SANS_PREFERENCE)
  CHIFFRES: DM Mono (monospace)
  FALLBACK: Liberation* (inclus dans le projet)

Pour utiliser Noto Sans à la place de DM Sans :
  Télécharger NotoSans-Regular.ttf + NotoSans-Bold.ttf + NotoSans-Italic.ttf
  sur fonts.google.com → dossier resources/fonts/
  et changer SANS_PREFERENCE = "noto" ci-dessous.

Pour utiliser DM Sans :
  Télécharger DMSans-Regular.ttf + DMSans-Bold.ttf + DMSans-Italic.ttf
  sur fonts.google.com → dossier resources/fonts/
"""
import os

_FONTS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "resources", "fonts")
)

# ── Choix de la police sans-serif ──────────────────────────
# "dm"   → DM Sans   (plus géométrique, design moderne)
# "noto" → Noto Sans (plus neutre, excellent support caractères)
# Changez cette valeur selon vos préférences :
SANS_PREFERENCE = "dm"
# ────────────────────────────────────────────────────────────

FAMILY_SERIF = "Georgia"
FAMILY_SANS  = "Arial"
FAMILY_MONO  = "Courier New"

_qt_initialized = False


def init_qt_fonts():
    global _qt_initialized, FAMILY_SERIF, FAMILY_SANS, FAMILY_MONO
    if _qt_initialized:
        return
    _qt_initialized = True

    try:
        from PySide6.QtGui import QFontDatabase

        def load(filename):
            path = os.path.join(_FONTS_DIR, filename)
            if os.path.exists(path):
                fid = QFontDatabase.addApplicationFont(path)
                if fid >= 0:
                    families = QFontDatabase.applicationFontFamilies(fid)
                    return families[0] if families else None
            return None

        # ── SERIF — Playfair Display ──────────────────────────
        f = load("PlayfairDisplay-Regular.ttf")
        if f:
            load("PlayfairDisplay-Bold.ttf")
        else:
            f = load("LiberationSerif-Regular.ttf")
            load("LiberationSerif-Bold.ttf")
        if f:
            FAMILY_SERIF = f

        # ── SANS — DM Sans ou Noto Sans ───────────────────────
        if SANS_PREFERENCE == "noto":
            f = load("NotoSans-Regular.ttf")
            if f:
                load("NotoSans-Bold.ttf")
                load("NotoSans-Italic.ttf")
                load("NotoSans-Medium.ttf")
        else:
            f = None

        if not f:  # fallback sur DM Sans quelle que soit la préférence
            f = load("DMSans-Regular.ttf")
            if f:
                load("DMSans-Bold.ttf")
                load("DMSans-Italic.ttf")

        if not f:  # fallback sur Liberation Sans (inclus)
            f = load("LiberationSans-Regular.ttf")
            load("LiberationSans-Bold.ttf")
            load("LiberationSans-Italic.ttf")

        if f:
            FAMILY_SANS = f

        # ── MONO — DM Mono ────────────────────────────────────
        f = load("DMMono-Regular.ttf")
        if not f:
            f = load("LiberationMono-Regular.ttf")
        if f:
            FAMILY_MONO = f

    except Exception:
        pass


def serif():
    init_qt_fonts()
    return FAMILY_SERIF


def sans():
    init_qt_fonts()
    return FAMILY_SANS


def mono():
    init_qt_fonts()
    return FAMILY_MONO
