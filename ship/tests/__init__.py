import unittest
import logging

def load_tests(loader, tests, pattern):
    return loader.discover('.')

def get_suite():
    "Return a unittest.TestSuite."

    # setup logging for tests
    logger = logging.getLogger("ship")
    logger.setLevel(logging.WARN)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARN)

    # add ch to logger
    logger.addHandler(ch)

    import ship.tests
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(ship.tests)

    return suite