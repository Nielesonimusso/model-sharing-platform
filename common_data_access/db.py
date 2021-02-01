from flask_sqlalchemy import SQLAlchemy

from .db_access import Query


def create_db_connection(app=None, query_cls=Query):
    global __db__
    if '__db__' not in globals():
        __db__ = SQLAlchemy(app=app, query_class=query_cls)
        __db__.init_app(app)
    return __db__
