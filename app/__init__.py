from flask import Flask, redirect, url_for
from flask_migrate import Migrate

from .config import Config
from .extensions import db, migrate, login_manager, mail

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialisierung der Erweiterungen
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Importiere Blueprints
    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .forms.routes import forms_bp
    
    # Registrierung der Blueprints ohne Präfixe
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(forms_bp)
    
    # Direkte Testroute
    @app.route('/test')
    def test():
        return 'Test erfolgreich!'
    
    # Umleitung von der Wurzel zur Login-Seite
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    return app
