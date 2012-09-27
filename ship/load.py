import os
import os.path
import csv
import logging

logger = logging.getLogger('ship')

from itertools import chain, islice
from collections import Counter

from ship import config
from ship.config import session
from ship.models import Town, Insurer, Premium

available_types = ('insurers', 'towns', 'ch', 'eu')
 
def all(year='*', update=False):
    towns(year, update)
    insurers(year, update)
    ch_premiums(year, update)
    eu_premiums(year, update)

def file_path(year, type):
    """ Return the path to the given year and filetype, or None if missing."""

    assert type in available_types, "invalid file type %s" % type

    path = os.path.join(config.rawdata_path, u'%i_%s.csv' % (year, type))
    return os.path.exists(path) and os.path.abspath(path) or None

def available_years(files=None):
    """ Return the available rawdata years in ascending order. 
    The list of files may be optionally passed to ease testing."""
    
    files = files or os.listdir(config.rawdata_path)
    year_files = Counter()
    
    for f in files:
        if not '_' in f:
            continue
        
        year = f.split('_')[0]

        if not year.isdigit():
            continue

        year_files[int(year)] += 1

    years = set(year_files.elements())

    for year in years:
        assert year_files[year] == len(available_types), \
        'types missing in year %i' % year

    return sorted(years)

def chunked(seq, chunksize):
    """ Yields items from an iterator in chunks."""
    it = iter(seq)
    while True:
        yield chain([it.next()], islice(it, chunksize-1))

def premium_in_cents(value):
    """ Parse the premium from the csv file and return it's value in cents. """

    if not value:
        return 0

    if not '.' in value:
        return int(value) * 100

    if '.' in value and len(value.split('.')[1]) == 1:
        return int(value.replace('.', '')) * 10

    return int(value.replace('.', ''))

class Loader(object):

    def __init__(self, model, type, factory):
        self.model = model
        self.type = type
        self.factory = factory

    def __call__(self, year='*', update=False, limit=0):

        # limit is for testing only
        if year and year != '*':
            # continue with year if file is found
            csv_path = file_path(year, self.type)
            if not csv_path:
                return 0
        else:
            # no year given, go through all years
            results = []
            for year in available_years():
                results.append(self.__call__(year, update, limit))

            return sum(results)

        # if there's a record of the given year, maybe stop
        if not update:
            if self.model is Premium:
                query = session.query(Premium).filter(Premium.year==year)
                query = query.filter(Premium.group==self.type.upper())
            else:
                query = session.query(self.model).filter(self.model.year==year)
            
            if query.first():
                return 0

        # the csv module does not support unicode so we need to decode
        # unicode strings on the fly
        def lines():
            decode = lambda s: s.decode('utf-8')

            _lines = csv.reader(open(csv_path, 'rb'), delimiter=';')
            for ix, line in enumerate(_lines):
                yield map(decode, line)

        lineindex = 0

        # load lines chunked to keep the memory usage under control
        for chunk in chunked(lines(), 1000):

            try:
                for line in chunk:
                    lineindex += 1

                    try:
                        obj = self.factory(line)
                        obj.year = year
                    
                    except ValueError:
                        # there are a number of empty lines in the rawdata files
                        # which we can safely skip over
                        logger.warn("invalid line %i in %s, skipping" % (
                            lineindex, csv_path
                        ))
                        continue

                    if update:
                        session.merge(obj)
                    else:
                        session.add(obj)
            except:
                session.rollback()
                raise
            else:
                # I cannot for the life of me figure out why sqlite won't accept
                # nested transactions here. So I make due with sequential commits
                session.commit()

            # respect the limit, which is aligned to the chunk steps
            if limit > 0 and lineindex > limit:
                break

        return 1

def load_town(line):
    t = Town()
    t.zipcode = int(line[0])
    t.name = line[1]
    t.canton = line[2]
    t.region = int(line[4])
    t.municipality = line[5]
    return t

towns = Loader(Town, 'towns', load_town)
        
def load_insurer(line):
    i = Insurer()
    i.insurer_id = int(line[0])
    i.name = line[1]
    return i

insurers = Loader(Insurer, 'insurers', load_insurer)

def load_ch_premium(line):
    p = Premium()
    p.insurer_id = int(line[0])                     # G_ID
    p.canton = line[1]                              # C_ID
    p.group = line[2]                               # C_GRP
    p.inquiry_year = int(line[3])                   # EJAHR
    p.region = line[5]                              # R_ID
    p.age_group = line[6]                           # M_ID
    p.with_accident = int(line[7]) == 5             # VAR_ID
    p.internal_type = line[8]                       # V_ID
    p.insurance_type = line[9]                      # V_TYP
    p.primary_age_subgroup = int(line[10]) == 1     # isBase_V2
    p.age_group_id = line[11]                       # V2_ID
    p.age_group_type = line[12]                     # V2_TYP
    p.is_base_insurance = int(line[13]) == 1        # isBase_P
    p.is_base_franchise = int(line[14]) == 1        # isBase_F
    p.franchise_level = int(line[15])               # F_Stufe
    p.franchise = int(line[16])                     # F
    p.premium = premium_in_cents(line[17])          # P (in cents)
    p.model_sort_id = int(line[18])                 # V_SORT_NR
    p.insurance_description = line[19]              # V_KBEZ
    p.primary_insurance_type = line[20]             # isBASE_V
    p.is_fully_active = line[21] != u'1.1'          # isTaetig
    return p

ch_premiums = Loader(Premium, 'ch', load_ch_premium)

def load_eu_premium(line):
    p = Premium()
    p.insurer_id = int(line[0])                     # G_ID
    p.country = line[1]                             # C_ID
    p.group = line[2]                               # C_GRP
    p.region = line[4]                              # R_ID
    p.age_group = line[5]                           # M_ID
    p.with_accident = int(line[6]) == 5             # VAR_ID
    p.internal_type = line[7]                       # V_ID
    p.insurance_type = line[8]                      # V_TYP
    p.primary_age_subgroup = int(line[9]) == 1      # isBase_V2
    p.age_group_id = line[10]                       # V2_ID
    p.age_group_type = line[11]                     # V2_TYP
    p.is_base_insurance = int(line[12]) == 1        # isBase_P
    p.is_base_franchise = int(line[13]) == 1        # isBase_F
    p.franchise_level = int(line[14])               # F_Stufe
    p.franchise = int(line[15])                     # F
    p.premium = premium_in_cents(line[17])          # P (in cents)
    p.insurance_description = line[17]              # V_KBEZ
    return p

eu_premiums = Loader(Premium, 'eu', load_eu_premium)