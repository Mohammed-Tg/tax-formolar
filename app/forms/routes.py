import re

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, session, current_app
from flask_login import login_required, current_user
from ..extensions import db, mail
from ..models.form import Form
from ..models.user_profile import UserProfile
from excel_export import create_multi_sheet_excel, send_form_data_email

# Blueprint erstellen
forms_bp = Blueprint('forms', __name__)

def is_valid_tax_id(tax_id: str) -> bool:
    if not re.fullmatch(r"\d{11}", tax_id or ""):
        return False
    digits = [int(char) for char in tax_id]
    product = 10
    for digit in digits[:-1]:
        sum_value = (digit + product) % 10
        if sum_value == 0:
            sum_value = 10
        product = (2 * sum_value) % 11
    check_digit = (11 - product) % 10
    return check_digit == digits[-1]

@forms_bp.route('/create_form', methods=['GET', 'POST'])
@login_required
def create_form():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        tax_id = request.form['tax_id']
        tax_class = request.form['tax_class']
        family_status = request.form['family_status']
        has_children = request.form.get('children', 'no')
        num_children = request.form.get('num_children', 0)
        remarks = request.form.get('remarks', '')

        if not is_valid_tax_id(tax_id):
            flash('Bitte eine gültige 11-stellige Steuer-ID eingeben.', 'error')
            return render_template('forms/create_form.html', form_data=request.form)

        # Formular in der Datenbank speichern
        form = Form(
            title=f"Steuerformular für {name} {surname}",
            description=f"Steuer-ID: {tax_id}, Steuerklasse: {tax_class}",
            user_id=current_user.id
        )
        db.session.add(form)

        profile_data = {
            'name': name,
            'surname': surname,
            'tax_id': tax_id,
            'tax_class': tax_class,
            'family_status': family_status,
            'children': has_children,
            'num_children': num_children,
            'remarks': remarks,
        }
        profile = UserProfile.query.filter_by(user_id=current_user.id).first()
        if profile is None:
            profile = UserProfile(user_id=current_user.id, data=profile_data)
            db.session.add(profile)
        else:
            profile.data = profile_data

        db.session.commit()

        form_data = session.get('form_data', {})
        form_data['stammdaten'] = {
            'name': name,
            'surname': surname,
            'tax_id': tax_id,
            'tax_class': tax_class,
            'family_status': family_status,
            'has_children': has_children,
            'num_children': num_children,
            'remarks': remarks,
        }
        session['form_data'] = form_data
        return redirect(url_for('forms.einnahmen'))

    session_data = session.get('form_data', {}).get('stammdaten', {})
    if session_data:
        form_data = dict(session_data)
        form_data['children'] = form_data.get('children', form_data.get('has_children'))
    else:
        profile = UserProfile.query.filter_by(user_id=current_user.id).first()
        form_data = dict(profile.data) if profile and profile.data else {}
    return render_template('forms/create_form.html', form_data=form_data)

@forms_bp.route('/einnahmen', methods=['GET', 'POST'])
@login_required
def einnahmen():
    if request.method == 'POST':
        form_data = session.get('form_data', {})
        form_data['einnahmen'] = request.form.to_dict()
        session['form_data'] = form_data
        flash('Daten erfolgreich gespeichert!')
        return redirect(url_for('forms.ausgaben'))
    return render_template('forms/einnahmen.html')  # Rendern der nächsten Seite

@forms_bp.route('/ausgaben', methods=['GET', 'POST'])
@login_required
def ausgaben():
    return render_template('forms/ausgaben.html')

@forms_bp.route('/submit_form', methods=['POST'])
@login_required
def submit_form():
    form_data = session.get('form_data', {})
    form_data['ausgaben'] = request.form.to_dict()
    session['form_data'] = form_data

    user_info = {
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'email': current_user.email,
    }
    admin_email = current_app.config['MAIL_USERNAME']
    send_form_data_email(form_data, user_info, mail, admin_email)
    session.pop('form_data', None)

    flash('Formular erfolgreich abgeschickt!', 'success')
    return redirect(url_for('main.dashboard'))  # Weiterleitung zum Dashboard

@forms_bp.route('/export_excel', methods=['POST'])
@login_required
def export_excel():
    form_data = session.get('form_data', {})
    current_form_data = request.form.to_dict()
    if current_form_data:
        form_data['ausgaben'] = current_form_data
        session['form_data'] = form_data
    if not form_data:
        flash('Keine Formulardaten für den Excel-Export gefunden.', 'error')
        return redirect(url_for('main.dashboard'))

    excel_file = create_multi_sheet_excel(form_data)
    filename = f"formular_{current_user.first_name}_{current_user.last_name}.xlsx"
    return send_file(
        excel_file,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
