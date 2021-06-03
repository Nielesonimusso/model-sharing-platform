import os
import json

class BaseConfiguration():
    # application config
    PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))
    DATA_SOURCE_FILE_PATHS = [os.path.join(os.path.abspath(os.path.dirname(__file__)), p) for p in 
        os.getenv('DATA_SOURCE_FILE_PATHS', 
            'data/IngredientDatabase.csv,data/IngredientPropertyDatabase.csv').split(',')]
    # DATA_SOURCE_FILE_PATHS = [os.path.join(PACKAGE_PATH, 'data/IngredientDatabase.csv'), 
        # os.path.join(PACKAGE_PATH, 'data/IngredientPropertyDatabase.csv')]
    COLUMN_TYPES = json.loads(os.getenv('COLUMN_TYPES',
        json.dumps([dict(Ingredient='str', IngredientCode='str'), 
                    dict(Ingredient='str',IngredientCode='str',IngredientProperty='str',
                            ValueText='str',ValueNum='float',UnitOfMeasure='str')])))
    # COLUMN_TYPES = [dict(Ingredient=str, IngredientCode=str), 
        # dict(Ingredient=str,IngredientCode=str,IngredientProperty=str,
            # ValueText=str,ValueNum=float,UnitOfMeasure=str)]
    ONTOLOGY_FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.getenv('ONTOLOGY_FILE_PATH', 'data/test-ontology.ttl'))
    # APPLICATION_BASE = 'http://data-access-gateway:5001'
    APPLICATION_BASE = os.getenv('APPLICATION_BASE', 'http://localhost:5020')
    ACCESS_PRICE = float(os.getenv('ACCESS_PRICE', '3'))

    # flask config
    TESTING = False
    SECRET_KEY = str(os.urandom(32))
    DEBUG = True
    ENV = 'development'

    # Internet of Food config
    #INOF_BASE = 'http://model-sharing-backend:5020'
    INOF_BASE = os.getenv('INOF_BASE', 'http://localhost:81')
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
    INOF_BASE = os.getenv('INOF_BASE', 'http://localhost:81')
    APPLICATION_BASE = os.getenv('APPLICATION_BASE', 'http://localhost:5020')


class DockerDeployConfiguration(BaseConfiguration):
    # SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@db-container:5432/ingredient_db'

    # Internet of Food config
    #INOF_BASE = 'http://internet-of-food.win.tue.nl:81/api/' # <- for external deployment
    #APPLICATION_BASE = 'http://data-access-gateway:5002/api/' # <- change if hosted on other machine
    INOF_BASE = os.getenv('INOF_BASE', 'http://model-sharing-backend:81')

    # TESTING = False
    # DEBUG = False
    ENV = 'production'


DefaultConfiguration: BaseConfiguration = BaseConfiguration()
