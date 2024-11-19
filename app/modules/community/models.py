from app import db


class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f'Community<{self.id}>'
