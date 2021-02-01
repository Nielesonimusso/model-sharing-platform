from flask import Flask

from common_data_access.db import create_db_connection
from common_data_access.db_access import Query


def initialize_db_connections(app: Flask):
    create_db_connection(app, Query)
