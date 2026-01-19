from models.user import db

class ResidentDiet(db.Model):
    __tablename__ = 'resident_diet'

    id = db.Column(db.Integer, primary_key=True)

    resident_id = db.Column(
        db.Integer,
        db.ForeignKey('resident.id'),
        nullable=False
    )

    diet_id = db.Column(
        db.Integer,
        db.ForeignKey('diet.id'),
        nullable=False
    )

    breakfast = db.Column(db.Boolean, default=False)
    lunch = db.Column(db.Boolean, default=False)
    dinner = db.Column(db.Boolean, default=False)
