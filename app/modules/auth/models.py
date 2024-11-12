from datetime import datetime, timedelta, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    data_sets = db.relationship('DataSet', backref='user', lazy=True)
    profile = db.relationship('UserProfile', backref='user', uselist=False)
    
    reset_token = db.Column(db.String(256), nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if 'password' in kwargs:
            self.set_password(kwargs['password'])

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def temp_folder(self) -> str:
        from app.modules.auth.services import AuthenticationService
        return AuthenticationService().temp_folder_by_user(self)
    
    def generate_reset_token(self, expires_minutes=15):
        s = Serializer(current_app.config['SECRET_KEY'])
        token = s.dumps({'user_id': self.id})
        self.reset_token = token
        self.reset_token_expiration = datetime.now() + timedelta(minutes=expires_minutes)
        db.session.commit()
        return token

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=1800)['user_id']  # Aquí se define la expiración en segundos
        except Exception:
            return None
        return User.query.get(user_id)