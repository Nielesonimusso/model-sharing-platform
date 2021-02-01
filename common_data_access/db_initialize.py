from abc import ABC, abstractmethod

from sqlalchemy.exc import OperationalError

from .db import create_db_connection

_db = create_db_connection()


class BaseDbInitialize(ABC):

    def create_database(self, drop_before_creating=False, **kwargs):
        if drop_before_creating:
            try:
                _db.engine.connect()
                _db.session.commit()
                _db.drop_all()
                _db.session.commit()
            except OperationalError:
                print('db does not exist. trying to create.')
            except Exception as e:
                print(*e.args)
                _db.session.close()

        try:
            _db.create_all()
            self._seed_database(**kwargs)
        except Exception as e:
            print(*e.args)
        finally:
            _db.session.commit()
            _db.session.close()

    @abstractmethod
    def _seed_database(self, **kwargs):
        pass
