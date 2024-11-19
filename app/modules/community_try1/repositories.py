from datetime import datetime, timezone
import logging
from typing import Optional

from sqlalchemy import desc

from app.modules.community.models import (
    Community
)
from core.repositories.BaseRepository import BaseRepository

logger = logging.getLogger(__name__)


class CommunitiesRepository(BaseRepository):
    def __init__(self):
        super().__init__(Community) 

    def get_community_by_name(self, name: str) -> Optional[Community]:
        return self.model.query.filter_by(name=name).first()

    def list_communities(self, limit: int = 10):
        return self.model.query.order_by(desc(self.model.created_at)).limit(limit).all()

    def create_new_community(self, name: str, description: str, user_id: int) -> Community:
        return self.create(
            name=name,
            description=description,
            created_by=user_id,
            created_at=datetime.now(timezone.utc)
        )

    def update_community_description(self, community_id: int, new_description: str):
        community = self.get_by_id(community_id)
        if community:
            community.description = new_description
            self.save(community)
        return community

    def delete_community(self, community_id: int):
        community = self.get_by_id(community_id)
        if community:
            self.delete(community)