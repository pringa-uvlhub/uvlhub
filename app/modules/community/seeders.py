from app.modules.community.models import Community
from app.modules.auth.models import User
from core.seeders.BaseSeeder import BaseSeeder
from datetime import datetime, timezone

class CommunitySeeder(BaseSeeder):

    priority = 2  # Prioridad menor que AuthSeeder si los usuarios ya deben existir.

    def run(self):

        # Busca usuarios existentes para asociarlos con comunidades.
        users = User.query.all()

        if not users:
            print("No users found. Make sure AuthSeeder has run before this.")
            return

        # Mapear usuarios a IDs
        user_ids = [user.id for user in users]

        # Si no hay suficientes usuarios, usa un ID ficticio o maneja la excepción.
        if len(user_ids) < 2:
            print("Not enough users to assign to communities. Check AuthSeeder.")
            return

        # Datos de ejemplo para comunidades.
        communities = [
            Community(
                name="Open Source Enthusiasts",
                description="A community for developers passionate about open source projects.",
                created_by_id=user_ids[0],  # Asigna al primer usuario como creador.
                created_at=datetime.now(timezone.utc),
                logo=None  # Puedes agregar un logo específico
            ),
            Community(
                name="AI Researchers",
                description="A group for discussing advancements in AI and machine learning.",
                created_by_id=user_ids[1],  # Usa otro usuario si está disponible.
                created_at=datetime.now(timezone.utc),
                logo=None  # Otro logo específico
            ),
            Community(
                name="Scientific Community",
                description="Explore scientific breakthroughs, collaborate on research papers, and connect with leading academics in various fields of science and technology.",
                created_by_id=user_ids[0],  # Usar el primer usuario.
                created_at=datetime.now(timezone.utc),
                logo=None  # No se asigna logo, utilizará el predeterminado.
            ),
        ]

        # Insertar comunidades en la base de datos.
        self.seed(communities)
