from app import create_app, db
import os


app = create_app()

if __name__ == '__main__':
    # Debug-Ausgabe aller Routen
    print("Registrierte Routen:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")
    
    with app.app_context():
        print("Erstelle Datenbank...")
        db.create_all()  # Stellt sicher, dass die Tabellen angelegt werden
        print("Datenbank wurde erfolgreich erstellt!")

    app.run(debug=True)