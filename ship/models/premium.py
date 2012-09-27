from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.orm import deferred, relationship, backref
from sqlalchemy.types import Boolean, String, Integer, SmallInteger

from ship.config import base
from ship.models.mixins import YearMixin

class Premium(base, YearMixin):
    __tablename__ = 'premiums'

    id = Column(Integer, primary_key=True)

    # Important Fields #
    ####################

    # CH or EU, CH is for Swiss living in Switzerland
    # EU is for Swiss living in an EU country
    group = Column(String(2), nullable=False)

    # Canton in uppercase letters (CH group only)
    canton = Column(String(2))

    # Country in uppercase letters (EU group only)
    # List of countries: http://www.priminfo.ch/praemien/praemien_eu/EU.pdf
    country = Column(String(3))

    # Region (0 if no region applies). Some cantons divide their towns 
    # in different regions which have different premiums. 
    # Check ship.models.town and ship.db.Towns to acquire the relevant region.
    region = Column(SmallInteger, nullable=False)

    # Age group (0-18 = Kids, 19-25 = Young Adults, 26+ = Adults)
    age_group = Column(SmallInteger, nullable=False)

    # K1-4 for kids, J1 for Yong Adults, E1 for Adults
    age_group_id = Column(String(2), nullable=False)

    # True if the premium includes accidents
    with_accident = Column(Boolean, nullable=False)

    # Insurance type (Base, HAM_RDS, HMO or DIV)
    insurance_type = Column(String(7), nullable=False)

    # Description of the *specific* insurance (not the description of the type)
    insurance_description = Column(String(100), nullable=False)

    # Franchise used
    franchise = Column(SmallInteger, nullable=False)

    # Premium (in cents/rappen, to avoid floating point issues)
    premium = Column(Integer, nullable=False) # store in cents

    # Link to the insurer providing this insurance
    insurer_id = Column(Integer, ForeignKey('insurers.id'))
    insurer = relationship("Insurer", backref=backref('premiums'))

    # (Probably) Not Important Fields #
    ###################################

    # Year in which the record was recorded
    inquiry_year = deferred(Column(SmallInteger))

    # Type the insurance uses internally? Probably.
    internal_type = deferred(Column(String(20), nullable=False))

    # First record of the given age subgroup
    primary_age_subgroup = deferred(Column(Boolean, nullable=False))

    # Age group (K, J or E)
    age_group_type = deferred(Column(String(1), nullable=False))

    # True if base insurance. Not sure what a base insurance is in this case.
    is_base_insurance = deferred(Column(Boolean, nullable=False))

    # True if first franchise of type
    is_base_franchise = deferred(Column(Boolean, nullable=False))

    # Level of the franchise, 1 = base franchise
    franchise_level = deferred(Column(SmallInteger, nullable=False))

    # Sort index by which the model should be sorted (defined by whom?)
    model_sort_id = deferred(Column(SmallInteger))

    # True if the first insurance model of an insurance type
    primary_insurance_type = deferred(Column(SmallInteger))

    # Fully active how? I don't understand..
    is_fully_active = deferred(Column(Boolean))