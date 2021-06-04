import atexit
from functools import partial
import os
import traceback
from typing import Dict

from flask import Flask, jsonify
import requests
from requests.exceptions import RequestException
from common_data_access.api_utils import api_authorization_header

from common_data_access.db import create_db_connection
from model_access_gateway.src.models.model import Model
from model_access_gateway.src.models.nutrition_model import NutritionModel
from model_access_gateway.src.models.tomato_soup_taste_model import TasteModel
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

    register_model(app)

    setup_cli(app)
    # seed_db_init()
    setup_global_error_handlers(app)
    return app

def get_model(app) -> Model:
    global __model__
    if '__model__' not in globals():
        models: Dict[str, Model] = dict(
            taste=TasteModel(app.config.get('TASTES_TO_CALCULATE', None)),
            nutrition=NutritionModel(),
            pasteurization=None,
            shelflife=None,
            calibration=None,
            dropletsize=None
        )

        __model__ = models.get(app.config['MODEL'])

    return __model__

def register_model(app: Flask):
    if auth_token_header := api_authorization_header(app):
        application_base = app.config['APPLICATION_BASE']

        model = get_model(app)

        inof_base = app.config['INOF_BASE']
        api_check_endpoint = inof_base + '/api/own_models'
        api_register_endpoint = inof_base + '/api/model'
        try:
            check = requests.get(api_check_endpoint, headers=auth_token_header).json()
            existing = [a for a in check if a["gateway_url"] == application_base]

            model_info = dict(
                name=model.name,
                description=model.description,
                price=model.price,
                is_connected=True,
                gateway_url=application_base,
                ontology_uri=application_base + '/api/ontology.ttl#' + type(model).__name__
            )

            if len(existing) > 0:
                print(requests.put(api_register_endpoint + '/' + existing[0]["id"], 
                    json = model_info, headers=auth_token_header).json())
                model.id = existing[0]['id']
                print('updated model')
            else:
                print(post_result := requests.post(api_register_endpoint, 
                    json=model_info, headers=auth_token_header).json())
                model.id = post_result['id']
                print('registered model')
        except RequestException as ex:
            print("Could not register model ")

    # register deregistration endpoint as well
    atexit.register(partial(deregister_on_exit, app))

def deregister_on_exit(app: Flask):
    if auth_token_header := api_authorization_header(app):
        application_base = app.config['APPLICATION_BASE']

        model = get_model(app)

        inof_base = app.config['INOF_BASE']
        api_update_endpoint = inof_base + '/api/model/'
        try:
            print(requests.put(api_update_endpoint + model.id, json = dict(
                name=model.name,
                description=model.description,
                price=model.price,
                is_connected=False,
                gateway_url=application_base,
                ontology_uri=application_base + '/api/ontology.ttl#' + type(model).__name__
            ), headers=auth_token_header).json())
        except RequestException as ex:
            print("Could not update connected state of model")


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
