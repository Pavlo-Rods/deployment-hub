from app.modules.community.models import Community
from core.seeders.BaseSeeder import BaseSeeder
from app.modules.auth.models import User


class CommunitySeeder(BaseSeeder):
    priority = 2  # Lower priority

    def run(self):
        user1 = User.query.filter_by(email='user1@example.com').first()
        user2 = User.query.filter_by(email='user2@example.com').first()

        if not user1 or not user2:
            raise Exception("Users not found. Please seed users first.")

        communityData = [
            Community(id=1,
                      name="Comunidad de ciencias",
                      description="Una comunidad de ciencias sin más",
                      owner_id=user1.id),
            Community(id=2,
                      name="Comunidad de tecnología",
                      description="Una comunidad dedicada a la tecnología y la innovación.",
                      owner_id=user1.id),
            Community(id=3,
                      name="Comunidad de arte",
                      description="Un espacio para los amantes del arte y la cultura.",
                      owner_id=user2.id),
            Community(id=4,
                      name="Comunidad de deportes",
                      description="Para los entusiastas de los deportes y la actividad física.",
                      owner_id=user2.id),
            Community(id=5,
                      name="Comunidad de música",
                      description="Un lugar para compartir y disfrutar de la música.",
                      owner_id=user1.id),
            Community(id=6,
                      name="Comunidad de literatura",
                      description="Para los amantes de la lectura y la escritura.",
                      owner_id=user2.id),
        ]

        self.seed(communityData)
