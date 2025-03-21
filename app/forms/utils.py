from fpdf import FPDF
import pandas as pd
import io
from flask_mail import Message

def create_pdf_from_form_data(form_data, user_info):
    """
    Erstellt eine PDF-Datei aus den Formulardaten
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, 'Steuerformular Zusammenfassung', ln=True, align='C')
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(200, 10, f"Name: {user_info['first_name']} {user_info['last_name']}", ln=True)
    pdf.cell(200, 10, f"E-Mail: {user_info['email']}", ln=True)
    
    # Weitere Formulardaten hinzufügen
    if 'stammdaten' in form_data:
        pdf.cell(200, 10, "Stammdaten:", ln=True)
        for key, value in form_data['stammdaten'].items():
            pdf.cell(200, 10, f"{key}: {value}", ln=True)
    
    if 'einnahmen' in form_data:
        pdf.cell(200, 10, "Einnahmen:", ln=True)
        for key, value in form_data['einnahmen'].items():
            pdf.cell(200, 10, f"{key}: {value}", ln=True)
    
    if 'ausgaben' in form_data:
        pdf.cell(200, 10, "Ausgaben:", ln=True)
        for key, value in form_data['ausgaben'].items():
            pdf.cell(200, 10, f"{key}: {value}", ln=True)
    
    return pdf

def create_multi_sheet_excel_with_format(template_path, form_data_dict):
    """
    Erstellt eine Excel-Datei mit mehreren Sheets basierend auf einer Vorlage
    """
    # Originaldatei laden
    template_xls = pd.ExcelFile(template_path, engine='openpyxl')
    
    # Neuen Byte-Stream für das neue Excel-Dokument erstellen
    excel_file = io.BytesIO()
    
    # Mit der OpenPyXL-Engine schreiben, um Formatierungen beizubehalten
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        for sheet_name in template_xls.sheet_names:
            # Original-Sheet einlesen
            df_template = template_xls.parse(sheet_name, header=None)
            
            # Falls Daten für dieses Sheet existieren, sie einfügen
            if sheet_name in form_data_dict:
                df_data = pd.DataFrame([form_data_dict[sheet_name]])
                for col_idx, col_data in enumerate(df_data.values[0]):
                    df_template.iloc[1, col_idx] = col_data  # Werte in die zweite Zeile setzen
            
            # Sheet speichern
            df_template.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
    
    # Datei zurücksetzen
    excel_file.seek(0)
    return excel_file

def send_form_data_email_with_template(form_data_dict, user_info, mail_app, admin_email, template_path=None):
    """
    Sendet die Formulardaten per E-Mail, optional mit einer vordefinierten Excel-Vorlage
    """
    # Wenn eine Vorlage angegeben wurde und der Excel-Teil aktiviert werden soll
    if template_path is not None:
        # Excel-Datei mit Vorlage erstellen
        excel_file = create_multi_sheet_excel_with_format(template_path, form_data_dict)
        
        msg = Message(
            f'Neues Steuerformular von {user_info["first_name"]} {user_info["last_name"]}',
            sender=admin_email,
            recipients=[admin_email]
        )
        msg.body = f"""
        Ein neues Steuerformular wurde von {user_info['first_name']} {user_info['last_name']} ({user_info['email']}) eingereicht.
        Die Daten wurden in der Originalvorlage gespeichert.
        """
        
        msg.attach(
            f"formular_{user_info['first_name']}_{user_info['last_name']}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            excel_file.getvalue()
        )
        
        mail_app.send(msg)
    else:
        # Einfache E-Mail senden mit Formulardaten
        msg = Message(
            f'Neues Steuerformular von {user_info["first_name"]} {user_info["last_name"]}',
            sender=admin_email,
            recipients=[admin_email]
        )
        msg.body = f"""
        Ein neues Steuerformular wurde von {user_info['first_name']} {user_info['last_name']} ({user_info['email']}) eingereicht.
        
        Formular-Daten:
        {form_data_dict}
        """
        
        mail_app.send(msg)
