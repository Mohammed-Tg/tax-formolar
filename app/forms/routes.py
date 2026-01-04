from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, session, current_app
from flask_login import login_required, current_user
from fpdf import FPDF

from ..extensions import db, mail
from ..models.form import Form
from excel_export import create_multi_sheet_excel, send_form_data_email

# Blueprint erstellen
forms_bp = Blueprint('forms', __name__)

@forms_bp.route('/create_form', methods=['GET', 'POST'])
@login_required
def create_form():
    if request.method == 'POST':
        # Formular-Daten sammeln
        name = request.form['name']
        surname = request.form['surname']
        tax_id = request.form['tax_id']
        tax_class = request.form['tax_class']
        family_status = request.form['family_status']
        has_children = request.form.get('children', 'no')
        num_children = request.form.get('num_children', 0)

        # PDF erstellen
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(200, 10, 'Formular Zusammenfassung', ln=True, align='C')

        # PDF-Inhalt hinzufügen
        pdf.set_font('Arial', '', 12)
        pdf.cell(200, 10, f"Name: {name}", ln=True)
        pdf.cell(200, 10, f"Nachname: {surname}", ln=True)
        pdf.cell(200, 10, f"Steuer-ID: {tax_id}", ln=True)
        pdf.cell(200, 10, f"Steuerklasse: {tax_class}", ln=True)
        pdf.cell(200, 10, f"Familienstand: {family_status}", ln=True)
        pdf.cell(200, 10, f"Haben Sie Kindern?: {'Ja' if has_children == 'yes' else 'Nein'}", ln=True)

        if has_children == 'yes':
            pdf.cell(200, 10, f"Anzahl der Kindern: {num_children}", ln=True)

        # PDF speichern
        pdf_output = f"{name}_{surname}_form.pdf"
        pdf.output(pdf_output)

        # Formular in der Datenbank speichern
        form = Form(
            title=f"Steuerformular für {name} {surname}",
            description=f"Steuer-ID: {tax_id}, Steuerklasse: {tax_class}",
            user_id=current_user.id
        )
        db.session.add(form)
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
        }
        session['form_data'] = form_data

        # PDF dem Benutzer anbieten
        return send_file(pdf_output, as_attachment=True)

    return render_template('forms/create_form.html')

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
