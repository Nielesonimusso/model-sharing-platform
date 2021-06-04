import os


class BaseConfiguration():
    # application config
    PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))
    INGREDIENT_SERVICE_URL = 'http://localhost:5002'
    TASTES_TO_CALCULATE = os.getenv('TASTES_TO_CALCULATE', 'sweetness,sourness,saltiness,tomato taste').split(',')
    MODEL = os.getenv('MODEL', 'taste').lower() # ['taste', 'nutrition'] ['pasteurization', 'shelflife', 'calibration', 'dropletsize']

    APPLICATION_BASE = os.getenv('APPLICATION_BASE', 'http://localhost:5001')
    INOF_BASE = os.getenv('INOF_BASE', 'http://localhost:81')
    API_TOKEN = 'inof1234hossain' # replace with api token of user

    # SQLAlchemy config
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@localhost:5432/gateway_db_test'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@db-container:5432/gateway_db_test'
    SQLALCHEMY_ECHO = False

    # flask config
    TESTING = False
    SECRET_KEY = str(os.urandom(32))
    ENV = 'development'
    DEBUG = True


class TestConfiguration(BaseConfiguration):
    SECRET_KEY = 's3cr3t_k3y'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@localhost:5432/gateway_db_test'


class DockerDeployConfiguration(BaseConfiguration):
    INGREDIENT_SERVICE_URL = 'http://ingredient-service:5002'
    SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@db-container:5432/gateway_db'
    # TESTING = False
    # DEBUG = False
    # ENV = 'production'


DefaultConfiguration: BaseConfiguration = BaseConfiguration()
