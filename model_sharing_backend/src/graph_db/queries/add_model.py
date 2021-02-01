import uuid
from typing import List

from common_data_access import string_utils
from model_sharing_backend.src.graph_db.model_data_structure import GraphDbModelParameter, GraphDbModel
from model_sharing_backend.src.graph_db.queries.property_uris import description_property_uri, label_property_uri
from model_sharing_backend.src.graph_db.queries.query_runner import SparQlRunner

__inofm_prefix = 'http://www.foodvoc.org/resource/InternetOfFoodModel/'


def add_model(model_name: str, input_parameters: List[GraphDbModelParameter],
              output_parameters: List[GraphDbModelParameter], client: SparQlRunner) -> GraphDbModel:
    model_unique_name = _add_model_only(model_name, client)
    _add_parameters(model_unique_name, input_parameters, output_parameters, client)
    return GraphDbModel(model_name, input_parameters or [],
                        output_parameters or [], f'{__inofm_prefix}{model_unique_name}')


def _get_unit_uri(unit):
    return unit.uri


def _add_parameters(model_unique_name: str, input_params: List[GraphDbModelParameter],
                    output_params: List[GraphDbModelParameter], client: SparQlRunner):
    query = f'''
    prefix : <{__inofm_prefix}> 
    prefix dcterms: <http://purl.org/dc/terms/> 
    prefix inofm: <{__inofm_prefix}> 
    prefix om: <http://www.ontology-of-units-of-measure.org/resource/om-2/> 
    prefix owl: <http://www.w3.org/2002/07/owl#> 
    prefix prov: <http://www.w3.org/ns/prov/>
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    prefix skos: <http://www.w3.org/2004/02/skos/core#> 
    prefix xsd: <http://www.w3.org/2001/XMLSchema#> 
    INSERT DATA {{'''

    for param_type, params in [('inofm:hasInput', input_params), ('inofm:hasOutput', output_params)]:
        for p in params:
            unit_uri = _get_unit_uri(p.unit)
            param_unique_name = _create_unique_name(p.labels[0].name)
            query += f'inofm:{param_unique_name} rdf:type skos:Concept . \n'
            for l in p.labels:
                query += f'inofm:{param_unique_name} rdfs:label "{l.name}"@{l.language} . \n'

            query += f'''
                inofm:{model_unique_name} {param_type} inofm:massOf{param_unique_name} .
                inofm:massOf{param_unique_name} <{description_property_uri}> "{p.description}"@en .
                inofm:massOf{param_unique_name} rdf:type om:MassFraction .
                inofm:massOf{param_unique_name} om:hasPhenomenon inofm:{param_unique_name} .
                inofm:massOf{param_unique_name} om:hasUnit <{unit_uri}> .
                <{unit_uri}> rdf:type om:Unit .
                <{unit_uri}> <{label_property_uri}> "{p.unit.label.name}" .'''
    query += '}'
    return client.write(query)


def _add_model_only(name: str, client: SparQlRunner) -> str:
    unique_name = _create_unique_name(name)
    query = f'''
    prefix : <{__inofm_prefix}> 
    prefix dcterms: <http://purl.org/dc/terms/> 
    prefix inofm: <{__inofm_prefix}> 
    prefix om: <http://www.ontology-of-units-of-measure.org/resource/om-2/> 
    prefix owl: <http://www.w3.org/2002/07/owl#> 
    prefix prov: <http://www.w3.org/ns/prov/>
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    prefix skos: <http://www.w3.org/2004/02/skos/core#> 
    prefix xsd: <http://www.w3.org/2001/XMLSchema#> 
    INSERT DATA {{ 
        inofm:{unique_name} rdf:type inofm:Model .
        inofm:{unique_name} inofm:hasID "{name}"@en .
    }}'''
    client.write(query)
    return unique_name


def _create_unique_name(name: str) -> str:
    return f'{string_utils.to_camel_case(name)}{uuid.uuid4()}'
