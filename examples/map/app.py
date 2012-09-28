from flask.ext.script import Manager
from flask import Flask, render_template, send_from_directory

import ship

app = Flask(__name__)
manager = Manager(app)

ship.config.connect('sqlite:///premiums.db')

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/data/<path:filename>')
def send_foo(filename):
     return send_from_directory('./data', filename)

cantons = ('AG', 'AI', 'AR', 'BE', 'BL', 'BS', 'FR', 'GE', 'GL', 'GR', 'JU', 
           'LU', 'NE', 'NW', 'OW', 'SG', 'SH', 'SO', 'SZ', 'TG', 'TI', 'UR', 
           'VD', 'VS', 'ZG', 'ZH')

@manager.command
def load():
    print "loading premiums data"
    ship.load.all()
    
if __name__ == "__main__":
    manager.run()