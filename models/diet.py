from models.user import db

class Diet(db.Model):
    __tablename__ = 'diet'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)

    is_basic = db.Column(db.Boolean, default=False)
    is_light = db.Column(db.Boolean, default=False)
    is_diabetes = db.Column(db.Boolean, default=False)
    is_milk_free = db.Column(db.Boolean, default=False)
    is_mix = db.Column(db.Boolean, default=False)
    is_peg = db.Column(db.Boolean, default=False)
    is_restrictive = db.Column(db.Boolean, default=False)

    active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.String(150), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)