import sys
from typing import Type
import rdflib
from rdflib.graph import Graph
from rdflib.namespace import Namespace

import requests
from requests.exceptions import RequestException

from common_data_access.dtos import GatewayPaths, ModelResultDtoSchema, ModelRunStatusDtoSchema
from model_sharing_backend.src.models.simulation import ModelRunStatusWithModelIdDtoSchema
from model_sharing_backend.src.ontology_services.data_structures import ArgumentDefinition, ColumnDefinition, ModelInterfaceDefinition, TableDefinition


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
    
def fetch_data_source_metadata(gateway_url: str, ontology_uri: str) -> TableDefinition:
    return __parse_graph_node(__load_graph(gateway_url+'/ontology.ttl'),
        ontology_uri, TableDefinition)

def fetch_argument_definition(gateway_url: str, ontology_uri: str) -> ArgumentDefinition:
    return __parse_graph_node(__load_graph(gateway_url+'/ontology.ttl'),
        ontology_uri, ArgumentDefinition)

def fetch_model_interface_definition(gateway_url: str, ontology_uri: str) -> ModelInterfaceDefinition:
    return __parse_graph_node(__load_graph(gateway_url+'/ontology.ttl'),
        ontology_uri, ModelInterfaceDefinition)

def __parse_graph_node(graph: Graph, ontology_uri: str, node_type: Type):
    return node_type.from_graph(graph, rdflib.URIRef(ontology_uri))

def __load_graph(graph_url: str) -> Graph:
    graph = rdflib.Graph().parse(location=graph_url, format="turtle")
    # TODO potentially handle imports if those are encountered
    
    # add namespaces used in queries
    SERVICE = Namespace('http://www.foodvoc.org/resource/InternetOfFood/Service/')
    TABLE = Namespace('http://www.foodvoc.org/resource/InternetOfFood/Table/')
    OM = Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')
    OMX = Namespace('http://www.foodvoc.org/resource/InternetOfFood/omx/')
    OWL3 = Namespace('http://www.foodvoc.org/resource/InternetOfFood/OntologyWebLanguage/') # BUG IMAGINARY OWL

    graph.namespace_manager.bind('service', SERVICE)
    graph.namespace_manager.bind('table', TABLE)
    graph.namespace_manager.bind('om', OM)
    graph.namespace_manager.bind('omx', OMX)
    graph.namespace_manager.bind('owl3', OWL3)

    return graph

def __make_request(url: str, method: any, **kwargs):
    try:
        response = method(url, timeout=5, **kwargs)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, requests.HTTPError) as e:
        print(e, file=sys.stderr)
        raise e
