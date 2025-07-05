import smtplib
from email.message import EmailMessage

async def send_email(to: str, subject: str, body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "no-reply@Chathera.com"
    msg["To"] = to
    msg.set_content(body)

    with smtplib.SMTP("smtp.tonfournisseur.com", 587) as server:
        server.starttls()
        server.login("TON_EMAIL", "TON_MOT_DE_PASSE")
        server.send_message(msg)


async def send_email_verification_code(to_email: str, code: str):
    msg = EmailMessage()
    msg["Subject"] = "Votre code de vérification"
    msg["From"] = "noreply@chathera.com"
    msg["To"] = to_email
    msg.set_content(f"Votre code de vérification est : {code}")

    # SMTP fictif ici
    """
    with smtplib.SMTP_SSL("smtp.exemple.com", 465) as smtp:
        smtp.login("YOUR_EMAIL", "YOUR_PASSWORD")
        smtp.send_message(msg)
    """
    print(f"Email sent to {to_email} with code: {code}")  # Pour les tests, remplacez par l'envoi réel