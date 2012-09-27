# This module has the imports inlined because a DBConfig class instance
# is the actual module. This usually works fine, but some older virtualenv
# versions seem to have trouble with that.

# Namely, the imports done outside the functions of DBConfig are None once
# they are required

# Why do it like this? Because it allows for rather nice syntax:

# from ship.config import session
# session.query()

# which would otherwise be

# from ship import config
# config.session.query()

# In other words, this makes properties of the DbConfig instance
# available for import. It'll probably work just fine with
# future virtualenv releases.

class DbConfig(object):
    
    _session = None
    _file = __file__ # is also weird on older virtualenv versions

    from sqlalchemy.ext.declarative import declarative_base
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

        import os.path

        this = os.path.dirname(self._file)
        
        path = os.path.join(this, '../rawdata')
        path = os.path.abspath(path)

        assert os.path.exists(path)

        return path

    def connect(self, url='sqlite:///:memory:', engine=None):
        """ Use the database defined by the url or the sqlalchemy engine. """
        
        assert url or engine

        from zope import proxy
        from sqlalchemy import create_engine, orm

        if url: engine = create_engine(url)

        session = orm.scoped_session(orm.sessionmaker(bind=engine))

        if self._session:
            self._session.close()
            proxy.setProxiedObject(self._session, session)
        else:
            self._session = proxy.ProxyBase(session)
        
        # import models before creating them to ensure that base.metadata
        # contains all tables needed
        from ship import models
        assert models

        self.base.metadata.create_all(bind=engine)
        assert self._session.bind.table_names()

# see http://stackoverflow.com/questions/9937279/can-modules-have-properties
import sys
sys.modules[__name__] = DbConfig()