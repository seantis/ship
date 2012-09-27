# SHIP - Swiss Healthcare Insurance Premiums

Provides access to the official records for the health-insurance premiums
provided by the Bundesamt für Gesundheit (BAG).

SHIP tries to do two things right:

 * Parses the CSV files that we acquired by asking the BAG and puts them into
 the SQL Database of your choice, renaming certain fields (because we
 think that 'franchise' is better than 'F' and 'canton' better than 'C_ID').

 * Makes it easy to run a number of queries against the database. The idea
 is to gather useful queries and routines with the goal to eventually
 provide a nice API.

# Under Development

Currently, SHIP is under development, which is why the following instructions
are meant for developers. Expect this README to grow in the future.

# Installation

## Create Project

    mkdir ship && cd ship
    git clone git://github.com/seantis/ship.git .

## Install SHIP

(Virtualenv or Virtualenvrwapper are highly recommended)

    virtualenv -p python2.7 --no-site-packages .
    source bin/activate
    python setup.py develop

## Test SHIP

    python setup.py test

# Usage

There's an interactive example using IPython notebook in the "docs" folder.
Read docs/example.txt for further instructions.

For now it is best to get a database running, grab a coffee and read the source.

To get a simple sqlite database running:

    from ship import config
    config.connect('sqlite:///premiums.db')

    from ship import load
    load.all()

To understand the data read models/premium.py and db.py

# License

This project is released under the GPL v3. See LICENSE.txt.