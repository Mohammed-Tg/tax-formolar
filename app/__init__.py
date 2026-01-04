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
    from .models.user import User
    
    # Registrierung der Blueprints ohne Präfixe
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(forms_bp)

    if app.config['DEV_USER_ENABLED']:
        with app.app_context():
            existing_user = User.query.filter_by(username=app.config['DEV_USERNAME']).first()
            if existing_user is None:
                dev_user = User(
                    first_name=app.config['DEV_FIRST_NAME'],
                    last_name=app.config['DEV_LAST_NAME'],
                    username=app.config['DEV_USERNAME'],
                    email=app.config['DEV_EMAIL'],
                    password='',
                    verification_code='DEV000',
                    is_verified=True,
                )
                dev_user.set_password(app.config['DEV_PASSWORD'])
                db.session.add(dev_user)
                db.session.commit()
    
    # Direkte Testroute
    @app.route('/test')
    def test():
        return 'Test erfolgreich!'
    
    # Umleitung von der Wurzel zur Login-Seite
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    return app
