from app.modules.fakenodo.models import Deposition

from core.repositories.BaseRepository import BaseRepository

from app import db


class DepositionRepository(BaseRepository):
    def __init__(self):
        super().__init__(Deposition)

    def createDeposition(self, metadata=None, doi=None):  # Damos un valor por defecto a ambos campos
        """
        Crea una nueva Deposition de Fakenodo

        Args:
            metadata (dict, optional): Json o Diccionarion con metada de la deposición
            doi (str, optional): El doi de la deposición

        Returns:
            Deposition: La deposición creada
        """
        # Con esto vamos a impedr que un dtaset que aun no
        # tenga metadata no se pueda subir a fakenodo
        if metadata is None:
            metadata = {}

        depo = Deposition(metadata=metadata, doi=doi)
        db.session.add(depo)
        db.session.commit()

        return depo
