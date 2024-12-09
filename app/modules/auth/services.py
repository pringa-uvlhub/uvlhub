import os
from flask_login import login_user
from flask_login import current_user

from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Message
from flask import url_for, render_template
from app import mail
from app.modules.auth.models import User
from app.modules.auth.repositories import UserRepository
from app.modules.profile.models import UserProfile
from app.modules.profile.repositories import UserProfileRepository
from core.configuration.configuration import uploads_folder_name
from core.services.BaseService import BaseService


class AuthenticationService(BaseService):
    def __init__(self):
        super().__init__(UserRepository())
        self.user_profile_repository = UserProfileRepository()
        self.serializer = URLSafeTimedSerializer('secret_key')

    def login(self, email, password, remember=True):
        user = self.repository.get_by_email(email)
        if user is not None and user.check_password(password):
            login_user(user, remember=remember)
            return True
        return False

    def send_verification_email(self, user_data):
        # Almacenar los datos del usuario en el token
        token = self.serializer.dumps(user_data, salt='email-confirmation-salt')
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        html = render_template('auth/email_verification.html', confirm_url=confirm_url, user_name=user_data['name'])
        msg = Message(subject="Please verify your email", recipients=[user_data['email']], html=html)
        mail.send(msg)

    def confirm_token(self, token, expiration=3600):  # 1 hora
        try:
            email = self.serializer.loads(token, salt='email-confirmation-salt', max_age=expiration)
        except SignatureExpired:
            # El token ha expirado
            return False
        except BadSignature:
            # El token es inválido (posible manipulación)
            return False
        return email

    def is_email_available(self, email: str) -> bool:
        return self.repository.get_by_email(email) is None

    def create_with_profile(self, **kwargs):
        try:
            email = kwargs.pop("email", None)
            password = kwargs.pop("password", None)
            name = kwargs.pop("name", None)
            surname = kwargs.pop("surname", None)

            if not email:
                raise ValueError("Email is required.")
            if not password:
                raise ValueError("Password is required.")
            if not name:
                raise ValueError("Name is required.")
            if not surname:
                raise ValueError("Surname is required.")

            user_data = {
                "email": email,
                "password": password
            }

            profile_data = {
                "name": name,
                "surname": surname,
            }

            user = self.create(commit=False, **user_data)
            profile_data["user_id"] = user.id
            self.user_profile_repository.create(**profile_data)
            self.repository.session.commit()
        except Exception as exc:
            self.repository.session.rollback()
            raise exc
        return user

    def update_profile(self, user_profile_id, form):
        if form.validate():
            updated_instance = self.update(user_profile_id, **form.data)
            return updated_instance, None

        return None, form.errors

    def get_authenticated_user(self) -> User | None:
        if current_user.is_authenticated:
            return current_user
        return None

    def get_authenticated_user_profile(self) -> UserProfile | None:
        if current_user.is_authenticated:
            return current_user.profile
        return None

    def temp_folder_by_user(self, user: User) -> str:
        return os.path.join(uploads_folder_name(), "temp", str(user.id))


def send_reset_email(to_email, reset_url):
    msg = Message("Restablece tu contraseña", recipients=[to_email])
    msg.body = f"Para restablecer tu contraseña, sigue este enlace: {reset_url}"
    mail.send(msg)
