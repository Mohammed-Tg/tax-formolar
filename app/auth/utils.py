from flask_mail import Message
from ..extensions import mail

def send_verification_email(email, verification_code):
    """
    Sendet einen Verifizierungscode an die angegebene E-Mail-Adresse.
    """
    msg = Message('Verifizierungscode',
                  sender='kk6151850@gmail.com',
                  recipients=[email])
    msg.body = f'Ihr Verifizierungscode lautet: {verification_code}'
    mail.send(msg)

def send_username_email(email, username):
    """
    Sendet den Benutzernamen an die angegebene E-Mail-Adresse.
    """
    msg = Message('Ihr Benutzername',
                  sender='kk6151850@gmail.com',
                  recipients=[email])
    msg.body = f'Ihr Benutzername lautet: {username}'
    mail.send(msg)
