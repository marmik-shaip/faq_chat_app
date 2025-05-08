import logging
import traceback
from contextlib import contextmanager
from urllib.parse import quote

from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()

class Database:

    def __init__(self, db_config: dict) -> None:
        try:
            self._log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

            logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)
            logging.getLogger("sqlalchemy.pool").setLevel(logging.DEBUG)
            print(db_config)
            self.set_database(db_config)
        except:
            print(traceback.format_exc())

    def set_database(self, db_config: dict) -> None:
        db_url = self.get_url(db_config)
        self._engine = create_engine(db_url)

        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def get_url(self, db_config: dict) -> str:
        if 'db_url' in db_config:
            return db_config['db_url']
        else:
            dialect = db_config['dialect']
            username = quote(db_config['username'])
            password = quote(db_config['password'])
            hostname = db_config['hostname']
            database = db_config['database']
            return f'{dialect}://{username}:{password}@{hostname}/{database}'

    def create_database(self) -> None:
        Base.metadata.create_all(self._engine)

    @contextmanager
    def session(self):
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            self._log.exception("Session rollback because of exception", exc_info=1)
            session.rollback()
            raise
        finally:
            session.close()