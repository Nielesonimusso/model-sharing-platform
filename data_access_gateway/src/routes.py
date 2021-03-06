from flask import Blueprint, make_response, request, jsonify, current_app

from common_data_access.json_extension import get_json
from .data.data_source import get_data_sources

routes_blueprint = Blueprint('data_access_gateway', __name__)

@routes_blueprint.route('/<data_source>/data.json', methods=['GET'])
def get_data(data_source: str):
    data_source_object = get_data_sources(current_app)[data_source]
    columns = tuple(request.args.getlist('columns')) or data_source_object.get_field_names()
    unique = bool(request.args.get('unique'))
    # output = get_json(get_data_source().get_ingredient_properties(), IngredientPropertyCompleteDtoSchema, None, columns, unique)
    output = jsonify(data_source_object.get_rows(columns, unique))
    return output

@routes_blueprint.route('/<data_source>/ontology.ttl', methods=['GET'])
def get_ontology(data_source: str):
    data_source_object = get_data_sources(current_app)[data_source]
    response = make_response(data_source_object.get_ontology(), 200)
    response.mimetype = 'text/turtle'
    return response
