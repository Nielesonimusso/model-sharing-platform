import os


class BaseConfiguration():
    # application config
    PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))
    # DATA_SOURCE_FILE_PATH = os.path.join(PACKAGE_PATH, 'data/IngredientDatabase_2020m02d21.csv')
    DATA_SOURCE_FILE_PATHS = [os.path.join(PACKAGE_PATH, 'data/IngredientDatabase.csv'), 
        os.path.join(PACKAGE_PATH, 'data/IngredientPropertyDatabase.csv')]
    COLUMN_TYPES = [dict(Ingredient=str, IngredientCode=str), 
        dict(Ingredient=str,IngredientCode=str,IngredientProperty=str,
            ValueText=str,ValueNum=float,UnitOfMeasure=str)]
    ONTOLOGY_FILE_PATH = os.path.join(PACKAGE_PATH, 'data/test-ontology.ttl')
    # APPLICATION_BASE = 'http://data-access-gateway:5001/api/'
    APPLICATION_BASE = 'http://localhost:5002/api/'
    ACCESS_PRICE = 7

    # flask config
    TESTING = False
    SECRET_KEY = str(os.urandom(32))
    DEBUG = True
    ENV = 'development'

    # Internet of Food config
    #INOF_BASE = 'http://model-sharing-backend:5000/api/'
    INOF_BASE = 'http://localhost:81/api/'
    API_TOKEN = 'inof1234hossain' # replace with api token of user

    # # SQLAlchemy config
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@localhost:5432/ingredient_db'
    # SQLALCHEMY_ECHO = False


class TestConfiguration(BaseConfiguration):
    SECRET_KEY = 's3cr3t_k3y'
    DEBUG = True
    # SQLALCHEMY_ECHO = True
    # SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@localhost:5432/ingredient_db_test'
    
    # Internet of Food config
    INOF_BASE = 'http://localhost:81/api/'
    APPLICATION_BASE = 'http://localhost:5002/api/'


class DockerDeployConfiguration(BaseConfiguration):
    # SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@db-container:5432/ingredient_db'

    # Internet of Food config
    #INOF_BASE = 'http://internet-of-food.win.tue.nl:81/api/' # <- for external deployment
    #APPLICATION_BASE = 'http://data-access-gateway:5002/api/' # <- change if hosted on other machine
    INOF_BASE = 'http://model-sharing-backend:81/api/'

    TESTING = False
    DEBUG = False
    ENV = 'production'


DefaultConfiguration: BaseConfiguration = BaseConfiguration()
