from datetime import datetime
from models.user import db

class Resident(db.Model):
    __tablename__ = 'resident'

    id = db.Column(db.Integer, primary_key=True)

    last_name = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)

    room_number = db.Column(db.Text)
    floor = db.Column(db.Integer)

    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_hospital = db.Column(db.Boolean, default=False, nullable=False)
    is_pass = db.Column(db.Boolean, default=False, nullable=False)

    # DIETA I WYKRZYKNIK
    has_diet = db.Column(db.Boolean, default=False, nullable=False)
    needs_attention = db.Column(db.Boolean, default=True, nullable=False)

    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
