from app import db


class Fakenodo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    creators = db.Column(db.String(255), nullable=False)
    doi = db.Column(db.String(100), nullable=True)