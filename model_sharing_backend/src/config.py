import os
from datetime import timedelta


class BaseConfiguration():
    # application config
    PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))
    INGREDIENT_SERVICE_URL = 'http://localhost:5002'
    GRAPH_DB_SERVER_URL = 'http://localhost:7200'
    GRAPH_DB_REPOSITORY_ID = 'INoF'

    # flask config
    TESTING = True
    SECRET_KEY = str(os.urandom(32))
    DEBUG = True
    ENV = 'development'

    # SQLAlchemy config
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@localhost:5432/model_db_test'
    APPLICATION_VERSION = '0.1'
    SQLALCHEMY_ECHO = True

    # JWT
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # SWAGGER
    SWAGGER_TITLE = 'Model Sharing Platform'
    SWAGGER_VERSION = '2.0'
    SWAGGER = dict(swagger_version=SWAGGER_VERSION,
                   title=SWAGGER_TITLE,
                   description='Api specification for Model Sharing Platform')


class TestConfiguration(BaseConfiguration):
    SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@localhost:5432/model_db_test'
    TESTING = True


class DockerDeployConfiguration(BaseConfiguration):
    INGREDIENT_SERVICE_URL = 'http://ingredient-service:5002'
    SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@db-container:5432/model_db'
    GRAPH_DB_SERVER_URL = 'http://graphdb-container:7200'
    GRAPH_DB_REPOSITORY_ID = 'INoF'
    TESTING = False
    DEBUG = False
    SQLALCHEMY_ECHO = False
    ENV = 'production'
