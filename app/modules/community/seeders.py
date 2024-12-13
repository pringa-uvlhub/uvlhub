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
                logo=None,
                admin_by_id=user_ids[0],
                users=[users[0]]  # Añade al creador como miembro automáticamente
            ),
            Community(
                name="AI Researchers",
                description="A group for discussing advancements in AI and machine learning.",
                created_by_id=user_ids[1],  # Usa otro usuario si está disponible.
                created_at=datetime.now(timezone.utc),
                logo=None,
                admin_by_id=user_ids[1],
                users=[users[1]]  # Añade al creador como miembro automáticamente
            ),

            Community(
                name="Scientific Community",
                description=(
                        "Explore scientific breakthroughs, collaborate on research papers, and connect "
                        "with leading academics in various fields of science and technology."
                ),
                created_by_id=user_ids[0],  # Usar el primer usuario.
                created_at=datetime.now(timezone.utc),
                logo=None,  # No se asigna logo, utilizará el predeterminado.
                admin_by_id=user_ids[0],
                users=[users[0]]  # Añade al creador como miembro automáticamente
            ),
            Community(
                name="Dark Matter",
                description="A group for discussing advancements in Dark Matter.",
                created_by_id=user_ids[1],  # Usa otro usuario si está disponible.
                created_at=datetime.now(timezone.utc),
                logo=None,
                admin_by_id=user_ids[1],
                users=[users[1]]  # Añade al creador como miembro automáticamente
            ),
            Community(
                name="Biology",
                description="A group for discussing advancements in biology.",
                created_by_id=user_ids[1],  # Usa otro usuario si está disponible.
                created_at=datetime.now(timezone.utc),
                logo=None,
                admin_by_id=user_ids[1],
                users=[users[1], users[0]]
            ),
            Community(
                name="Atomic",
                description="A group for discussing advancements in atomic.",
                created_by_id=user_ids[0],  # Usa otro usuario si está disponible.
                created_at=datetime.now(timezone.utc),
                logo=None,
                admin_by_id=user_ids[0],
                users=[users[1], users[0]]
            ),
        ]

        # Insertar comunidades en la base de datos.
        self.seed(communities)

        # Después de crear las comunidades, agregar los creadores como miembros.
