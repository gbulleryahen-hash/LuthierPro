"""ui/page_settings.py — Paramètres entreprise"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QScrollArea,
    QFrame, QWidget, QGroupBox, QFileDialog, QMessageBox,
    QComboBox, QSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from ui.base_page import BasePage
from core.i18n import t
import os


class SettingsPage(BasePage):
    def setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(16)

        # ── Identité ──────────────────────────────────────
        btn_save = QPushButton(t("btn.save"))
        btn_save.setObjectName("btn-primary"); btn_save.setFixedHeight(36)
        btn_save.clicked.connect(self.save_settings)
        header, _ = self.make_header(t("page.settings.h1"), t("page.settings.h2"), extra_widgets=[btn_save])
        outer.addWidget(header)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        inner = QWidget()
        layout = QVBoxLayout(inner); layout.setContentsMargins(0,0,8,20); layout.setSpacing(18)

        # ── Langue de l'interface ─────────────────────────────
        grp_lang = QGroupBox(t("settings.language"))
        g_lang = QVBoxLayout(grp_lang)
        g_lang.setSpacing(10)

        lang_row = QHBoxLayout()
        self.lang_cb = QComboBox()
        self.lang_cb.setFixedWidth(220)
        self.lang_cb.addItem("🇫🇷  Français",       "fr")
        self.lang_cb.addItem("🇬🇧  English",         "en")
        self.lang_cb.addItem("🇪🇸  Español",         "es")
        lang_row.addWidget(self.lang_cb)
        lang_row.addStretch()
        g_lang.addLayout(lang_row)

        lang_note = QLabel(t("settings.lang_note"))
        lang_note.setStyleSheet("color:#d4a853;font-size:8pt;")
        lang_note.setWordWrap(True)
        g_lang.addWidget(lang_note)
        layout.addWidget(grp_lang)

        # ── Identité ──────────────────────────────────────
        grp1 = QGroupBox("Identité de l'entreprise")
        f1 = QFormLayout(grp1); f1.setSpacing(10); f1.setLabelAlignment(Qt.AlignRight)
        self.f = {}
        fields = [
            ("name",    "Nom / Raison sociale"),
            ("address", "Adresse"),
            ("city",    "Ville / CP"),
            ("phone",   "Téléphone"),
            ("email",   "Email"),
            ("siret",   "SIRET"),
            ("tva",     "N° TVA intracommunautaire"),
        ]
        for key, label in fields:
            w = QLineEdit(); w.setFixedHeight(32)
            f1.addRow(label, w)
            self.f[key] = w
        layout.addWidget(grp1)

        # ── Logo ──────────────────────────────────────────
        grp_logo = QGroupBox("Logo de l'entreprise")
        g_logo = QHBoxLayout(grp_logo); g_logo.setSpacing(16)
        self.logo_preview = QLabel("Aucun logo")
        self.logo_preview.setFixedSize(160, 72)
        self.logo_preview.setAlignment(Qt.AlignCenter)
        self.logo_preview.setStyleSheet("background:#252215;border:1px dashed #3a3525;border-radius:6px;color:#6a6050;font-size:9pt;")
        g_logo.addWidget(self.logo_preview)
        btn_col = QVBoxLayout()
        btn_logo = QPushButton("📁  Choisir une image...")
        btn_logo.setFixedHeight(32); btn_logo.clicked.connect(self._pick_logo)
        btn_rm_logo = QPushButton("🗑  Supprimer le logo")
        btn_rm_logo.setFixedHeight(32); btn_rm_logo.clicked.connect(self._remove_logo)
        note = QLabel("PNG/JPG recommandé\nMax 2 Mo")
        note.setStyleSheet("color:#6a6050;font-size:8pt;")
        btn_col.addWidget(btn_logo); btn_col.addWidget(btn_rm_logo); btn_col.addWidget(note)
        g_logo.addLayout(btn_col); g_logo.addStretch()
        layout.addWidget(grp_logo)

        # ── Banque / IBAN ─────────────────────────────────
        grp2 = QGroupBox("Coordonnées bancaires")
        f2 = QFormLayout(grp2); f2.setSpacing(10); f2.setLabelAlignment(Qt.AlignRight)
        for key, label in [("iban","IBAN"),("bic","BIC"),("bank","Banque")]:
            w = QLineEdit(); w.setFixedHeight(32); f2.addRow(label, w); self.f[key] = w
        layout.addWidget(grp2)

        # ── Numérotation ──────────────────────────────────
        grp3 = QGroupBox("Numérotation & TVA par défaut")
        f3 = QFormLayout(grp3); f3.setSpacing(10); f3.setLabelAlignment(Qt.AlignRight)
        for key, label, ph in [("devisPrefix","Préfixe devis","DEV-"),("facturePrefix","Préfixe facture","FAC-")]:
            w = QLineEdit(); w.setFixedHeight(32); w.setPlaceholderText(ph)
            f3.addRow(label, w); self.f[key] = w

        # TVA par défaut
        from PySide6.QtWidgets import QComboBox as QCB
        self.tva_defaut_cb = QCB()
        from core.styles import TVA_RATES
        for r in TVA_RATES:
            self.tva_defaut_cb.addItem(f"{r:g} %", r)
        self.tva_defaut_cb.setCurrentIndex(3)  # 20% par défaut
        self.tva_defaut_cb.setFixedWidth(120)
        info_tva = QLabel("Appliquée automatiquement sur les nouveaux devis/factures")
        info_tva.setStyleSheet("color:#6a6050;font-size:8pt;")
        tva_row = QHBoxLayout()
        tva_row.addWidget(self.tva_defaut_cb)
        tva_row.addWidget(info_tva)
        tva_row.addStretch()
        tva_widget = QWidget(); tva_widget.setLayout(tva_row)
        f3.addRow("TVA par défaut", tva_widget)
        layout.addWidget(grp3)

        # ── Email SMTP ────────────────────────────────────
        grp4 = QGroupBox("Configuration email (SMTP)")
        f4 = QFormLayout(grp4); f4.setSpacing(10); f4.setLabelAlignment(Qt.AlignRight)
        smtp_fields = [
            ("smtp_host",     "Serveur SMTP",     "smtp.gmail.com"),
            ("smtp_port",     "Port",              "587"),
            ("smtp_user",     "Identifiant",       "votreadresse@gmail.com"),
            ("smtp_password", "Mot de passe",      "Mot de passe d'application"),
            ("smtp_from",     "Expéditeur",        "Laissez vide = identifiant"),
        ]
        for key, label, ph in smtp_fields:
            w = QLineEdit(); w.setFixedHeight(32); w.setPlaceholderText(ph)
            if "password" in key: w.setEchoMode(QLineEdit.Password)
            f4.addRow(label, w); self.f[key] = w

        info = QLabel("💡 Pour Gmail : activez les 'Mots de passe d'application' dans votre compte Google.")
        info.setStyleSheet("color:#d4a853;font-size:8pt;padding:6px;")
        info.setWordWrap(True)
        f4.addRow("", info)
        layout.addWidget(grp4)

        # ── Modèles email ─────────────────────────────────
        grp5 = QGroupBox("Modèles d'email")
        f5 = QFormLayout(grp5); f5.setSpacing(10); f5.setLabelAlignment(Qt.AlignRight)
        self.email_devis = QTextEdit(); self.email_devis.setFixedHeight(80)
        self.email_facture = QTextEdit(); self.email_facture.setFixedHeight(80)
        f5.addRow("Modèle devis", self.email_devis)
        f5.addRow("Modèle facture", self.email_facture)
        layout.addWidget(grp5)

        # ── Mentions légales ─────────────────────────────
        grp6 = QGroupBox("Mentions légales (pied de page)")
        f6 = QVBoxLayout(grp6)
        self.mentions = QTextEdit(); self.mentions.setFixedHeight(80)
        self.mentions.setPlaceholderText("Auto-entrepreneur — TVA non applicable, art. 293 B du CGI...")
        f6.addWidget(self.mentions)
        layout.addWidget(grp6)


        # ── Emplacement de la base de données ────────────────
        grp_db = QGroupBox("Emplacement de la base de données")
        g_db = QVBoxLayout(grp_db); g_db.setSpacing(10)

        info_db = QLabel(
            "La base de données contient TOUTES vos données (clients, guitares, devis, factures).\n"
            "Déplacez-la vers Dropbox, OneDrive, un NAS… pour la synchroniser automatiquement."
        )
        info_db.setStyleSheet("color:#8a8070;font-size:9pt;")
        info_db.setWordWrap(True)
        g_db.addWidget(info_db)

        path_row = QHBoxLayout(); path_row.setSpacing(8)
        self.db_path_edit = QLineEdit()
        self.db_path_edit.setFixedHeight(32)
        self.db_path_edit.setReadOnly(True)
        self.db_path_edit.setStyleSheet("color:#d4a853;font-family:Courier New;font-size:9pt;")

        btn_change_db = QPushButton("📁  Changer l'emplacement…")
        btn_change_db.setFixedHeight(32)
        btn_change_db.clicked.connect(self._change_db_path)

        btn_open_dir = QPushButton("📂  Ouvrir le dossier")
        btn_open_dir.setFixedHeight(32)
        btn_open_dir.clicked.connect(self._open_db_dir)

        path_row.addWidget(self.db_path_edit, 1)
        path_row.addWidget(btn_change_db)
        path_row.addWidget(btn_open_dir)
        g_db.addLayout(path_row)

        self.db_path_info = QLabel("")
        self.db_path_info.setStyleSheet("color:#6bbf8e;font-size:9pt;")
        g_db.addWidget(self.db_path_info)
        layout.addWidget(grp_db)

        # ── Sauvegarde générale ───────────────────────────────
        grp7 = QGroupBox("Sauvegarde & Restauration")
        g7l = QVBoxLayout(grp7); g7l.setSpacing(10)

        info7 = QLabel("Exportez toutes vos données (clients, articles, guitares, devis, factures) dans un fichier JSON.\nUtilisez ce fichier pour sauvegarder ou transférer LuthierPro sur un autre ordinateur.")
        info7.setStyleSheet("color:#8a8070;font-size:9pt;")
        info7.setWordWrap(True)
        g7l.addWidget(info7)

        btn_row7 = QHBoxLayout(); btn_row7.setSpacing(10)

        btn_backup = QPushButton("💾  Sauvegarder tout (JSON)")
        btn_backup.setObjectName("btn-success"); btn_backup.setFixedHeight(36)
        btn_backup.clicked.connect(self._backup_json)

        btn_restore = QPushButton("📂  Restaurer depuis une sauvegarde")
        btn_restore.setFixedHeight(36)
        btn_restore.clicked.connect(self._restore_json)

        btn_export_devis = QPushButton("📤  Exporter devis CSV")
        btn_export_devis.setFixedHeight(36)
        btn_export_devis.clicked.connect(lambda: self._export_docs_csv("devis"))

        btn_export_factures = QPushButton("📤  Exporter factures CSV")
        btn_export_factures.setFixedHeight(36)
        btn_export_factures.clicked.connect(lambda: self._export_docs_csv("facture"))

        btn_row7.addWidget(btn_backup); btn_row7.addWidget(btn_restore)
        btn_row7.addWidget(btn_export_devis); btn_row7.addWidget(btn_export_factures)
        btn_row7.addStretch()
        g7l.addLayout(btn_row7)

        self.backup_info = QLabel("")
        self.backup_info.setStyleSheet("color:#6bbf8e;font-size:9pt;")
        g7l.addWidget(self.backup_info)
        layout.addWidget(grp7)

        scroll.setWidget(inner)
        outer.addWidget(scroll)

    def refresh(self):
        s = self.db.get_all_settings()
        for key, widget in self.f.items():
            widget.setText(s.get(key, ""))
        self.email_devis.setPlainText(s.get("email_devis",""))
        self.email_facture.setPlainText(s.get("email_facture",""))
        self.mentions.setPlainText(s.get("mentions",""))

        # Langue
        saved_lang = s.get("language", "fr") or "fr"
        for i in range(self.lang_cb.count()):
            if self.lang_cb.itemData(i) == saved_lang:
                self.lang_cb.setCurrentIndex(i); break

        # Chemin base de données
        self.db_path_edit.setText(str(self.db.db_path))
        self.db_path_info.setText("")

        # TVA par défaut
        tva_saved = float(s.get("tva_defaut", "20") or 20)
        for i in range(self.tva_defaut_cb.count()):
            if self.tva_defaut_cb.itemData(i) == tva_saved:
                self.tva_defaut_cb.setCurrentIndex(i); break

        # Logo
        logo_path = s.get("logo_path","")
        if logo_path and os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(156, 68, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_preview.setPixmap(pix)
            self.logo_preview.setText("")
        else:
            self.logo_preview.clear()
            self.logo_preview.setText("Aucun logo")

    def save_settings(self):
        for key, widget in self.f.items():
            self.db.set_setting(key, widget.text().strip())
        self.db.set_setting("email_devis",    self.email_devis.toPlainText().strip())
        self.db.set_setting("email_facture",  self.email_facture.toPlainText().strip())
        self.db.set_setting("mentions",       self.mentions.toPlainText().strip())
        self.db.set_setting("tva_defaut",     str(self.tva_defaut_cb.currentData()))
        self.db.set_setting("language",       self.lang_cb.currentData())
        self.main_window.refresh_sidebar_name()
        QMessageBox.information(self, t("msg.saved"), t("settings.saved"))

    def _pick_logo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choisir un logo", "",
            "Images (*.png *.jpg *.jpeg *.webp *.svg)"
        )
        if path:
            stat = os.path.getsize(path)
            if stat > 2 * 1024 * 1024:
                QMessageBox.warning(self, "Fichier trop lourd", "L'image doit faire moins de 2 Mo.")
                return
            pix = QPixmap(path).scaled(156, 68, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_preview.setPixmap(pix)
            self.logo_preview.setText("")
            self.db.set_setting("logo_path", path)

    def _remove_logo(self):
        self.logo_preview.clear()
        self.logo_preview.setText("Aucun logo")
        self.db.set_setting("logo_path", "")

    def _change_db_path(self):
        from PySide6.QtWidgets import QFileDialog, QCheckBox, QDialogButtonBox
        import os

        current = str(self.db.db_path)
        current_dir = os.path.dirname(current)

        # Choisir le nouveau fichier
        new_path, _ = QFileDialog.getSaveFileName(
            self,
            "Choisir l'emplacement de la base de données",
            current,
            "Base de données SQLite (*.db)"
        )
        if not new_path:
            return

        # Assurer l'extension .db
        if not new_path.endswith(".db"):
            new_path += ".db"

        if new_path == current:
            return

        # Demander si on déplace ou on crée une nouvelle DB vide
        from PySide6.QtWidgets import QMessageBox as QMB
        msg = QMB(self)
        msg.setWindowTitle("Déplacer la base de données")
        msg.setText(
            f"Nouveau chemin :\n<b>{new_path}</b>\n\n"
            f"Que souhaitez-vous faire ?"
        )
        msg.setTextFormat(Qt.RichText)
        btn_move  = msg.addButton("📦  Déplacer mes données", QMB.AcceptRole)
        btn_empty = msg.addButton("🆕  Créer une base vide", QMB.DestructiveRole)
        btn_cancel = msg.addButton("Annuler", QMB.RejectRole)
        msg.exec()

        clicked = msg.clickedButton()
        if clicked == btn_cancel:
            return

        move = (clicked == btn_move)

        ok, result = self.db.change_db_path(new_path, move_file=move)
        if ok:
            self.db_path_edit.setText(result)
            self.db_path_info.setText(f"✅ Base de données {'déplacée' if move else 'créée'} à cet emplacement")
            # Mettre à jour la statusbar
            self.main_window.status.showMessage(f"LuthierPro — Base : {result}")
            if not move:
                QMB.information(self, "Nouvelle base créée",
                    "Une nouvelle base de données vide a été créée.\n\n"
                    "⚠️ Vos anciennes données sont toujours dans :\n"
                    f"{current}\n\n"
                    "Redémarrez LuthierPro pour recharger.")
            else:
                QMB.information(self, "Base déplacée ✓",
                    f"La base de données a été déplacée vers :\n{result}\n\n"
                    "Redémarrez LuthierPro pour que le changement soit pris en compte.")
        else:
            self.db_path_info.setText(f"❌ Erreur")
            QMB.critical(self, "Erreur", result)

    def _open_db_dir(self):
        import os, sys, subprocess
        folder = os.path.dirname(str(self.db.db_path))
        try:
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.run(["open", folder])
            else:
                subprocess.run(["xdg-open", folder])
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Dossier", f"Chemin du dossier :\n{folder}")

    def _backup_json(self):
        from PySide6.QtWidgets import QFileDialog
        from core.csv_io import export_backup_json
        from datetime import datetime
        default_name = f"lutherpro-backup-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
        path, _ = QFileDialog.getSaveFileName(self, "Sauvegarder les données", default_name, "JSON (*.json)")
        if path:
            content = export_backup_json(self.db)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            size_kb = os.path.getsize(path) // 1024
            self.backup_info.setText(f"✅ Sauvegarde créée : {os.path.basename(path)} ({size_kb} Ko)")
            QMessageBox.information(self, "Sauvegardé ✓",
                f"Sauvegarde complète créée :\n{path}\n\nConservez ce fichier précieusement !")

    def _restore_json(self):
        from PySide6.QtWidgets import QFileDialog
        from core.csv_io import import_backup_json
        path, _ = QFileDialog.getOpenFileName(self, "Restaurer une sauvegarde", "", "JSON (*.json)")
        if not path:
            return
        reply = QMessageBox.question(self, "Confirmer la restauration",
            "⚠️ La restauration AJOUTE les données de la sauvegarde à la base existante.\n"
            "Les données actuelles ne seront pas supprimées.\n\n"
            "Continuer ?",
            QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            stats = import_backup_json(content, self.db)
            self.main_window.pages["dashboard"].refresh()
            msg = (f"✅ Restauration réussie !\n\n"
                   f"• {stats['clients']} clients\n"
                   f"• {stats['articles']} articles\n"
                   f"• {stats['guitares']} guitares\n"
                   f"• {stats['devis']} devis\n"
                   f"• {stats['factures']} factures")
            QMessageBox.information(self, "Restauré ✓", msg)
            self.backup_info.setText(f"✅ Restauration terminée depuis {os.path.basename(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de lire la sauvegarde :\n{str(e)}")

    def _export_docs_csv(self, doc_type):
        from PySide6.QtWidgets import QFileDialog
        from core.csv_io import export_documents_csv
        docs = self.db.get_documents(doc_type)
        if not docs:
            QMessageBox.information(self, "Vide", f"Aucun{'e' if doc_type=='facture' else ''} {doc_type} à exporter.")
            return
        label = "factures" if doc_type == "facture" else "devis"
        path, _ = QFileDialog.getSaveFileName(self, f"Exporter les {label}", f"{label}.csv", "CSV (*.csv)")
        if path:
            content = export_documents_csv(docs, self.db)
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                f.write(content)
            QMessageBox.information(self, "Exporté ✓", f"{len(docs)} {label} exporté(s) vers :\n{path}")
