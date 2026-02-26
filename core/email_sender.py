"""core/email_sender.py — Envoi email avec pièce jointe PDF via SMTP"""
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


def send_email(settings, to, subject, body, attachment_path=None):
    """
    Envoie un email avec pièce jointe optionnelle.
    settings doit contenir : smtp_host, smtp_port, smtp_user, smtp_password, smtp_from
    Retourne (True, "") en cas de succès, (False, message_erreur) sinon.
    """
    smtp_host = settings.get("smtp_host", "smtp.gmail.com")
    smtp_port = int(settings.get("smtp_port", 587))
    smtp_user = settings.get("smtp_user", "")
    smtp_pass = settings.get("smtp_password", "")
    from_addr = settings.get("smtp_from", smtp_user)

    if not smtp_user or not smtp_pass:
        return False, "Paramètres SMTP non configurés. Rendez-vous dans Mon Entreprise → Email SMTP."

    try:
        msg = MIMEMultipart()
        msg["From"]    = from_addr
        msg["To"]      = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            filename = os.path.basename(attachment_path)
            part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
            msg.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_addr, to, msg.as_string())

        return True, ""

    except smtplib.SMTPAuthenticationError:
        return False, "Échec d'authentification SMTP.\nPour Gmail : activez les 'Mots de passe d'application' dans votre compte Google."
    except smtplib.SMTPConnectError:
        return False, f"Impossible de se connecter à {smtp_host}:{smtp_port}.\nVérifiez votre connexion internet et les paramètres SMTP."
    except Exception as e:
        return False, f"Erreur d'envoi : {str(e)}"
