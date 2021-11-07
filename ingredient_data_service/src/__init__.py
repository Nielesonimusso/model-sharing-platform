import os

from flask import Flask

from .config import DefaultConfiguration, BaseConfiguration, TestConfiguration, DockerDeployConfiguration
from .data import initialize_db_connections


def create_app() -> Flask:
    app = Flask(__name__)
    configuration = select_configuration()
    app.config.from_object(configuration)

    initialize_db_connections(app)
    setup_cli(app)

    from ingredient_data_service.src.routes import routes_blueprint
    app.register_blueprint(routes_blueprint, url_prefix='/api')

    # just initialize the database
    from ingredient_data_service.src.data.db_init import IngredientDbInitialize
    IngredientDbInitialize().create_database(True, data_file_path=DefaultConfiguration.INGREDIENT_FILE_PATH)

    return app


def setup_cli(app: Flask):
    """Hookup methods with custom flask cli commands. Type ``flask --help`` to see these options."""

    @app.cli.command('seed-db')
    def seed_db():
        """Initialized the database with ingredient data."""
        from ingredient_data_service.src.data.db_init import IngredientDbInitialize
        IngredientDbInitialize().create_database(True, data_file_path=DefaultConfiguration.INGREDIENT_FILE_PATH)


def select_configuration():
    run_config_name = os.environ.get('INOF_RUN_CONFIG', 'debug').strip()
    config_map = dict(debug=BaseConfiguration, test=TestConfiguration, deploy=DockerDeployConfiguration)
    conf = config_map.get(run_config_name, DefaultConfiguration)
    print(f'Starting with configuration {conf.__name__}')
    return conf
