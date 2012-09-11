from sqlalchemy.schema import Column
from sqlalchemy.types import SmallInteger

# make the year column go at the end
# see http://stackoverflow.com/questions/3923910/sqlalchemy-move-mixin-columns-to-end
from sqlalchemy.ext.declarative import declared_attr


class YearMixin(object):

    @declared_attr
    def year(cls):
        return Column(SmallInteger, nullable=False)