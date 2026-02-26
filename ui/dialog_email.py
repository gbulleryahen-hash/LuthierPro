"""ui/dialog_email.py — Envoi email avec pièce jointe PDF"""
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QDialogButtonBox,
    QMessageBox, QFrame, QProgressDialog
)
from PySide6.QtCore import Qt, QThread, Signal


class SendThread(QThread):
    done = Signal(bool, str)

    def __init__(self, settings, to, subject, body, pdf_path):
        super().__init__()
        self.settings = settings
        self.to = to
        self.subject = subject
        self.body = body
        self.pdf_path = pdf_path

    def run(self):
        from core.email_sender import send_email
        ok, msg = send_email(self.settings, self.to, self.subject, self.body, self.pdf_path)
        self.done.emit(ok, msg)


class EmailDialog(QDialog):
    def __init__(self, db, doc_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.doc_id = doc_id
        self.pdf_path = None
        doc = db.get_document(doc_id)
        self.doc = doc
        self.setWindowTitle("Envoyer par email")
        self.setMinimumWidth(520)
        self._build(doc)

    def _build(self, doc):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout(); form.setSpacing(10); form.setLabelAlignment(Qt.AlignRight)

        is_facture = doc["type"] == "facture"
        client_email = doc["client_email"] if "client_email" in doc.keys() else ""
        if not client_email and doc["client_id"]:
            c = self.db.get_client(doc["client_id"])
            if c: client_email = c["email"] or ""

        self.to_edit = QLineEdit(client_email); self.to_edit.setFixedHeight(32)
        self.subject_edit = QLineEdit(f"{'Facture' if is_facture else 'Devis'} N°{doc['numero']} — {doc['objet'] or ''}")
        self.subject_edit.setFixedHeight(32)

        s = self.db.get_all_settings()
        default_body = s.get("email_facture" if is_facture else "email_devis", "")
        if not default_body:
            default_body = f"Bonjour,\n\nVeuillez trouver ci-joint {'votre facture' if is_facture else 'votre devis'} N°{doc['numero']}.\n\nCordialement,\n{s.get('name','')}"
        self.body_edit = QTextEdit(default_body); self.body_edit.setFixedHeight(140)

        form.addRow("Destinataire *", self.to_edit)
        form.addRow("Objet",          self.subject_edit)
        form.addRow("Message",        self.body_edit)
        layout.addLayout(form)

        # Pièce jointe
        attach_frame = QFrame(); attach_frame.setObjectName("card")
        af = QHBoxLayout(attach_frame); af.setContentsMargins(12, 8, 12, 8)
        self.attach_lbl = QLabel("Aucun PDF généré")
        self.attach_lbl.setStyleSheet("color:#6a6050;font-size:9pt;")
        af.addWidget(self.attach_lbl)
        af.addStretch()
        btn_gen_pdf = QPushButton("📄  Générer le PDF")
        btn_gen_pdf.setFixedHeight(30)
        btn_gen_pdf.clicked.connect(self._gen_pdf)
        af.addWidget(btn_gen_pdf)
        layout.addWidget(attach_frame)

        # Info SMTP
        smtp_user = self.db.get_setting("smtp_user","")
        if not smtp_user:
            info = QLabel("⚠️  SMTP non configuré — allez dans Mon Entreprise → Configuration email")
            info.setStyleSheet("color:#d4a853;font-size:9pt;padding:6px;background:rgba(212,168,83,0.08);border-radius:4px;")
            info.setWordWrap(True)
            layout.addWidget(info)

        btns = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.btn_send = QPushButton("📧  Envoyer avec pièce jointe")
        self.btn_send.setObjectName("btn-primary")
        self.btn_send.setFixedHeight(36)
        self.btn_send.clicked.connect(self._send)
        btns.addButton(self.btn_send, QDialogButtonBox.AcceptRole)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _gen_pdf(self):
        from core.pdf_generator import generate_pdf
        doc = self.db.get_document(self.doc_id)
        lignes = self.db.get_document_lignes(self.doc_id)
        bilan  = self.db.get_bilan(self.doc_id)
        settings = self.db.get_all_settings()

        docs_dir = os.path.join(os.path.expanduser("~"), "LuthierPro", "PDF")
        os.makedirs(docs_dir, exist_ok=True)
        pdf_path = os.path.join(docs_dir, f"{doc['numero']}.pdf")

        try:
            path = generate_pdf(dict(doc), [dict(l) for l in lignes], bilan, settings, pdf_path)
            self.pdf_path = path
            self.attach_lbl.setText(f"✅  {os.path.basename(path)}")
            self.attach_lbl.setStyleSheet("color:#6bbf8e;font-size:9pt;font-weight:bold;")
        except Exception as e:
            QMessageBox.warning(self, "Erreur PDF", f"Erreur : {e}\n\nInstallez : pip install reportlab")

    def _send(self):
        to = self.to_edit.text().strip()
        if not to:
            QMessageBox.warning(self, "Requis", "Entrez l'adresse email du destinataire.")
            return

        if not self.pdf_path:
            if QMessageBox.question(self, "Pas de PDF",
                "Aucun PDF généré. Envoyer quand même sans pièce jointe ?",
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                return

        settings = self.db.get_all_settings()
        subject  = self.subject_edit.text()
        body     = self.body_edit.toPlainText()

        progress = QProgressDialog("Envoi en cours...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Envoi email")
        progress.setCancelButton(None)
        progress.show()

        self.thread = SendThread(settings, to, subject, body, self.pdf_path)
        self.thread.done.connect(lambda ok, msg: self._on_sent(ok, msg, progress))
        self.thread.start()

    def _on_sent(self, ok, msg, progress):
        progress.close()
        if ok:
            QMessageBox.information(self, "Envoyé ✓", f"Email envoyé à {self.to_edit.text()} ✓")
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur d'envoi", msg)
