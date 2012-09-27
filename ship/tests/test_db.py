import unittest
import os.path

from ship import load
from ship import config
from ship.models import Town

class TestDb(unittest.TestCase):

    def tearDown(self):
        config.base.metadata.drop_all(bind=config.session.bind)
        config.base.metadata.create_all(bind=config.session.bind)

    def test_session(self):

        # ensure that the default session is initialized
        self.assertTrue(config.session is not None)
        self.assertTrue(config.session() is config.session())
        self.assertEqual(str(config.session.bind.url), 'sqlite:///:memory:')

    def test_session_property(self):

        # ensure that a change in the connection leads to a change
        # in the proxied session
        from ship.config import session
        old_bind = session.bind

        config.connect()
        self.assertFalse(old_bind is config._session.bind)
        self.assertFalse(old_bind is session.bind)

    def test_models(self):
        
        town = Town(name=u"Leetlington", zipcode=1337, region=0, year=2012)
        self.assertEqual(town.name, u"Leetlington")
        self.assertEqual(town.zipcode, 1337)
        self.assertEqual(town.region, 0)
        self.assertEqual(town.year, 2012)

        config.session.add(town)

    def test_rawdata_path(self):

        self.assertTrue(os.path.exists(config.rawdata_path))

    def test_file_path(self):

        missing = [2011]
        existing = [2012]

        for year in existing:
            self.assertTrue(os.path.exists(load.file_path(year, u"ch")))
            self.assertTrue(os.path.exists(load.file_path(year, u"eu")))
            self.assertTrue(os.path.exists(load.file_path(year, u"towns")))
            self.assertTrue(os.path.exists(load.file_path(year, u"insurers")))

        for year in missing:
            self.assertEqual(load.file_path(year, u"ch"), None)
            self.assertEqual(load.file_path(year, u"eu"), None)
            self.assertEqual(load.file_path(year, u"towns"), None)
            self.assertEqual(load.file_path(year, u"insurers"), None)

    def test_available_years(self):

        files = [
            '2012_insurers.csv', '2012_towns', '2012_ch.csv', '2012_eu.csv',
            '2013_insurers.csv', '2013_towns', '2013_ch.csv', '2013_eu.csv',
        ]

        self.assertEqual(load.available_years(files), [2012, 2013])

        files = [
            '2012-insurers.csv', '2012-towns', '2012-ch.csv', '2012-eu.csv',
            '2013-insurers.csv', '2013-towns', '2013-ch.csv', '2013-eu.csv',
        ]

        self.assertEqual(load.available_years(files), [])

        files = [
            '2012_insurers.csv', '2012_towns', '2012_ch.csv', '2012_eu.csv',
            '2013_insurers.csv', '2013_towns', '2013_ch.csv'
        ]

        self.assertRaises(AssertionError, load.available_years, files)

    def test_parse_cents(self):

        self.assertEqual(load.premium_in_cents(''), 0)
        self.assertEqual(load.premium_in_cents('0'), 0)
        self.assertEqual(load.premium_in_cents('100.00'), 10000)
        self.assertEqual(load.premium_in_cents('100.1'), 10010)
        self.assertEqual(load.premium_in_cents('100'), 10000)

    def test_load_ch_premiums(self):

        self.assertEqual(load.ch_premiums(limit=1000), 2)

    def test_load_eu_premiums(self):

        self.assertEqual(load.eu_premiums(limit=1000), 2)

    def test_load_towns(self):

        self.assertEqual(load.towns(), 2)
        self.assertEqual(load.towns(), 0)
        self.assertEqual(load.towns(update=True), 2)
        self.assertEqual(load.towns(year=1999), 0)

        config.session.commit()

    def test_load_insurers(self):

        self.assertEqual(load.insurers(), 2)
        self.assertEqual(load.insurers(), 0)
        self.assertEqual(load.insurers(update=True), 2)
        self.assertEqual(load.insurers(year=1999), 0)

        config.session.commit()

    def test_teardown(self):

        # test if the teardown mechanism of this class work
        # by re-running the first part of test_load_insurers
        self.assertEqual(load.insurers(), 2)