from app.modules.auth.models import User
from core.repositories.BaseRepository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def create(self, commit: bool = True, **kwargs):
        password = kwargs.pop("password")
        instance = self.model(**kwargs)
        instance.set_password(password)
        self.session.add(instance)
        if commit:
            self.session.commit()
        else:
            self.session.flush()
        return instance

    def get_by_email(self, email: str):
        return self.model.query.filter_by(email=email).first()

    def count_total_users(self):
        return self.model.query.count()

    def count_total_admin_users(self):
        return self.model.query.filter_by(is_admin=True).count()
