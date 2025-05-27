import smtplib
from email.message import EmailMessage

def send_email(to: str, subject: str, body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "no-reply@Chathera.com"
    msg["To"] = to
    msg.set_content(body)

    with smtplib.SMTP("smtp.tonfournisseur.com", 587) as server:
        server.starttls()
        server.login("TON_EMAIL", "TON_MOT_DE_PASSE")
        server.send_message(msg)