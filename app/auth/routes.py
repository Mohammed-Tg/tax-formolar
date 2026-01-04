from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
import random
import string

from ..models.user import User
from ..extensions import db, login_manager
from .utils import send_verification_email, send_username_email

# Blueprint erstellen
auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/')
def home():
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        # Generiere einen Verifizierungscode
        verification_code = ''.join(random.choices(string.digits, k=6))

        # Erstelle einen neuen Benutzer
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=f"{first_name.lower()}.{last_name.lower()}",  # Generieren des Benutzernamens
            email=email,
            password='',
            verification_code=verification_code  # Setzen des Verifizierungscodes
        )
        new_user.set_password(password)

        # Überprüfen, ob die E-Mail-Adresse bereits existiert
        if User.query.filter_by(email=new_user.email).first() is not None:
            flash('E-Mail-Adresse ist bereits registriert. Bitte melden Sie sich an.', 'error')
            return redirect(url_for('auth.login'))

        # Benutzer in die Datenbank einfügen
        db.session.add(new_user)
        db.session.commit()

        # Verifizierungscode senden
        send_verification_email(email, verification_code)

        flash('Ein Verifizierungscode wurde an Ihre E-Mail-Adresse gesendet. Bitte überprüfen Sie Ihren Posteingang.')
        return redirect(url_for('auth.verify', email=email))

    return render_template('auth/register.html')

@auth_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        email = request.form['email']
        verification_code = request.form['verification_code']

        # Benutzer anhand der E-Mail finden
        user = User.query.filter_by(email=email).first()
        if user and user.verification_code == verification_code:
            user.is_verified = True
            # Setze den verifizierung_code nicht auf None, sondern auf einen leeren String, wenn gewünscht
            user.verification_code = ''  # Oder du könntest den Code behalten, aber in der Logik die Verwendung anpassen
            db.session.commit()
            flash('E-Mail erfolgreich verifiziert! Ihr Benutzername wird Ihnen per E-Mail zugesendet.')

            # Senden des Benutzernamens
            send_username_email(user.email, user.username)
            
            return redirect(url_for('auth.login'))
        else:
            flash('Ungültiger Verifizierungscode oder E-Mail.')
    
    email = request.args.get('email')  # E-Mail aus der Anfrage holen
    return render_template('auth/verify.html', email=email)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login fehlgeschlagen. Überprüfen Sie Benutzername und Passwort.')
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
