from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from app import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
import random, string

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='sha256')

        verification_code = ''.join(random.choices(string.digits, k=6))
        new_user = User(email=email, password=password, verification_code=verification_code)

        db.session.add(new_user)
        db.session.commit()
        flash('Registrierung erfolgreich!')

        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        flash('Falsche Anmeldedaten')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
