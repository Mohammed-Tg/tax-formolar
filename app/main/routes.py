from flask import Blueprint, render_template
from flask_login import login_required, current_user

# Blueprint erstellen
main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('main/dashboard.html', first_name=current_user.first_name, last_name=current_user.last_name)

@main_bp.route('/view_forms')
@login_required
def view_forms():
    # Hole alle Formulare des aktuellen Benutzers aus der Datenbank
    from ..models.form import Form
    forms = Form.query.filter_by(user_id=current_user.id).all()
    return render_template('forms/view_forms.html', forms=forms)
