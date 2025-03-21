import os

basedir = os.path.abspath(os.path.dirname(__file__))
project_dir = os.path.dirname(basedir)  # Übergeordnetes Verzeichnis (Projektroot)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    
    # Absoluter Pfad für die Datenbank
    db_path = os.path.join(project_dir, 'app.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail-Konfiguration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'kk6151850@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'bsts pwnz cdol kuou')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'kk6151850@gmail.com')
