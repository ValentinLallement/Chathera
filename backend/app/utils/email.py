import os
import smtplib
from email.message import EmailMessage
from app.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL

async def send_email(to: str, subject: str, html_body: str, plain_text_body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to

    msg.set_content(plain_text_body)  # Version texte brut
    msg.add_alternative(html_body, subtype="html")  # Version HTML

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"[send_email] Email envoyé à {to}")
    except Exception as e:
        print(f"[send_email] Erreur d'envoi: {e}")
        raise e

async def send_email_verification_code(to_email: str, code: str):
    subject = "Votre code de vérification"
    body = f"Bonjour,\n\nVoici votre code de vérification : {code}\n\nMerci,\nL’équipe Chathera"
    await send_email(to_email, subject, body,body)


async def send_email_for_password_reset(to: str, subject: str, reset_link: str):
    # Template HTML complet avec insertion du lien dynamique
    html_content = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Réinitialisation de mot de passe</title>
    <style>
        /* Insérer ici ton CSS inline si besoin */
    </style>
</head>
<body style="background-color: #d9dffa; margin: 0; padding: 0;">
<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background-color: #d9dffa;">
    <tr>
        <td align="center">
            <table width="600" cellpadding="0" cellspacing="0" role="presentation" style="background-color: #cfd6f4; margin: 20px auto; border-radius: 8px; overflow: hidden;">
                <tr>
                    <td align="center" style="padding: 20px;">
                        <img src="https://d1oco4z2z1fhwp.cloudfront.net/templates/default/3991/animated_header.gif" alt="Header Image" width="600" style="width: 100%; max-width: 600px; height: auto; display: block;" />
                    </td>
                </tr>
                <tr>
                    <td style="padding: 15px 50px; font-family: Helvetica, Arial, sans-serif; color: #40507a;">
                        <h1 style="color:#506bec; font-size: 38px; margin: 0 0 10px;">Forgot your password?</h1>
                        <p style="font-size: 16px; margin: 10px 0;">Hey, we received a request to reset your password.</p>
                        <p style="font-size: 16px; margin: 10px 0;">Let’s get you a new one!</p>
                        <p style="text-align: left; margin: 30px 0;">
                            <a href="{reset_link}" target="_blank" style="
                                background-color: #506bec;
                                color: #ffffff;
                                text-decoration: none;
                                padding: 12px 30px;
                                border-radius: 16px;
                                font-weight: bold;
                                font-size: 16px;
                                display: inline-block;
                                ">
                                RESET MY PASSWORD
                            </a>
                        </p>
                        <p style="font-size: 14px; color: #40507a;">
                            Having trouble? <a href="http://chathera.com/contact" style="color: #40507a; text-decoration: none;" target="_blank"><strong>@contact</strong></a>
                        </p>
                        <p style="font-size: 14px; color: #40507a;">Didn’t request a password reset? You can ignore this message.</p>
                    </td>
                </tr>
                <tr>
                    <td align="center" style="padding: 10px 0;">
                        <img src="https://d1oco4z2z1fhwp.cloudfront.net/templates/default/3991/bottom_img.png" alt="" width="600" style="width: 100%; max-width: 600px; height: auto; display: block;" />
                    </td>
                </tr>
                <tr style="background-color: #ffffff;">
                    <td align="center" style="padding: 10px;">
                        <a href="http://chathera.com/" target="_blank">
                            <img src="https://d1oco4z2z1fhwp.cloudfront.net/templates/default/3991/logo.png" alt="Logo" width="145" style="height: auto; display: block; margin: auto;" />
                        </a>
                        <table cellpadding="0" cellspacing="0" style="margin: 10px auto; text-align: center;">
                            <tr>
                                <td><a href="https://www.instagram.com/chathera_officiel/" target="_blank"><img src="https://app-rsrc.getbee.io/public/resources/social-networks-icon-sets/t-only-logo-dark-gray/instagram@2x.png" alt="Instagram" width="32" style="border:0;" /></a></td>
                                <td><a href="https://x.com/ChatheraAI" target="_blank"><img src="https://app-rsrc.getbee.io/public/resources/social-networks-icon-sets/t-only-logo-dark-gray/twitter@2x.png" alt="Twitter" width="32" style="border:0;" /></a></td>
                            </tr>
                        </table>
                        <p style="font-family: Helvetica, Arial, sans-serif; font-size: 14px; color: #97a2da; margin: 5px 0;">
                            This link will expire in the next 30 minutes.<br />
                            Please feel free to contact us at contact@chathera.com.
                        </p>
                        <p style="font-family: Helvetica, Arial, sans-serif; font-size: 12px; color: #97a2da; margin: 5px 0;">
                            Copyright© 2021 Your Brand.<br />
                            <a href="http://chathera.com/unsubscribe" style="color: #97a2da; text-decoration: underline;" target="_blank">Unsubscribe</a> |
                            <a href="http://chathera.com/privacy" style="color: #97a2da; text-decoration: underline;" target="_blank">Privacy Policy</a>
                        </p>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>
</body>
</html>
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to
    msg.set_content("Pour voir ce mail, veuillez utiliser un client mail compatible HTML.")
    msg.add_alternative(html_content, subtype="html")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"[send_email] Email HTML envoyé à {to}")
    except Exception as e:
        print(f"[send_email] Erreur d'envoi: {e}")
        raise