from flask import Blueprint, request, jsonify
from flask.helpers import make_response
from flask_jwt_extended import jwt_required, current_user
from marshmallow.exceptions import ValidationError
import rdflib

import requests
from datetime import datetime

from common_data_access.json_extension import get_json
from model_sharing_backend.src.models.data_source_info import DataSourceInfo, DataSourceInfoWithTableDbSchema, \
    DataSourcePermission, DataSourcePermissionTypes
from model_sharing_backend.src.ontology_services.data_structures import TableDefinition, TableDefinitionSchema
from model_sharing_backend.src.utils.gateway_service import fetch_data_source_data

data_source_bp = Blueprint('DataSources', __name__)

@data_source_bp.route('/data_source', methods=['POST'])
@jwt_required
def create_data_source():
    """
    Create new data source
    ---
    tags:
        -   Data Source
    security:
        -   bearer: []
    parameters:
        -   name: datasource
            in: body
            description: information about the datasource
            required: true
            schema:
                $ref: '#/definitions/DataSourceInfoDbSchema'
    responses:
        201:
            description: Created a new data source
            schema:
                $ref: '#/definitions/DataSourceInfoDbSchema'
    """

    data_source_info = DataSourceInfo.DataSourceInfoDbSchema().load(request.json)

    data_source_info.owner = current_user.company
    data_source_info.created_on = datetime.utcnow()
    data_source_info.created_by = current_user

    data_source_info.add()

    return get_json(data_source_info, DataSourceInfo.DataSourceInfoDbSchema, 
        {'company_id': current_user.company.id})

@data_source_bp.route('/data_source/<data_source_id>', methods=['PUT'])
@jwt_required
def update_data_source(data_source_id: str):
    data_source_info_db = DataSourceInfo.query.get_created_by_or_404(current_user.id, data_source_id)
    data_source_info_new = DataSourceInfo.DataSourceInfoDbSchema().load(request.json)

    data_source_info_db.name = data_source_info_new.name
    data_source_info_db.price = data_source_info_new.price
    data_source_info_db.is_connected = data_source_info_new.is_connected
    data_source_info_db.gateway_url = data_source_info_new.gateway_url
    data_source_info_db.ontology_uri = data_source_info_new.ontology_uri
    
    data_source_info_db = data_source_info_db.update()
    return get_json(data_source_info_db, DataSourceInfo.DataSourceInfoDbSchema,
        {'company_id': current_user.company_id})

@data_source_bp.route('/data_source/<data_source_id>', methods=['DELETE'])
@jwt_required
def delete_data_source(data_source_id: str):
    data_source_info = DataSourceInfo.query.get_created_by_or_404(current_user.id, data_source_id)
    # TODO maybe: dont delete if already used in a simulation? (see model_routes)
    data_source_info.delete()
    return jsonify()

@data_source_bp.route('/data_sources', methods=['GET'])
@jwt_required
def get_data_sources():
    return get_json(DataSourceInfo.query.get_all_accessible_by(current_user.company_id),
                    DataSourceInfo.DataSourceInfoDbSchema, {'company_id': current_user.company_id})


@data_source_bp.route('/own_data_sources', methods=['GET'])
@jwt_required
def get_own_data_sources():
    return get_json(DataSourceInfo.query.get_all_owned_by(current_user.company_id),
                    DataSourceInfo.DataSourceInfoDbSchema, {'company_id': current_user.company_id})

@data_source_bp.route('/data_source/<data_source_id>', methods=['GET'])
@jwt_required
def get_data_source(data_source_id: str):
    data_source_info = DataSourceInfo.query.get_created_by_or_404(current_user.id, data_source_id)

    # include datasource table 
    data_source_table = TableDefinition.from_graph(
        rdflib.Graph().parse(location=data_source_info.gateway_url+'/ontology.ttl', format="turtle"),
        rdflib.URIRef(data_source_info.ontology_uri))

    data_source_info_table = DataSourceInfo.DataSourceInfoDbSchema(context={'company_id': current_user.company_id}).dump(data_source_info)
    data_source_info_table.update(TableDefinitionSchema().dump(data_source_table))

    if len(val_errors := DataSourceInfoWithTableDbSchema().validate(data_source_info_table)) == 0:
        return jsonify(data_source_info_table)
    else:
        raise ValidationError(val_errors)

@data_source_bp.route('/data_source/data/<data_source_id>', methods=['GET'])
@jwt_required
def get_data_source_data(data_source_id: str):
    data_source_info = DataSourceInfo.query.get_created_by_or_404(current_user.id, data_source_id)
    return jsonify(fetch_data_source_data(data_source_info.gateway_url))


@data_source_bp.route('/data_source/permissions/<data_source_id>', methods=['PUT'])
@jwt_required
def set_data_source_permissions(data_source_id: str):
    data_source_permissions = DataSourcePermission.DataSourcePermissionDtoSchema(exclude=['data_source_info_id'], many=True).load(request.json)
    data_source_info = DataSourceInfo.query.get_created_by_or_404(current_user.id, data_source_id)

    unique_permissions = {}
    for p in data_source_permissions:
        company_permission = unique_permissions.get(p.company_id, set())
        company_permission.add(p.permission_type)
        unique_permissions[p.company_id] = company_permission

    data_source_info.permissions = []
    for company_id, permissions in unique_permissions.items():
        for permission_type in permissions:
            data_source_info.permissions.append(DataSourcePermission(
                data_source_info_id=data_source_id,
                company_id=company_id,
                permission_type=DataSourcePermissionTypes(permission_type)))

    data_source_info.save()
    return get_json(data_source_info.permissions, DataSourcePermission.DataSourcePermissionDtoSchema)


@data_source_bp.route('/data_source/permissions/<data_source_id>', methods=['GET'])
@jwt_required
def get_data_source_permissions(data_source_id: str):
    return get_json(DataSourceInfo.query.get_owned_or_404(current_user.company_id, data_source_id).permissions,
                    DataSourcePermission.DataSourcePermissionDtoSchema)