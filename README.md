# Tax-Formolar - Steuerformular-Anwendung

Diese Anwendung ermöglicht es Benutzern, Steuerformulare online auszufüllen und zu verwalten.

## Projektstruktur

Die Anwendung ist nach dem Blueprint-Muster strukturiert und verwendet eine Application Factory für bessere Modularität und Testbarkeit.

```
tax-formolar/
├── app/                      # Hauptanwendungspaket
│   ├── __init__.py           # Application Factory
│   ├── config.py             # Konfigurationseinstellungen
│   ├── extensions.py         # Flask-Erweiterungen (SQLAlchemy, Login, Mail)
│   ├── models/               # Datenbankmodelle
│   │   ├── __init__.py
│   │   ├── user.py           # User-Modell
│   │   └── form.py           # Formular-Modell
│   ├── auth/                 # Authentifizierungs-Blueprint
│   │   ├── __init__.py
│   │   ├── routes.py         # Auth-Routen (Login, Register, Verify)
│   │   └── utils.py          # Auth-Hilfsfunktionen (E-Mail-Versand)
│   ├── main/                 # Haupt-Blueprint
│   │   ├── __init__.py
│   │   └── routes.py         # Hauptrouten (Dashboard, Home)
│   ├── forms/                # Steuerformular-Blueprint
│   │   ├── __init__.py
│   │   ├── routes.py         # Formular-Routen
│   │   └── utils.py          # Formular-Hilfsfunktionen (PDF, Excel)
│   ├── templates/            # HTML-Templates
│   └── static/               # Statische Dateien
├── migrations/               # Datenbank-Migrationen
├── instance/                 # Instanz-spezifische Daten
├── tests/                    # Tests
├── .env                      # Umgebungsvariablen (nicht im Git)
├── .gitignore                # Git-Ignore-Datei
├── requirements.txt          # Abhängigkeiten
└── run.py                    # Anwendungsstarter
```

## Installation

1. Virtuelle Umgebung erstellen und aktivieren:
```
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
```

2. Abhängigkeiten installieren:
```
pip install -r requirements.txt
```

3. Umgebungsvariablen konfigurieren:
Kopieren Sie die `.env`-Datei und passen Sie die Werte an Ihre Umgebung an.

4. Datenbank initialisieren:
```
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. Anwendung starten:
```
python run.py
```

## Funktionen

- Benutzerregistrierung und -authentifizierung
- E-Mail-Verifizierung
- Steuerformulare erstellen und verwalten
- PDF-Generierung
- Excel-Export

## Technologien

- Flask
- SQLAlchemy
- Flask-Login
- Flask-Mail
- FPDF
- Pandas
