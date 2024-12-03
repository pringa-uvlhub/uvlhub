from app.modules.auth.models import User
from app.modules.profile.models import UserProfile
from core.seeders.BaseSeeder import BaseSeeder


class AuthSeeder(BaseSeeder):

    priority = 1

    def run(self):
        # Crear usuarios sin asociarlos inicialmente a comunidades
        users = [
            User(email='user1@example.com', password='1234'),
            User(email='user2@example.com', password='1234'),
            User(email='user3@example.com', password='1234'),  # Este usuario no tendrá comunidades
        ]

        seeded_users = self.seed(users)

        # Crear perfiles asociados a usuarios (opcional)
        user_profiles = []
        names = [("John", "Doe"), ("Jane", "Doe"), ("Alex", "Smith")]

        for user, name in zip(seeded_users, names):
            profile_data = {
                "user_id": user.id,
                "orcid": "",
                "affiliation": "Some University",
                "name": name[0],
                "surname": name[1],
            }
            user_profile = UserProfile(**profile_data)
            user_profiles.append(user_profile)

        self.seed(user_profiles)
