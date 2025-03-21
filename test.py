# test_flask.py
from flask import Flask, render_template

app = Flask(__name__, template_folder='app/templates')

@app.route('/')
def index():
    return "Hauptseite funktioniert!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        return render_template('auth/login.html')
    except Exception as e:
        return f"Fehler beim Rendern des Templates: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)

# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()
#         if user and user.check_password(password):
#             login_user(user)
#             return redirect(url_for('main.dashboard'))
#         else:
#             flash('Login fehlgeschlagen. Überprüfen Sie Benutzername und Passwort.')
#     return render_template('auth/login.html')