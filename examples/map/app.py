from flask.ext.script import Manager
from flask import Flask, render_template, send_from_directory, request

import ship
import json

from ship.models import Premium
from sqlalchemy import func
from pprint import pformat

app = Flask(__name__)
manager = Manager(app)

ship.config.connect('sqlite:///premiums.db')

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/data/<path:filename>')
def data(filename):
     return send_from_directory('./data', filename)

@app.route('/query')
def query():
    age = request.args.get('age', 19, type=int)
    franchise = request.args.get('franchise', 300, type=int)
    year = request.args.get('year', 2013, type=int)

    p = ship.db.Premiums()
    p = p.for_swiss()
    p = p.for_year(year)
    p = p.for_age(age)
    p = p.for_franchises((franchise, ))

    query = p.q
    query = query.with_entities(Premium.canton, func.avg(Premium.price))
    query = query.group_by(Premium.canton)

    results = []
    for result in query:
        results.append(dict(canton=result[0], premium=result[1]))

    round_results(results)

    return json.dumps(results)

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
    
if __name__ == "__main__":
    manager.run()