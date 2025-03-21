from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from fpdf import FPDF
import os

from ..extensions import db
from ..models.form import Form

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

        # PDF dem Benutzer anbieten
        return send_file(pdf_output, as_attachment=True)

    return render_template('forms/create_form.html')

@forms_bp.route('/einnahmen', methods=['GET', 'POST'])
@login_required
def einnahmen():
    if request.method == 'POST':
        # Verarbeiten Sie die Daten aus dem Formular
        flash('Daten erfolgreich gespeichert!')
        return render_template('forms/einnahmen.html')  # Rendern der nächsten Seite
    return render_template('forms/einnahmen.html')  # Rendern der nächsten Seite

@forms_bp.route('/ausgaben', methods=['GET', 'POST'])
@login_required
def ausgaben():
    if request.method == 'POST':
        # Verarbeiten Sie die Daten aus dem Formular
        flash('Daten erfolgreich gespeichert!')
        return redirect(url_for('main.dashboard'))  # Weiterleitung zum Dashboard
    return render_template('forms/ausgaben.html')

@forms_bp.route('/submit_form', methods=['POST'])
@login_required
def submit_form():
    # Verarbeiten Sie die Daten aus dem Formular
    flash('Formular erfolgreich abgeschickt!', 'success')
    return redirect(url_for('main.dashboard'))  # Weiterleitung zum Dashboard
