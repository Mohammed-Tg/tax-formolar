import io

from flask import Blueprint, render_template, send_file
from flask_login import login_required, current_user

# Blueprint erstellen
main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    from ..models.form import Form

    forms = Form.query.filter_by(user_id=current_user.id).order_by(Form.id.desc()).all()
    return render_template(
        'main/dashboard.html',
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        forms=forms,
    )

@main_bp.route('/view_forms')
@login_required
def view_forms():
    # Hole alle Formulare des aktuellen Benutzers aus der Datenbank
    from ..models.form import Form
    forms = Form.query.filter_by(user_id=current_user.id).all()
    return render_template('forms/view_forms.html', forms=forms)

@main_bp.route('/forms/<int:form_id>/pdf')
@login_required
def download_form_pdf(form_id):
    from ..forms.utils import create_pdf_from_form_data
    from ..models.form import Form

    form = Form.query.filter_by(id=form_id, user_id=current_user.id).first_or_404()
    form_data = form.data or {}
    user_info = {
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'email': current_user.email,
    }
    pdf = create_pdf_from_form_data(form_data, user_info)
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return send_file(
        io.BytesIO(pdf_bytes),
        as_attachment=True,
        download_name=f"antrag_{form.id}.pdf",
        mimetype="application/pdf",
    )
