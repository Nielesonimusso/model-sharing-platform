from itertools import groupby
from typing import List

from model_sharing_backend.src.graph_db.queries import property_uris
from model_sharing_backend.src.graph_db.queries.get_parameter import get_parameter
from model_sharing_backend.src.graph_db.model_data_structure import GraphDbModel
from model_sharing_backend.src.graph_db.queries.query_runner import SparQlRunner


def get_model(uri: str, client: SparQlRunner) -> GraphDbModel:
    query = '''
    PREFIX : <http://www.foodvoc.org/resource/InternetOfFoodModel/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select * where {{
    	?item rdf:type :Model .
        ?item ?property ?value
        filter(?item=<{model_uri}>)
    }}'''

    q = query.format(model_uri=uri)
    results = client.read(q)
    return __query_result_to_model_obj(client, results, uri)


def get_all_models(client: SparQlRunner) -> List[GraphDbModel]:
    query = '''
    PREFIX : <http://www.foodvoc.org/resource/InternetOfFoodModel/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    select * where { 
    	?item rdf:type :Model .
        ?item ?property ?value
    }'''
    query_results = client.read(query)
    grouped_by_model_uri = groupby(query_results, lambda r: r.item.value)
    models = []
    for m_uri, grp in grouped_by_model_uri:
        models.append(__query_result_to_model_obj(client, grp, m_uri))
    return models


def __query_result_to_model_obj(client, results, uri):
    inputs, outputs, name = [], [], ''
    for r in results:
        if r.property.value == property_uris.id_property_uri:
            name = r.value.value
        elif r.property.value == property_uris.input_property_uri:
            inputs.append(get_parameter(r.value.value, client))
        elif r.property.value == property_uris.output_property_uri:
            outputs.append(get_parameter(r.value.value, client))
    return GraphDbModel(name, inputs, outputs, uri)
