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
    subject = "Votre code de vérification - Chathera"
    
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f7f7f7; padding: 40px;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
          <h2 style="color: #333333;">Vérification de votre adresse e-mail</h2>
          <p style="font-size: 16px; color: #555555;">
            Bonjour,
          </p>
          <p style="font-size: 16px; color: #555555;">
            Merci de rejoindre <strong>Chathera</strong> !<br>
            Voici votre code de vérification :
          </p>
          <p style="font-size: 28px; font-weight: bold; color: #4A90E2; text-align: center; letter-spacing: 4px;">
            {code}
          </p>
          <p style="font-size: 14px; color: #999999; margin-top: 30px;">
            Si vous n'avez pas demandé ce code, ignorez simplement cet email.
          </p>
          <p style="font-size: 14px; color: #999999;">
            — L’équipe Chathera
          </p>
        </div>
      </body>
    </html>
    """

    # plain_text en fallback
    plain_text_body = f"""
    Bonjour,

    Merci de rejoindre Chathera !

    Voici votre code de vérification : {code}

    Si vous n'avez pas demandé ce code, ignorez simplement cet email.

    — L’équipe Chathera
    """

    await send_email(to_email, subject, plain_text_body, html_body)



import smtplib
from email.message import EmailMessage
from app.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL


async def send_email_for_password_reset(to: str, subject: str, reset_link: str):
    html_content = f"""\
<!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Réinitialisation de mot de passe</title>
    <style>
      body {{
        margin: 0;
        padding: 0;
        background-color: #f2f4f8;
        font-family: 'Segoe UI', sans-serif;
        color: #333333;
      }}
      .container {{
        max-width: 600px;
        margin: 40px auto;
        background-color: #ffffff;
        border-radius: 8px;
        padding: 40px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
      }}
      .header {{
        text-align: center;
        margin-bottom: 30px;
      }}
      .header img {{
        width: 100px;
        margin-bottom: 10px;
      }}
      .header h1 {{
        margin: 0;
        font-size: 24px;
        color: #1d1d1f;
      }}
      .content {{
        font-size: 16px;
        line-height: 1.6;
      }}
      .button {{
        display: inline-block;
        margin-top: 30px;
        padding: 12px 24px;
        background-color: #7c3aed;
        color: #ffffff;
        text-decoration: none;
        border-radius: 6px;
        font-weight: 600;
      }}
      .footer {{
        margin-top: 50px;
        font-size: 13px;
        text-align: center;
        color: #888888;
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <img src="https://chathera.com/logo.png" alt="Chathera" />
        <h1>Réinitialisation de mot de passe</h1>
      </div>

      <div class="content">
        <p>Bonjour,</p>

        <p>Nous avons reçu une demande de réinitialisation de votre mot de passe.</p>
        <p>Si vous êtes à l’origine de cette demande, cliquez sur le bouton ci-dessous :</p>

        <a href="{reset_link}" class="button">Réinitialiser mon mot de passe</a>

        <p style="margin-top: 40px;">
          Ce lien expirera dans les 30 minutes.<br />
          Si vous n’avez pas fait cette demande, vous pouvez ignorer cet email.
        </p>
      </div>

      <div class="footer">
        © 2025 Chathera • Tous droits réservés<br />
        <a href="https://chathera.com" style="color: #888888; text-decoration: none;">www.chathera.com</a>
      </div>
    </div>
  </body>
</html>
"""

    plain_text = f"""\
Bonjour,

Nous avons reçu une demande de réinitialisation de votre mot de passe.

Cliquez ici pour le réinitialiser : {reset_link}

Ce lien expirera dans 30 minutes. Si vous n’avez pas fait cette demande, ignorez ce message.

L'équipe Chathera.
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to
    msg.set_content(plain_text)
    msg.add_alternative(html_content, subtype="html")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"[send_email] Email de réinitialisation envoyé à {to}")
    except Exception as e:
        print(f"[send_email] Erreur d'envoi: {e}")
        raise

async def send_password_changed_email(to_email: str, user_name: str):
    subject = "Votre mot de passe Chathera a été modifié"
    
    plain_text_body = f"""Bonjour {user_name},

Nous vous confirmons que le mot de passe associé à votre compte Chathera a été modifié avec succès.

Si vous n'êtes pas à l'origine de cette action, veuillez contacter immédiatement notre équipe de support.

Merci pour votre confiance,
L’équipe Chathera
"""

    html_body = f"""\
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <title>Mot de passe modifié</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f6f6f6; padding: 20px;">
  <table width="100%" style="max-width: 600px; margin: auto; background-color: white; border-radius: 8px; overflow: hidden;">
    <tr>
      <td style="background-color: #4F46E5; padding: 20px; color: white; text-align: center;">
        <h2 style="margin: 0;">Chathera</h2>
      </td>
    </tr>
    <tr>
      <td style="padding: 30px;">
        <p>Bonjour <strong>{user_name}</strong>,</p>
        <p>Nous vous confirmons que le mot de passe de votre compte Chathera a été modifié avec succès.</p>
        <p>Si vous n’êtes pas à l’origine de cette action, merci de <a href="mailto:contact@chathera.com">nous contacter immédiatement</a>.</p>
        <p style="margin-top: 40px;">Merci pour votre confiance,<br>L’équipe Chathera</p>
      </td>
    </tr>
    <tr>
      <td style="background-color: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; color: #777;">
        © {2025} Chathera. Tous droits réservés.
      </td>
    </tr>
  </table>
</body>
</html>
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(plain_text_body)
    msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"[send_password_changed_email] Email envoyé à {to_email}")
    except Exception as e:
        print(f"[send_password_changed_email] Erreur lors de l’envoi : {e}")
        raise

async def send_account_created_email(to_email: str, user_first_name: str):
    subject = "Bienvenue sur Chathera ! 🌸"

    # HTML avec nom inséré dynamiquement
    html_body = f"""\
<!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Bienvenue sur Chathera</title>
    <style>
      body {{
        margin: 0;
        padding: 0;
        background-color: #f2f4f8;
        font-family: 'Segoe UI', sans-serif;
        color: #333333;
      }}
      .container {{
        max-width: 600px;
        margin: 40px auto;
        background-color: #ffffff;
        border-radius: 8px;
        padding: 40px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
      }}
      .header {{
        text-align: center;
        margin-bottom: 30px;
      }}
      .header img {{
        width: 100px;
        margin-bottom: 10px;
      }}
      .header h1 {{
        margin: 0;
        font-size: 24px;
        color: #1d1d1f;
      }}
      .content {{
        font-size: 16px;
        line-height: 1.6;
      }}
      .button {{
        display: inline-block;
        margin-top: 30px;
        padding: 12px 24px;
        background-color: #7c3aed;
        color: #ffffff;
        text-decoration: none;
        border-radius: 6px;
        font-weight: 600;
      }}
      .footer {{
        margin-top: 50px;
        font-size: 13px;
        text-align: center;
        color: #888888;
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <img src="https://chathera.com/logo.png" alt="Chathera" />
        <h1>Bienvenue sur Chathera 👋</h1>
      </div>

      <div class="content">
        <p>Bonjour {user_first_name},</p>

        <p>
          Votre compte Chathera a bien été créé. Vous pouvez dès maintenant discuter avec votre compagnon IA personnalisé et vivre une expérience unique, intime et bienveillante.
        </p>

        <p>
          Pour commencer, cliquez sur le bouton ci-dessous :
        </p>

        <a href="https://chathera.com/" class="button">Accéder à Chathera</a>

        <p style="margin-top: 40px;">
          Si vous n’êtes pas à l’origine de cette inscription, vous pouvez ignorer cet email.
        </p>
      </div>

      <div class="footer">
        © 2025 Chathera • Tous droits réservés<br />
        <a href="https://chathera.com" style="color: #888888; text-decoration: none;">www.chathera.com</a>
      </div>
    </div>
  </body>
</html>
"""

    # Version texte brut
    plain_text_body = f"""\
Bonjour {user_first_name},

Votre compte Chathera a bien été créé.
Rendez-vous sur https://chathera.com pour commencer votre expérience.

Merci et bienvenue !
L'équipe Chathera.
"""

    # Envoi
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(plain_text_body)
    msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"[send_email] Email de bienvenue envoyé à {to_email}")
    except Exception as e:
        print(f"[send_email] Erreur d'envoi: {e}")
        raise