from app import db
from datetime import datetime, timezone


class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    logo = db.Column(db.String(255), nullable=True, default='img/community/community-default.svg')

    def __repr__(self):
        return f'Community<{self.id}>'
