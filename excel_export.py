import pandas as pd
import io
from flask_mail import Message

def create_multi_sheet_excel(form_data_dict):
    """
    Erstellt eine Excel-Datei mit mehreren Sheets aus den Formulardaten
    
    Args:
        form_data_dict (dict): Dictionary mit Seitennamen als Schlüssel und Formulardaten als Werte
        
    Returns:
        BytesIO: Excel-Datei als Byte-Stream
    """
    # Excel-Datei in einen Byte-Stream schreiben
    excel_file = io.BytesIO()
    
    # Excel-Writer erstellen
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Für jede Seite ein eigenes Sheet erstellen
        for sheet_name, data in form_data_dict.items():
            # Pandas DataFrame aus den Formulardaten erstellen
            df = pd.DataFrame([data])
            # In das entsprechende Sheet schreiben
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # Zurück zum Anfang des Streams springen
    excel_file.seek(0)
    
    return excel_file

def send_form_data_email(form_data_dict, user_info, mail_app, admin_email):
    """
    Sendet die Formulardaten als Excel-Datei mit mehreren Sheets per E-Mail an den Administrator
    
    Args:
        form_data_dict (dict): Dictionary mit Seitennamen als Schlüssel und Formulardaten als Werte
        user_info (dict): Informationen über den Benutzer (Name, E-Mail)
        mail_app: Die Mail-Instanz der Flask-Anwendung
        admin_email (str): Die E-Mail-Adresse des Administrators
    """
    # Excel-Datei mit mehreren Sheets erstellen
    excel_file = create_multi_sheet_excel(form_data_dict)
    
    # E-Mail erstellen
    msg = Message(
        f'Neues Steuerformular von {user_info["first_name"]} {user_info["last_name"]}',
        sender=admin_email,
        recipients=[admin_email]
    )
    
    msg.body = f"""
    Ein neues Steuerformular wurde von {user_info['first_name']} {user_info['last_name']} ({user_info['email']}) eingereicht.
    
    Die Formulardaten finden Sie in der angehängten Excel-Datei mit separaten Sheets für jede Formularseite.
    """
    
    # Excel-Datei als Anhang hinzufügen
    msg.attach(
        f"formular_{user_info['first_name']}_{user_info['last_name']}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        excel_file.getvalue()
    )
    
    # E-Mail senden
    mail_app.send(msg)

# Für Abwärtskompatibilität die alte Funktion beibehalten
def create_excel_from_form_data(form_data):
    """
    Erstellt eine Excel-Datei aus den Formulardaten (für Abwärtskompatibilität)
    
    Args:
        form_data (dict): Die Formulardaten
        
    Returns:
        BytesIO: Excel-Datei als Byte-Stream
    """
    # Pandas DataFrame aus den Formulardaten erstellen
    df = pd.DataFrame([form_data])
    
    # Excel-Datei in einen Byte-Stream schreiben
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False, engine='openpyxl')
    excel_file.seek(0)
    
    return excel_file
