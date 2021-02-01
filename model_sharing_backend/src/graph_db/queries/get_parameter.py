from typing import List

from model_sharing_backend.src.graph_db.model_data_structure import GraphDbModelParameter, Label, Unit
from model_sharing_backend.src.graph_db.queries.query_runner import SparQlRunner
from . import property_uris

__query = '''
select * 
where {{ 
    ?item ?property ?value  
    filter(?item=<{uri}>)
}}'''


def get_parameter(uri: str, client: SparQlRunner) -> GraphDbModelParameter:
    q = __query.format(uri=uri)
    results = client.read(q)
    labels, unit, description = ([], None, '')
    for res in results:
        if res.property.value == property_uris.has_phenomenon_property_uri:
            labels.extend(get_labels_from_phenomenon(res.value.value, client))
        elif res.property.value == property_uris.has_unit_uri:
            unit = get_unit(res.value.value, client)
        elif res.property.value == property_uris.description_property_uri:
            description = res.value.value
    return GraphDbModelParameter(labels, description, unit)


def get_labels_from_phenomenon(phenomenon_uri: str, client: SparQlRunner) -> List[Label]:
    q = __query.format(uri=phenomenon_uri)
    results = client.read(q)
    labels = filter(lambda r: r.property.value == property_uris.label_property_uri, results)
    return list(map(lambda l: Label(l.value.value, l.value.language), labels))


def get_unit(uri: str, client: SparQlRunner) -> Unit:
    q = __query.format(uri=uri)
    results = client.read(q)
    label_res = filter(lambda r: r.property.value == property_uris.label_property_uri, results)
    labels = map(lambda l: Label(l.value.value, l.value.language), label_res)
    return Unit(uri, next(labels))
