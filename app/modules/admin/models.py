from app import db


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f'Admin<{self.id}>'
