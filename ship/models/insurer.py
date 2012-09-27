from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer

from ship.config import base
from ship.models.mixins import YearMixin

class Insurer(base, YearMixin):
    __tablename__ = 'insurers'

    id = Column(Integer, primary_key=True)
    insurer_id = Column(Integer, nullable=False)
    name = Column(String(length=32), nullable=False)