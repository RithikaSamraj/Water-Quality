from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    readings = db.relationship('Reading', backref='user', lazy=True)

class Reading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Sensor Data
    ph = db.Column(db.Float)
    hardness = db.Column(db.Float)
    solids = db.Column(db.Float)
    chloramines = db.Column(db.Float)
    sulfate = db.Column(db.Float)
    conductivity = db.Column(db.Float)
    organic_carbon = db.Column(db.Float)
    trihalomethanes = db.Column(db.Float)
    turbidity = db.Column(db.Float)
    
    # Result
    prediction = db.Column(db.String(20)) # "Potable" or "Not Potable"
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'ph': self.ph,
            'hardness': self.hardness,
            'solids': self.solids,
            'chloramines': self.chloramines,
            'sulfate': self.sulfate,
            'conductivity': self.conductivity,
            'organic_carbon': self.organic_carbon,
            'trihalomethanes': self.trihalomethanes,
            'turbidity': self.turbidity,
            'prediction': self.prediction
        }
