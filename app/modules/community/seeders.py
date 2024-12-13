from app.modules.community.models import Community
from app.modules.auth.models import User
from core.seeders.BaseSeeder import BaseSeeder
from datetime import datetime, timezone


class CommunitySeeder(BaseSeeder):

    priority = 2

    def run(self):

        users = User.query.all()

        if not users:
            print("No users found. Make sure AuthSeeder has run before this.")
            return

        user_ids = [user.id for user in users]

        if len(user_ids) < 2:
            print("Not enough users to assign to communities. Check AuthSeeder.")
            return

        communities = [
            Community(
                name="Open Source Enthusiasts",
                description="A community for developers passionate about open source projects.",
                created_by_id=user_ids[0],
                created_at=datetime.now(timezone.utc),
                logo=None,
                admin_by_id=user_ids[0],
                users=[users[0]]
            ),
            Community(
                name="AI Researchers",
                description="A group for discussing advancements in AI and machine learning.",
                created_by_id=user_ids[1],
                created_at=datetime.now(timezone.utc),
                logo=None,
                admin_by_id=user_ids[1],
                users=[users[1]]
            ),
            Community(
                name="Scientific Community",
                description=(
                    "Explore scientific breakthroughs, collaborate on research papers, and connect "
                    "with leading academics in various fields of science and technology."
                ),
                created_by_id=user_ids[0],
                created_at=datetime.now(timezone.utc),
                logo=None,
                admin_by_id=user_ids[0],
                users=[users[0]]
            ),
            Community(
                name="Dark Matter",
                description="A group for discussing advancements in Dark Matter.",
                created_by_id=user_ids[1],
                created_at=datetime.now(timezone.utc),
                logo=None,
                admin_by_id=user_ids[1],
                users=[users[1]]
            ),
            Community(
                name="Biology",
                description="A group for discussing advancements in biology.",
                created_by_id=user_ids[1],
                created_at=datetime.now(timezone.utc),
                logo=None,
                admin_by_id=user_ids[1],
                users=[users[1], users[0]]
            ),
            Community(
                name="Atomic",
                description="A group for discussing advancements in atomic.",
                created_by_id=user_ids[0],
                created_at=datetime.now(timezone.utc),
                logo=None,
                admin_by_id=user_ids[0],
                users=[users[1], users[0]]
            ),
        ]

        self.seed(communities)
