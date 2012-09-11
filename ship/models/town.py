from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, SmallInteger

from ship.config import base
from ship.models.mixins import YearMixin

class Town(base, YearMixin):
    __tablename__ = 'towns'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=20), nullable=False)
    canton = Column(String(length=2), nullable=False)
    zipcode = Column(SmallInteger, nullable=False)

    # region, of which there may be many for a single town / zipcode
    region = Column(SmallInteger, nullable=False)

    # name of the municipality (politische Gemeinde) to which the town belongs
    municipality = Column(String(length=30), nullable=False)