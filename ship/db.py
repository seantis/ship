from itertools import chain

from sqlalchemy import desc

from ship.config import session
from ship.models import Premium, Insurer, Town

def execute(sql):
    """ Executes the given sql expression on the current session and returns
    the result as SQLAlchemy Resultproxy. """
    return session.execute(sql)

def unpack(result):
    """ Takes a nested list and flattens/unpacks it, e.g.

    >>> unpack(("a", "b"), ("c", "d"))
    ["a", "b", "c", "d"]

    Useful for query results with only one row. """

    return list(chain.from_iterable(result))

def years():
    """ Returns the years available in the database. Not to be confused
    with ship.db.load.available_years which resturns the years available
    as rawdata files. 

    The years are returned in descending order.

    """

    # check the smallest table as all table should contain data for
    # each possible year
    query = session.query(Insurer.year).distinct()
    query = query.order_by(desc(Insurer.year))
    
    return unpack(query.all())

def latest_year():
    """ Returns the most current year. """
    all_years = years()
    return all_years and all_years[0] or None

def age_group(age):
    """ Returns the age group of the given age. Done static for now as it
    doesn't seem to be changing any time soon.
    """
    assert age >= 0

    if age >= 26: return 26
    if age >= 19: return 19

    return 0

def insurance_types(year=None):
    """ Returns the possible insurance types by year, with the latest 
    year as default. """
    
    year = year or latest_year()
    assert year

    query = session.query(Premium.insurance_type)
    query = query.filter(Premium.year == year)
    query = query.distinct()
    query = query.order_by(Premium.insurance_type)

    return unpack(query.all())

def insurers(year=None):
    """ Returns the insurers of the given or the latest year. """

    year = year or latest_year()
    assert year

    return session.query(Insurer)

def franchises(age=None, year=None):
    """ Returns a list of possible franchises for the given or the latest year. 
    Since kids may have different franchises than adults the list is further
    reduced if the age in question is passed.

    """

    year = year or latest_year()
    assert year

    query = session.query(Premium.franchise)
    query = query.filter(Premium.year == year)

    if age is not None:
        query = query.filter(Premium.age_group == age_group(age))

    query = query.distinct().order_by(Premium.franchise)

    return unpack(query.all())

def cantons():
    """ Returns a list of available cantons."""

    query = session.query(Premium.canton)
    query = query.filter(Premium.group == 'CH')
    return unpack(query.distinct().all())

def countries():
    """ Returns a list of available countries."""

    query = session.query(Premium.country)
    query = query.filter(Premium.group == 'EU')
    return unpack(query.distinct().all())

class Towns(object):
    """ Provides a wrapper around an SQLAlchemy Query to simplify the filtering
    of the database for people not too familiar with its structure.

    Towns specifically exists because it is not straight forward to get from
    a zipcode to a region number, which is required for premium lookups.

    Zipcodes may in fact belong to different region numbers and it is often
    up to the user to figure out which exact place is relevant for him. 

    Compare the way priminfo.ch solves this. Enter an ambiguous zipcode like
    6340 (Baar) and you'll be asked to choose one out of four municipalities.

    In other words, towns is not a simple lookup table, it deals with groups
    of records just as the premiums table.

    Example-Usage

    t = Towns()
    t = t.for_year(2012)
    t = t.in_canton('ZH')
    
    t.regions()
    >>> [0]

    """

    def __init__(self, query=None):
        self.q = query or session.query(Town)

    def for_year(self, year):
        return Towns(self.q.filter(Town.year==year))

    def with_zipcode(self, zipcode):
        return Towns(self.q.filter(Town.zipcode==zipcode))

    def in_canton(self, canton):
        return Towns(self.q.filter(Town.canton==canton.upper()))

    def regions(self):
        return unpack(self.q.with_entities(Town.region).distinct().all())

class Premiums(object):
    """ Provides a wrapper around an SQLAlchemy Query to simplifiy the filtering
    of the database for people not too familiar with its structure.

    The abstraction, as all abstractions, is not perfect and breaks down quickly,
    but it allows for some simple lookups which *might* be needed in a webapp
    providing a way to lookup premiums.

    If not useful for anything else it provides a place to document standard
    queries to the database.

    Example-Usage:

    p = Premiums()
    p = p.for_year(2012)
    p = p.for_age(28)
    p = p.for_canton('ZH')
    p = p.for_region(0)
    p = p.with_accident()

    p.count()
    >>> 25000

    """

    def __init__(self, query=None):
        self.q = query or session.query(Premium)

    def results(self):
        return self.q.order_by(Premium.premium)

    def count(self):
        return self.q.count()

    def for_year(self, year):
        return Premiums(self.q.filter(Premium.year==year))

    def for_swiss(self):
        return Premiums(self.q.filter(Premium.group=='CH'))

    def for_swiss_expats(self):
        return Premiums(self.q.filter(Premium.group=='EU'))

    def for_age(self, age):
        return Premiums(self.q.filter(Premium.age_group==age_group(age)))

    def for_ages(self, ages):
        groups = map(age_group, ages)
        return Premiums(self.q.filter(Premium.age_group.in_(groups)))

    def for_kids(self):
        return self.for_age(0)

    def for_young_adults(self):
        return self.for_age(19)

    def for_adults(self):
        return self.for_age(26)

    def for_country(self, country):
        return Premiums(self.q.filter(Premium.country==country))

    def for_canton(self, canton):
        return Premiums(self.q.filter(Premium.canton==canton.upper()))

    def for_region(self, region):
        return Premiums(self.q.filter(Premium.region==region))

    def for_town(self, town):
        return self.for_canton(town.canton).for_region(town.region)

    def for_franchises(self, franchises):
        return Premiums(self.q.filter(Premium.franchise.in_(franchises)))

    def for_insurance_types(self, insurance_types):
        return Premiums(self.q.filter(Premium.insurance_type.in_(insurance_types)))

    def with_accident(self):
        return Premiums(self.q.filter(Premium.with_accident==True))

    def without_accident(self):
        return Premiums(self.q.filter(Premium.with_accident==False))