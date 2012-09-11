import os.path

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

class DbConfig(object):
    
    _session = None
    
    base = declarative_base()

    @property
    def session(self):
        """ Return an sqlalchemy session. """

        if not self._session:
            self.connect()

        return self._session

    @property
    def rawdata_path(self):
        """ Return the absolute path to the rawdata. """

        this = os.path.dirname(__file__)
        
        path = os.path.join(this, '../rawdata')
        path = os.path.abspath(path)

        assert os.path.exists(path)

        return path

    def connect(self, url='sqlite:///:memory:', engine=None):
        """ Use the database defined by the url or the sqlalchemy engine. """
        
        assert url or engine

        if self._session:
            self._session.close()

        if url: engine = create_engine(url)

        self._session = scoped_session(sessionmaker(bind=engine))
        
        # import models before creating them to ensure that base.metadata
        # contains all tables needed
        from ship import models
        assert models

        self.base.metadata.create_all(bind=engine)
        assert self._session.bind.table_names()

# see http://stackoverflow.com/questions/9937279/can-modules-have-properties
import sys
sys.modules[__name__] = DbConfig()