from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Form

forms_bp = Blueprint('forms', __name__)

@forms_bp.route('/create_form', methods=['GET', 'POST'])
@login_required
def create_form():
    if request.method == 'POST':
        form = Form(
            user_id=current_user.id,
            name=request.form['name'],
            surname=request.form['surname'],
            tax_id=request.form['tax_id'],
            tax_class=request.form['tax_class'],
            family_status=request.form['family_status'],
            has_children=request.form.get('children', 'no'),
            num_children=int(request.form.get('num_children', 0))
        )

        db.session.add(form)
        db.session.commit()
        flash('Formular gespeichert!')

        return redirect(url_for('forms.view_forms'))

    return render_template('create_form.html')

@forms_bp.route('/view_forms')
@login_required
def view_forms():
    forms = Form.query.filter_by(user_id=current_user.id).all()
    return render_template('view_forms.html', forms=forms)

@forms_bp.route('/view_form/<int:form_id>')
@login_required
def view_form(form_id):
    form = Form.query.get_or_404(form_id)
    return render_template('view_form.html', form=form)
