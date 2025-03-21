from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from flask_migrate import Migrate
from fpdf import FPDF
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
import random
import string
# Import der Excel-Export-Funktionen
import pandas as pd
import io
from excel_export import create_multi_sheet_excel, send_form_data_email


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'kk6151850@gmail.com'  # Deine Gmail-Adresse
app.config['MAIL_PASSWORD'] = 'bsts pwnz cdol kuou'      # Verwende das generierte App-Passwort
app.config['MAIL_DEFAULT_SENDER'] = 'kk6151850@gmail.com'
mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(300), nullable=False, unique=True)  # Sicherstellen, dass der Username einzigartig ist
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    verification_code = db.Column(db.String(6), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)



def send_verification_email(email, verification_code):
    msg = Message('Verifizierungscode',
                  sender='kk6151850@gmail.com',
                  recipients=[email])
    msg.body = f'Ihr Verifizierungscode lautet: {verification_code}'
    mail.send(msg)

def send_username_email(email, username):
    msg = Message('Ihr Benutzername',
                  sender='kk6151850@gmail.com',
                  recipients=[email])
    msg.body = f'Ihr Benutzername lautet: {username}'
    mail.send(msg)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')

        # Generiere einen Verifizierungscode
        verification_code = ''.join(random.choices(string.digits, k=6))

        # Erstelle einen neuen Benutzer
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=f"{first_name.lower()}.{last_name.lower()}",  # Generieren des Benutzernamens
            email=email,
            password=hashed_password,
            verification_code=verification_code  # Setzen des Verifizierungscodes
        )

        # Überprüfen, ob die E-Mail-Adresse bereits existiert
        if User.query.filter_by(email=new_user.email).first() is not None:
            flash('E-Mail-Adresse ist bereits registriert. Bitte melden Sie sich an.', 'error')
            return redirect(url_for('login'))

        # Benutzer in die Datenbank einfügen
        db.session.add(new_user)
        db.session.commit()

        # Verifizierungscode senden
        send_verification_email(email, verification_code)

        flash('Ein Verifizierungscode wurde an Ihre E-Mail-Adresse gesendet. Bitte überprüfen Sie Ihren Posteingang.')
        return redirect(url_for('verify', email=email))

    return render_template('register.html')

@app.route('/verify', methods=['GET', 'POST'])
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
            
            return redirect(url_for('login'))
        else:
            flash('Ungültiger Verifizierungscode oder E-Mail.')
    
    email = request.args.get('email')  # E-Mail aus der Anfrage holen
    return render_template('verify.html', email=email)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            # Formular-Daten zurücksetzen, wenn ein neuer Benutzer sich anmeldet
            session.pop('form_data', None)
            return redirect(url_for('dashboard'))
        else:
            
            flash('Login fehlgeschlagen. Überprüfen Sie Benutzername und Passwort.')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Formular-Daten zurücksetzen, wenn der Benutzer zum Dashboard zurückkehrt
    session.pop('form_data', None)
    return render_template('dashboard.html', first_name=current_user.first_name, last_name=current_user.last_name)

class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@app.route('/create_form', methods=['GET', 'POST'])
@login_required
def create_form():
    if request.method == 'POST':
        # Formular-Daten sammeln
        form_data = {
            'name': request.form['name'],
            'surname': request.form['surname'],
            'tax_id': request.form['tax_id'],
            'tax_class': request.form['tax_class'],
            'family_status': request.form['family_status'],
            'has_children': request.form.get('children', 'no'),
            'num_children': request.form.get('num_children', 0)
        }

        # In der Session speichern
        session['form_data'] = {'stammdaten': form_data}
        
        # PDF erstellen (optional)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(200, 10, 'Formular Zusammenfassung - Stammdaten', ln=True, align='C')

        # PDF-Inhalt hinzufügen
        pdf.set_font('Arial', '', 12)
        pdf.cell(200, 10, f"Name: {form_data['name']}", ln=True)
        pdf.cell(200, 10, f"Nachname: {form_data['surname']}", ln=True)
        pdf.cell(200, 10, f"Steuer-ID: {form_data['tax_id']}", ln=True)
        pdf.cell(200, 10, f"Steuerklasse: {form_data['tax_class']}", ln=True)
        pdf.cell(200, 10, f"Familienstand: {form_data['family_status']}", ln=True)
        pdf.cell(200, 10, f"Haben Sie Kindern?: {'Ja' if form_data['has_children'] == 'yes' else 'Nein'}", ln=True)

        if form_data['has_children'] == 'yes':
            pdf.cell(200, 10, f"Anzahl der Kindern: {form_data['num_children']}", ln=True)

        # PDF speichern
        pdf_output = f"{form_data['name']}_{form_data['surname']}_stammdaten.pdf"
        pdf.output(pdf_output)

        flash('Stammdaten erfolgreich gespeichert!', 'success')
        
        # Zur nächsten Seite weiterleiten
        return redirect(url_for('einnahmen'))

    return render_template('create_form.html')
# Neue Route für die nächste Seite
@app.route('/einnahmen', methods=['GET', 'POST'])
@login_required
def einnahmen():
    if request.method == 'POST':
        # Formular-Daten sammeln
        einnahmen_data = request.form.to_dict()
        
        # Zur bestehenden Session hinzufügen
        form_data = session.get('form_data', {})
        form_data['einnahmen'] = einnahmen_data
        session['form_data'] = form_data
        
        flash('Einnahmen erfolgreich gespeichert!', 'success')
        print("Weiterleitung zu /ausgaben erfolgt")
        return redirect(url_for('ausgaben'))
    
    return render_template('einnahmen.html')

@app.route('/ausgaben', methods=['GET', 'POST'])
@login_required
def ausgaben():
    if request.method == 'POST':
        # Formular-Daten sammeln
        ausgaben_data = request.form.to_dict()
        
        # Zur bestehenden Session hinzufügen
        form_data = session.get('form_data', {})
        form_data['ausgaben'] = ausgaben_data
        session['form_data'] = form_data
        
        # Benutzerinformationen sammeln
        # user_info = {
        #     'first_name': current_user.first_name,
        #     'last_name': current_user.last_name,
        #     'email': current_user.email
        # }
        
        # # Excel-Datei mit mehreren Sheets erstellen und per E-Mail senden
        # admin_email = app.config['MAIL_USERNAME']
        # send_form_data_email(form_data, user_info, mail, admin_email)
        
        flash('Formular erfolgreich abgeschickt und an den Administrator gesendet!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('ausgaben.html')

# Neue Route für das Abschicken des Formulars
@app.route('/submit_form', methods=['POST'])
@login_required
def submit_form():
    # Formular-Daten aus der Session holen
    form_data = session.get('form_data', {})
    
    # Aktuelle Formulardaten hinzufügen
    current_form_data = request.form.to_dict()
    form_data['final'] = current_form_data
    
    # Benutzerinformationen sammeln
    user_info = {
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'email': current_user.email
    }
    
    # Excel-Datei mit mehreren Sheets erstellen und per E-Mail senden
    admin_email = app.config['MAIL_USERNAME']
    send_form_data_email(form_data, user_info, mail, admin_email)
    
    # Formular-Daten zurücksetzen
    session.pop('form_data', None)
    
    flash('Formular erfolgreich abgeschickt und an den Administrator gesendet!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/view_forms')
@login_required
def view_forms():
    # Hole alle Formulare des aktuellen Benutzers aus der Datenbank
    forms = Form.query.filter_by(user_id=current_user.id).all()
    return render_template('view_forms.html', forms=forms)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Erstellt die Tabellen, wenn sie noch nicht existieren
    app.run(debug=True)