import os
import traceback

from flask import Flask, jsonify

from common_data_access.db import create_db_connection
from .config import DefaultConfiguration, BaseConfiguration, TestConfiguration, DockerDeployConfiguration


def select_configuration():
    run_config_name = os.environ.get('INOF_RUN_CONFIG', 'debug').strip()
    config_map = dict(debug=BaseConfiguration, test=TestConfiguration, deploy=DockerDeployConfiguration)
    conf = config_map.get(run_config_name, BaseConfiguration)
    print(f'Choose configuration {conf.__name__}')
    return conf


def create_app() -> Flask:
    conf = select_configuration()
    app = Flask(__name__)
    app.config.from_object(conf)
    create_db_connection(app)
    from .routes import routes_blueprint
    app.register_blueprint(routes_blueprint, url_prefix='/api')
    setup_cli(app)
    # seed_db_init()
    setup_global_error_handlers(app)
    return app

def seed_db_init():
    from .db import GatewayDbInitialize
    GatewayDbInitialize().create_database(True)

def setup_cli(app: Flask):
    """Hookup methods with custom flask cli commands. Type ``flask --help`` to see these options."""

    @app.cli.command('seed-db')
    def seed_db():
        """Initialized the gateway database."""
        from .db import GatewayDbInitialize
        GatewayDbInitialize().create_database(True)



def setup_global_error_handlers(app: Flask):
    from werkzeug.exceptions import HTTPException
    from marshmallow.exceptions import ValidationError

    @app.errorhandler(ValidationError)
    def handle_http_error(e: ValidationError):
        return jsonify(e.messages), 400

    @app.errorhandler(HTTPException)
    def handle_http_error(e: HTTPException):
        response = {'code': e.code, 'description': e.description}
        return jsonify(response), e.code

    @app.errorhandler(Exception)
    def handle_generic(e: Exception):
        original = getattr(e, 'original_exception', e)

        if app.config.get('DEBUG'):
            return traceback.format_exc(), 500

        # wrapped unhandled error
        return f'{original.__class__.__name__} occurred', 500
