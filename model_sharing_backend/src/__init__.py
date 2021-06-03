import os
import traceback

from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flasgger import APISpec, Swagger
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager

from model_sharing_backend.src.models import initialize_db_connections
from .config import BaseConfiguration, TestConfiguration, DockerDeployConfiguration


def create_app() -> Flask:
    app = Flask(__name__)
    configuration = select_configuration()
    app.config.from_object(configuration)
    configure_jwt(app)
    initialize_db_connections(app)
    setup_cli(app)
    setup_global_error_handlers(app)
    register_blueprints(app)
    setup_api_specifications(app, configuration)
    configure_response(app)
    return app


def select_configuration():
    run_config_name = os.environ.get('INOF_RUN_CONFIG', 'debug').strip()
    config_map = dict(debug=BaseConfiguration, test=TestConfiguration, deploy=DockerDeployConfiguration)
    conf = config_map.get(run_config_name, BaseConfiguration)
    print(f'Choose configuration {run_config_name}: {conf.__name__}')
    return conf


def configure_jwt(app: Flask):
    jwt = JWTManager(app)

    @jwt.invalid_token_loader
    def my_expired_token_callback(expired_token):
        return jsonify({
            'status': 401,
            'sub_status': 422,
            'msg': f'The auth token is not valid. {expired_token}'
        }), 401

    @jwt.user_loader_callback_loader
    def get_current_user(identity):
        from model_sharing_backend.src.models.user import User
        return User.query.get_one_where(User.username == identity['username'])


def register_blueprints(app):
    from model_sharing_backend.src.routes.model_routes import model_bp
    from model_sharing_backend.src.routes.product_routes import products_bp
    from model_sharing_backend.src.routes.simulation_routes import simulation_bp
    from model_sharing_backend.src.routes.user_routes import user_bp
    from model_sharing_backend.src.routes.authorization import auth_bp
    from model_sharing_backend.src.routes.company_routes import company_bp
    from model_sharing_backend.src.routes.data_source_routes import data_source_bp

    app.register_blueprint(products_bp, url_prefix='/api')
    app.register_blueprint(model_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(simulation_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(company_bp, url_prefix='/api')
    app.register_blueprint(data_source_bp, url_prefix='/api')


def configure_response(app: Flask):
    # enable CORS
    from flask_cors import CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}, send_wildcard=True)

    @app.after_request
    def after_request(response):
        # response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response


# noinspection PyArgumentList
def setup_api_specifications(app: Flask, configuration: BaseConfiguration):
    from model_sharing_backend.src.models import get_schema_classes
    spec = APISpec(title=configuration.SWAGGER_TITLE,
                   openapi_version=configuration.SWAGGER_VERSION,
                   version=configuration.APPLICATION_VERSION,
                   plugins=[MarshmallowPlugin(), FlaskPlugin()])
    spec.components.security_scheme('bearer', {'type': 'apiKey', 'name': 'Authorization', 'in': 'header'})
    template = spec.to_flasgger(app, definitions=get_schema_classes())
    Swagger(app, template=template)


def setup_cli(app: Flask):
    """Hookup methods with custom flask cli commands. Type ``flask --help`` to see these options."""

    @app.cli.command('seed-db')
    def seed_db():
        """Initialized the database with model data."""
        from model_sharing_backend.src.models.db_initialize import ModelDbInitialize
        ModelDbInitialize().create_database(True)

        # seed graph db
        from model_sharing_backend.src.graph_db.seed.seed import seed_graph_db_with_inof_ontology
        seed_graph_db_with_inof_ontology(app.config['GRAPH_DB_SERVER_URL'], app.config['GRAPH_DB_REPOSITORY_ID'])

    @app.cli.command('cache-om')
    def cache_om_to_redis():
        """Cache Ontology of Measurement (OM) on Redis (requires redis server on localhost:6379)"""
        from unit_translation_component import cache_units
        print('caching OM on redis!')
        cache_units()
        print('OM caching complete!')


def setup_global_error_handlers(app: Flask):
    from werkzeug.exceptions import HTTPException
    from marshmallow.exceptions import ValidationError

    @app.errorhandler(ValueError)
    def handle_http_error(e: ValueError):
        return jsonify(str(e)), 400

    @app.errorhandler(ValidationError)
    def handle_http_error(e: ValidationError):
        return jsonify(e.messages), 400

    @app.errorhandler(HTTPException)
    def handle_http_error(e: HTTPException):
        response = {'code': e.code, 'description': e.description}
        return jsonify(response), e.code

    @app.errorhandler(Exception)
    def handle_generic(e: Exception):
        original = getattr(e, "original_exception", e)

        if app.config.get('DEBUG'):
            return traceback.format_exc(), 500

        # wrapped unhandled error
        return f'{original.__class__.__name__} occurred', 500
