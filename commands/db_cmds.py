from typing import Callable
from contextlib import AbstractContextManager
from dependency_injector.wiring import Provide, inject

from container import Container


class DbCmds:
    @inject
    def __init__(
        self,
        database: Callable[..., AbstractContextManager] = Provide[Container.db_session],
    ):
        self.database = database
        self.rows = []

    def __call__(self, command):
        if command == 'create-db':
            self.database.create_database()
