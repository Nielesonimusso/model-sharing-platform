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
    ONTOLOGY_PREFIX = "IngredientSource"

    # flask config
    TESTING = False
    SECRET_KEY = str(os.urandom(32))
    DEBUG = True
    ENV = 'development'

    # # SQLAlchemy config
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@localhost:5432/ingredient_db'
    # SQLALCHEMY_ECHO = False


class TestConfiguration(BaseConfiguration):
    SECRET_KEY = 's3cr3t_k3y'
    DEBUG = True
    # SQLALCHEMY_ECHO = True
    # SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@localhost:5432/ingredient_db_test'


class DockerDeployConfiguration(BaseConfiguration):
    # SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@db-container:5432/ingredient_db'

    TESTING = False
    DEBUG = False
    ENV = 'production'


DefaultConfiguration: BaseConfiguration = BaseConfiguration()
