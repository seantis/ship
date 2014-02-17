SHIP - Swiss Healthcare Insurance Premiums
==========================================

Provides access to the official records for the health-insurance
premiums provided by the Bundesamt für Gesundheit (BAG).

SHIP tries to do two things right:

-  Parses the CSV files that we acquired by asking the BAG and puts them
   into the SQL Database of your choice, renaming certain fields
   (because we think that 'franchise' is better than 'F' and 'canton'
   better than 'C\_ID').

-  Makes it easy to run a number of queries against the database. The
   idea is to gather useful queries and routines with the goal to
   eventually provide a nice API.

Under Development
=================

Currently, SHIP is under development, which is why the following
instructions are meant for developers. Expect this README to grow in the
future.

Installation
============

Create Project
--------------

::

    mkdir ship && cd ship
    git clone git://github.com/seantis/ship.git .

Install SHIP
------------

(Virtualenv or Virtualenvrwapper are highly recommended)

::

    virtualenv -p python2.7 --no-site-packages .
    source bin/activate
    python setup.py develop

Test SHIP
---------

::

    python setup.py test

Usage
=====

There's an interactive example using IPython notebook in the "docs"
folder. Read docs/example.txt for further instructions.

For now it is best to get a database running, grab a coffee and read the
source.

To get a simple sqlite database running:

::

    from ship import config
    config.connect('sqlite:///premiums.db')

    from ship import load
    load.all()

To understand the data read models/premium.py and db.py

Import latest data
==================

The latest data for the Swiss healthinsurance premiums are not yet
publically available, but they will be soon. Currently to get them one
has to contact the Swiss governement.

The data they release is a mixture of csv and xls files. To import them
into ship one has to do the following:

1. Check if the data structure has changed.

   Compare Doku\_PraemienDaten.txt in the data release with
   ``rawdata/doku_praemien_daten.txt``. The field descriptions should
   match.

2. Copy the premiums.

   Praemien\_CH.csv and Praemien\_EU.csv can be used without changes.
   Just copy them to the ``/rawdata`` folder, renaming them
   appropriately. E.g. if 2014 rename them as follows:

   ::

       Praemien_CH.csv -> rawdata/2014_ch.csv
       Praemien_EU.csv -> rawdata/2014_eu.csv

   The first line (headers) may be omitted, though it should also work
   with the header line present.

3. Copy the insurers.

   Open the Praemien\_CH.xls file, select the "(G)" sheet, and copy the
   columns "G\_ID" and "G\_KBEZ" to the new 2014\_insurers.csv file. Use
   semicolons as separator. When in doubt, check the insurers file of a
   previous year.

4. Copy the towns.

   The towns and the regions they are in can be acquired through the
   following website:

   http://www.priminfo.ch/praemien/regionen/de/index.php

   From the B\_NPA\_2014 copy PLZ, Ortsbezeichnung, Kanton, BFS-Nr.,
   Region and Gemeinde into a csv in the same format as the insurers in
   step three.

   Note that the BFS-Nr. comes before the region. The column order
   *must* be as follows:

   ``PLZ, Ortsbezeichnung, Kanton, BFS-Nr., Region, Gemeinde``

   Store this as ``rawdata/2014_towns.csv``

5. Adjust the test.

   Add the newly added year to ``ship/tests/test_db.py`` and run python
   setup.py test. If there's an unicode error you should save the csv
   files using UTF-8 encoding.

License
=======

This project is released under the GPL v3. See LICENSE.txt.
