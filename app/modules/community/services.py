from app.modules.community.repositories import CommunityRepository
from app.modules.community.models import Community
from core.services.BaseService import BaseService


class CommunityService(BaseService):
    def __init__(self):
        super().__init__(CommunityRepository())

    def get_all(self) -> Community:
        return self.repository.get_all()
