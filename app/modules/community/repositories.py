from app.modules.community.models import Community
from core.repositories.BaseRepository import BaseRepository
from typing import Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class CommunityRepository(BaseRepository):
    def __init__(self):
        super().__init__(Community)

    def get_community_by_id(self, name: str) -> Optional[Community]:
        return self.model.query.filter_by(id=id).first()

    def get_community_by_name(self, name: str) -> Optional[Community]:
        return self.model.query.filter_by(name=name).first()

    def list_communities(self, limit: int = 10):
        return self.model.query.order_by(self.model.created_at.desc()).limit(limit).all()

    def create_new_community(self, name: str, description: str, user_id: int) -> Community:
        return self.create(
            name=name,
            description=description,
            created_by=user_id,
            admin_by=user_id,
            created_at=datetime.now(timezone.utc)
        )

    def delete_community(self, community_id: int) -> bool:
        return self.delete(community_id)
