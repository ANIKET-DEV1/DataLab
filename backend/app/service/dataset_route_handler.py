from base import BaseRepository
from ..schemas import dataset
from uuid import UUID
class for_dataset(BaseRepository):
    async def add_dataset(self,dataset:dataset.Dataset,user_id:UUID):
        pass

    async def view_dataset(self,dataset:dataset.Dataset,user_id:UUID):
        pass

    async def _dataset(self,dataset:dataset.Dataset,user_id:UUID):
        pass

