import json
import time

import pytest
from flask.testing import FlaskClient

from model_sharing_backend.src import create_app
from model_sharing_backend.src.config import TestConfiguration
from model_sharing_backend.src.graph_db.seed.seed import seed_graph_db_with_inof_ontology


@pytest.fixture
def client_with_auth():
    app = create_app()
    app.test_client_class = CustomTestClient
    client = app.test_client()
    from model_sharing_backend.src.models.db_initialize import ModelDbInitialize
    ModelDbInitialize().create_database(True)
    seed_graph_db_with_inof_ontology(app.config['GRAPH_DB_SERVER_URL'], app.config['GRAPH_DB_REPOSITORY_ID'])
    time.sleep(2)  # time delay for the graph db to complete seeding
    return client


@pytest.fixture
def client():
    app = create_app()
    client = app.test_client()
    from model_sharing_backend.src.models.db_initialize import ModelDbInitialize
    ModelDbInitialize().create_database(True)
    seed_graph_db_with_inof_ontology(app.config['GRAPH_DB_SERVER_URL'], app.config['GRAPH_DB_REPOSITORY_ID'])
    time.sleep(2)  # time delay for the graph db to complete seeding
    return client


class CustomTestClient(FlaskClient):

    def open(self, *args, **kwargs):
        password = kwargs.pop('password', 'inof1234')
        username = kwargs.pop('username', 'test1_uni')
        auth_token = self.__get_auth_token(username, password)
        headers = kwargs.get('headers', {})
        headers['Authorization'] = headers.get('Authorization', auth_token)
        kwargs['headers'] = headers
        return super().open(*args, **kwargs)

    def __get_auth_token(self, username, password):
        user_login = {'username': username, 'password': password}
        response = super().open('/api/auth_token', data=json.dumps(user_login), content_type='application/json',
                                method='POST')
        return f'Bearer {response.json}'
