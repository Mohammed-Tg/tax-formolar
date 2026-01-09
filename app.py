from app import create_app


app = create_app()

if __name__ == '__main__':
     # Erstellt die Tabellen, wenn sie noch nicht existieren
    app.run(debug=True)