from flask.ext.script import Manager
from flask import Flask, render_template, send_from_directory, request

import ship
import json
import os.path
from collections import OrderedDict

from ship.models import Premium
from sqlalchemy import func

try:
    from werkzeug.contrib.cache import MemcachedCache
    cache = MemcachedCache(['127.0.0.1:11211'], key_prefix="shipmap://")
except ImportError, RuntimeError:
    from werkzeug.contrib.cache import SimpleCache
    cache = SimpleCache

application = app = Flask(__name__)
manager = Manager(app)

if os.path.exists('dsn.txt'):
    with open('dsn.txt', 'r') as dsn:
        ship.config.connect(dsn.read().rstrip('\n'))
else:
    ship.config.connect('sqlite:///premiums.db')

types = OrderedDict()
types['Base'] = 'Base'
types['HAM_RDS'] = 'Family Doctor'
types['HMO'] = 'Managed Care'
types['DIV'] = 'Other'

insurers = [(0, 'All')]
insurers.extend(ship.db.distinct_insurers())


@app.route("/")
def index():
    return render_template(
        'index.html',
        years=ship.db.years(),
        types=types,
        insurers=insurers
    )


@app.route('/data/<path:filename>')
def data(filename):
    return send_from_directory('./data', filename)


@app.route('/query')
def query():
    cache_key = lambda request: request.url.replace(request.url_root, '')

    cached = cache.get(cache_key(request))
    if cached:
        return cached

    age = request.args.get('age', 19, type=int)
    franchise = request.args.get('franchise', 300, type=int)
    year = request.args.get('year', 2014, type=int)
    accident = request.args.get('accident', "false", type=str)
    type = request.args.get('type', "Base", type=str)
    insurer = request.args.get('insurer', 0, type=int)

    p = ship.db.Premiums()
    p = p.for_swiss()
    p = p.for_year(year)
    p = p.for_age(age)
    p = p.for_franchises((franchise, ))
    p = p.for_insurance_types([type])

    if insurer:
        p = p.for_insurer(insurer)

    if accident == "true":
        p = p.with_accident()
    else:
        p = p.without_accident()

    query = p.q
    query = query.with_entities(Premium.canton, func.avg(Premium.price))
    query = query.group_by(Premium.canton)

    results = []
    for result in query:
        results.append(dict(canton=result[0], premium=result[1]))

    round_results(results)

    uncached = json.dumps(results)
    cache.set(cache_key(request), uncached)

    return uncached


def round_results(results):
    for result in results:
        result["premium"] = round(result["premium"])


cantons = ('AG', 'AI', 'AR', 'BE', 'BL', 'BS', 'FR', 'GE', 'GL', 'GR', 'JU',
           'LU', 'NE', 'NW', 'OW', 'SG', 'SH', 'SO', 'SZ', 'TG', 'TI', 'UR',
           'VD', 'VS', 'ZG', 'ZH')


@manager.command
def load():
    print "loading premiums data"
    ship.load.all()


def run():
    manager.run(default_command='runserver')


if __name__ == "__main__":
    manager.run()
