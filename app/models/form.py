from ..extensions import db

class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    data = db.Column(db.JSON, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Hier könnten weitere Felder für die Steuerformulardaten hinzugefügt werden
    # z.B. Steuer-ID, Steuerklasse, Familienstand, etc.
    
    def __repr__(self):
        return f'<Form {self.title}>'
