from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user
from marshmallow import ValidationError
import rdflib
from rdflib.namespace import OWL
from rdflib.term import URIRef
from werkzeug.exceptions import abort

from common_data_access.json_extension import get_json
from model_sharing_backend.src.graph_db.model_data_structure import GraphDbModel, GraphDbModelSchema
from model_sharing_backend.src.graph_db.queries import query_model
from model_sharing_backend.src.graph_db.queries.add_model import add_model
from model_sharing_backend.src.graph_db.queries.query_runner import SparQlRunner
from model_sharing_backend.src.models.model_info import ModelInfo, ModelPermission, ModelPermissionDtoSchema, \
    ModelPermissionTypes, ModelInfoWithParametersDtoSchema
from model_sharing_backend.src.ontology_services.data_structures import ModelInterfaceDefinition, ModelInterfaceDefinitionSchema

model_bp = Blueprint('Models', __name__)


@model_bp.route('/model', methods=['POST'])
@jwt_required
def create_model():
    """
    Create new model
    ---
    tags:
        -   Model
    security:
        -   bearer: []
    parameters:
        -   name: model
            in: body
            description: information about the model
            required: true
            schema:
                $ref: '#/definitions/ModelInfoWithParametersDto'
    responses:
        201:
            description: Created a new model
            schema:
                $ref: '#/definitions/ModelInfoWithParametersDto'
    """
    # model_info_with_params = ModelInfoWithParametersDtoSchema().load(request.json)
    # graph_db_model = add_model(model_info_with_params.name, model_info_with_params.inputs,
                            #    model_info_with_params.outputs, SparQlRunner())

    model_info = ModelInfo.ModelInfoDbSchema().load(request.json)
    model_info.owner = current_user.company
    model_info.created_on = datetime.utcnow()
    model_info.created_by = current_user
    # model_info.ontology_uri = graph_db_model.uri
    model_info.add()
    return get_json(model_info, ModelInfo.ModelInfoDbSchema), 201


@model_bp.route('/model/<model_id>', methods=['PUT'])
@jwt_required
def update_model(model_id: str):
    """
    Update existing model created by current user
    ---
    tags:
        -   Model
    security:
        -   bearer: []
    parameters:
        -   name: model_id
            in: path
            description: model id
            required: true
            schema:
                type: string
        -   name: model
            in: body
            description: information about the model
            required: true
            schema:
                $ref: '#/definitions/ModelInfoWithParametersDto'
    responses:
        200:
            description: Updated existing model
            schema:
                $ref: '#/definitions/ModelInfoWithParametersDto'
        404:
            description: model not found or not editable to current user
    """
    model_info_db = ModelInfo.query.get_created_by_or_404(current_user.id, model_id)
    model_info_new = ModelInfo.ModelInfoDbSchema().load(request.json)
    model_info_db.name = model_info_new.name
    model_info_db.description = model_info_new.description
    model_info_db.price = model_info_new.price
    model_info_db.is_connected = model_info_new.is_connected
    model_info_db.ontology_uri = model_info_new.ontology_uri
    model_info_db.gateway_url = model_info_new.gateway_url

    # model_info_with_params = GraphDbModelSchema().load(request.json)
    # graph_db_model = add_model(model_info_with_params.name, model_info_with_params.inputs,
                            #    model_info_with_params.outputs, SparQlRunner())

    model_info_db = model_info_db.update()
    return get_json(model_info_db, ModelInfo.ModelInfoDbSchema)


@model_bp.route('/model/<model_id>', methods=['DELETE'])
@jwt_required
def delete_model(model_id: str):
    """
    Delete model with specified id
    ---
    tags:
        -   Model
    security:
        - bearer: []
    parameters:
        -   name: id
            in: path
            description: id of the model
            required: true
            type: string
    responses:
        200:
            description: Model has been removed
        404:
            description: Model with specified id not found or not deletable by current user
        400:
            description: Model has been used in simulation
    """
    model_info = ModelInfo.query.get_created_by_or_404(current_user.id, model_id)
    if len(model_info.used_in_simulations or []):
        abort(400, description='model already used in simulation')
    model_info.delete()
    return jsonify()


@model_bp.route('/models', methods=['GET'])
@jwt_required
def get_models():
    """
    Get all models accessible to current user's company
    ---
    tags:
        -   Model
    security:
        - bearer: []
    responses:
        200:
            description: list of saved models
            schema:
                type: array
                items:
                    $ref: '#/definitions/ModelInfoDb'
    """
    return get_json(ModelInfo.query.get_all_accessible_by(current_user.company_id),
                    ModelInfo.ModelInfoDbSchema, {'company_id': current_user.company.id})


@model_bp.route('/own_models', methods=['GET'])
@jwt_required
def get_own_models():
    """
    Get models owned by logged in users organization
    ---
    tags:
        -   Model
    security:
        - bearer: []
    responses:
        200:
            description: list of saved models
            schema:
                type: array
                items:
                    $ref: '#/definitions/ModelInfoDb'
    """
    return get_json(ModelInfo.query.get_all_owned_by(current_user.company_id), ModelInfo.ModelInfoDbSchema,
                    {'company_id': current_user.company.id})


@model_bp.route('/model/<model_id>', methods=['GET'])
@jwt_required
def get_model(model_id: str):
    """
    Get model by id
    ---
    tags:
        -   Model
    security:
        - bearer: []
    parameters:
        -   name: model_id
            in: path
            description: id of the model
            required: true
            type: string
    responses:
        200:
            description: Model with specified id
            schema:
                $ref: '#/definitions/ModelInfoWithParametersDto'
        404:
            description: Model with specified id not found or not accessible by current user
    """
    model_info: ModelInfo = ModelInfo.query.get_accessible_or_404(current_user.company_id, model_id)
    model_graph = rdflib.Graph().parse(location=model_info.gateway_url+"/api/ontology.ttl")

    # load all imported ontologies into same graph 
    # TODO (and somehow keep track of default prefixes...)
    # TODO handle recursive imports (circular?)
    for imp in model_graph.objects(subject=URIRef(model_info.gateway_url+"/api/ontology.ttl#"), predicate=OWL.imports):
        model_graph.parse(location=str(imp))

    interface_info = ModelInterfaceDefinition.from_graph(model_graph,
        URIRef(model_info.ontology_uri))

    model_interface_info = ModelInfoWithParametersDtoSchema().dump(model_info)
    model_interface_info.update(ModelInterfaceDefinitionSchema().dump(interface_info))
    if len(val_errors := ModelInfoWithParametersDtoSchema().validate(model_interface_info)) == 0:
        return jsonify(model_interface_info)
    else:
        raise ValidationError(val_errors)
    # graph_db_model = query_model.get_model(model_info.ontology_uri, SparQlRunner())


@model_bp.route('/model/permissions/<model_id>', methods=['PUT'])
@jwt_required
def set_model_permissions(model_id: str):
    """
    Set permissions for model
    ---
    tags:
        -   Model
    security:
        - bearer: []
    parameters:
        -   name: model_id
            in: path
            description: model id
            required: true
            schema:
                type: string
        -   name: model_permissions
            in: body
            description: model permissions
            required: true
            schema:
                type: array
                items:
                    $ref: '#/definitions/ModelPermissionDto'
    responses:
        200:
            description: permissions
            schema:
                type: array
                items:
                    $ref: '#/definitions/ModelPermissionDto'
        404:
            description: model not found or not created by current user
    """
    model_permissions = ModelPermissionDtoSchema(exclude=['model_info_id'], many=True).load(request.json)
    model_info = ModelInfo.query.get_created_by_or_404(current_user.id, model_id)

    unique_permissions = {}
    for p in model_permissions:
        company_permission = unique_permissions.get(p.company_id, set())
        company_permission.add(p.permission_type)
        unique_permissions[p.company_id] = company_permission

    model_info.permissions = []
    for company_id, permissions in unique_permissions.items():
        for permission_type in permissions:
            model_info.permissions.append(ModelPermission(model_info_id=model_id, company_id=company_id,
                                                          permission_type=ModelPermissionTypes(permission_type)))
    model_info.save()
    return get_json(model_info.permissions, ModelPermissionDtoSchema)


@model_bp.route('/model/permissions/<model_id>', methods=['GET'])
@jwt_required
def get_model_permissions(model_id: str):
    """
    Get permissions of the corresponding model
    ---
    tags:
        -   Model
    security:
        - bearer: []
    parameters:
        -   name: model_id
            in: path
            description: id of the model
            required: true
            schema:
                type: string
    responses:
        200:
            description: <description>
            schema:
                type: array
                items:
                    $ref: '#/definitions/ModelPermissionDto'
        404:
            description: model not found or not owned by current user's organization
    """
    return get_json(ModelInfo.query.get_owned_or_404(current_user.company_id, model_id).permissions,
                    ModelPermissionDtoSchema)


# def __create_model_info_with_param_json(model_info: ModelInfo, model_graph_db: GraphDbModel):
#     model_info_dict = ModelInfo.ModelInfoDbSchema(context={'company_id': current_user.company.id}).dump(model_info)
#     model_with_params_dict = GraphDbModelSchema().dump(model_graph_db)
#     model_with_params_dict.update(model_info_dict)
#     if len(ModelInfoWithParametersDtoSchema().validate(model_with_params_dict)) == 0:
#         return jsonify(model_with_params_dict)
#     else:
#         raise ValidationError('model data is not correct')
