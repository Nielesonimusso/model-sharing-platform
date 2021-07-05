import os
import requests
from functools import partial
import atexit

from flask import Flask
from requests.exceptions import RequestException

from common_data_access.api_utils import api_authorization_header

from .config import DefaultConfiguration, BaseConfiguration, TestConfiguration, DockerDeployConfiguration
from .data.data_source import get_data_sources
# from .data import initialize_db_connections


def create_app() -> Flask:
    app = Flask(__name__)
    configuration = select_configuration()
    app.config.from_object(configuration)

    get_data_sources(app)
    # register_data_sources(app)

    # enable CORS
    from flask_cors import CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}, send_wildcard=True)

    setup_cli(app)
    app.config["REGISTERED"] = False
    register_data_sources(app)
    # register deregistration endpoint as well
    # atexit.register(partial(deregister_on_exit, app))

    from data_access_gateway.src.routes import routes_blueprint
    app.register_blueprint(routes_blueprint, url_prefix='/api')

    return app


def setup_cli(app: Flask):
    """Hookup methods with custom flask cli commands. Type ``flask --help`` to see these options."""

    @app.cli.command('seed-db')
    def seed_db():
        register_data_sources(app)
    #     """Initialized the database with ingredient data."""
    #     from data_access_gateway.src.data.db_init import DataGatewayDbInitialize
    #     DataGatewayDbInitialize().create_database(True, data_file_path=DefaultConfiguration.DATA_SOURCE_FILE_PATH)


def select_configuration():
    run_config_name = os.environ.get('INOF_RUN_CONFIG', 'debug').strip()
    config_map = dict(debug=BaseConfiguration, test=TestConfiguration, deploy=DockerDeployConfiguration)
    conf = config_map.get(run_config_name, DefaultConfiguration)
    print(f'Starting with configuration {conf.__name__}')
    return conf


def register_data_sources(app: Flask):

    if auth_token_header := api_authorization_header(app):
        application_base = app.config['APPLICATION_BASE'] + '/api/'

        # one request for every data source
        price = app.config['ACCESS_PRICE']
        inof_base = app.config['INOF_BASE']
        api_check_endpoint = inof_base + '/api/own_data_sources'
        api_register_endpoint = inof_base + '/api/data_source'

        data_sources = get_data_sources(app)
        for data_source_name, data_source in data_sources.items():
            try:
                check = requests.get(api_check_endpoint, headers=auth_token_header).json()
                existing = [a for a in check if a["gateway_url"] == application_base + data_source_name]

                data_source_info = dict(
                            name = data_source_name,
                            price = price,
                            is_connected = True,
                            gateway_url = application_base + data_source_name,
                            ontology_uri = application_base + data_source_name + '/ontology.ttl#' + data_source_name
                )

                if len(existing) > 0:
                    print(requests.put(api_register_endpoint + '/' + existing[0]["id"], json = data_source_info, 
                        headers=auth_token_header).json())
                    data_source.id = existing[0]["id"]
                    print(f'updated {data_source_name}')
                else:
                    print(post_result := requests.post(api_register_endpoint, json = data_source_info, 
                        headers=auth_token_header).json())
                    data_source.id = post_result["id"]
                    print(f'registered {data_source_name}')
            except RequestException as ex:
                print(f"Could not register datasource {data_source_name}")
        
        app.config["REGISTERED"] = True
        

def deregister_on_exit(app: Flask):
    if app.config["REGISTERED"] and (auth_token_header := api_authorization_header(app)):
        api_update_endpoint = app.config['INOF_BASE'] + '/api/data_source/'
        price = app.config['ACCESS_PRICE']
        application_base = app.config['APPLICATION_BASE'] + '/api/'

        data_sources = get_data_sources(app)
        for data_source_name, data_source in data_sources.items():
            try:
                print(requests.put(api_update_endpoint + data_source.id, json = dict(
                    name = data_source_name,
                    price = price,
                    is_connected = False,
                    gateway_url = application_base + data_source_name,
                    ontology_uri = application_base + data_source_name + '/ontology.ttl#' + data_source_name
                ), headers=auth_token_header).json())
            except RequestException as ex:
                print(f"Could not update connected state of data source {data_source_name}")
