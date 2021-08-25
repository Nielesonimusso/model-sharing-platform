import sys
import rdflib
from rdflib.namespace import Namespace

import requests
from requests.exceptions import RequestException

from common_data_access.dtos import GatewayPaths, ModelResultDtoSchema, ModelRunStatusDtoSchema
from model_sharing_backend.src.models.simulation import ModelRunStatusWithModelIdDtoSchema
from model_sharing_backend.src.ontology_services.data_structures import TableDefinition


def request_model_run(gateway_url: str, data: any):
    try:
        response_json = __make_request(f'{gateway_url.rstrip("/")}/{GatewayPaths.model_run}', requests.post, json=data)
        return ModelRunStatusDtoSchema().load(response_json)
    except requests.RequestException as e:
        print(f'error while communicating {gateway_url}. {str(e)}', file=sys.stdout)
        raise e


def get_model_run_result(gateway_url: str, run_id: str):
    try:
        response_json = __make_request(f'{gateway_url.rstrip("/")}/{GatewayPaths.model_result}/{run_id}', requests.get)
        return ModelResultDtoSchema().load(response_json)
    except requests.RequestException as e:
        print(f'error while communicating {gateway_url}. {str(e)}', file=sys.stdout)
        raise e


def get_model_run_status(gateway_url: str, run_id: str):
    try:
        response_json = __make_request(f'{gateway_url.rstrip("/")}/{GatewayPaths.model_status}/{run_id}', requests.get)
        return ModelRunStatusWithModelIdDtoSchema().load(response_json)
    except requests.RequestException as e:
        print(f'error while communicating {gateway_url}. {str(e)}', file=sys.stdout)
        raise e


def fetch_data_source_data(gateway_url: str):
    try:
        return __make_request(f'{gateway_url.rstrip("/")}/data.json', requests.get)
    except requests.RequestException as e:
        print(f'error while communicating {gateway_url}. {str(e)}', file=sys.stdout)
        raise e
    
def fetch_data_source_metadata(gateway_url: str, ontology_uri: str):
    try:
        data_source_graph = rdflib.Graph().parse(location=gateway_url+'/ontology.ttl', format="turtle")
        # TODO potentially handle imports if those are encountered
        
        # add namespaces used in queries
        SERVICE = Namespace('http://www.foodvoc.org/resource/InternetOfFood/Service/')
        TABLE = Namespace('http://www.foodvoc.org/resource/InternetOfFood/Table/')
        OM = Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')
        OMX = Namespace('http://www.foodvoc.org/resource/InternetOfFood/omx/')
        OWL3 = Namespace('http://www.foodvoc.org/resource/InternetOfFood/OntologyWebLanguage/') # BUG IMAGINARY OWL

        data_source_graph.namespace_manager.bind('service', SERVICE)
        data_source_graph.namespace_manager.bind('table', TABLE)
        data_source_graph.namespace_manager.bind('om', OM)
        data_source_graph.namespace_manager.bind('omx', OMX)
        data_source_graph.namespace_manager.bind('owl3', OWL3)

        return TableDefinition.from_graph(data_source_graph, 
            rdflib.URIRef(ontology_uri))
    except requests.RequestException as e:
        raise e


def __make_request(url: str, method: any, **kwargs):
    try:
        response = method(url, timeout=5, **kwargs)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, requests.HTTPError) as e:
        print(e, file=sys.stderr)
        raise e
