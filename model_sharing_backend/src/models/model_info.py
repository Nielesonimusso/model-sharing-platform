from enum import Enum

from marshmallow import fields, validate, post_load
from sqlalchemy.dialects.postgresql import UUID

from common_data_access.base_schema import DbSchema, BaseModel
from common_data_access.db import create_db_connection
from common_data_access.dtos import NotEmptyString
from model_sharing_backend.src.ontology_services.data_structures import ModelInterfaceDefinitionSchema
from .association_models import model_simulation_association
from .base_model import BaseModelWithOwnerAndCreator, BaseDbSchemaWithOwnerAndCreator, BasePermission, \
    BasePermissionDtoSchema
from .query_classes.model_info_query_class import ModelInfoQuery

_db = create_db_connection()


class ModelInfo(BaseModelWithOwnerAndCreator):
    __tablename__ = 'model_infos'
    query_class = ModelInfoQuery

    name = _db.Column(_db.String, nullable=False)
    description = _db.Column(_db.String)
    price = _db.Column(_db.Float)
    is_connected = _db.Column(_db.Boolean, default=True)
    ontology_uri = _db.Column(_db.String, nullable=False)
    gateway_url = _db.Column(_db.String, nullable=False)
    permissions = _db.relationship('ModelPermission', cascade='delete-orphan, delete, save-update')
    used_in_simulations = _db.relationship('Simulation', secondary=model_simulation_association)

    def __repr__(self):
        return f'<ModelInfo id:{self.id} name:{self.name}>'

    class ModelInfoDbSchema(BaseDbSchemaWithOwnerAndCreator):
        name = fields.Str(required=True, validate=[NotEmptyString()])
        description = fields.Str()
        price = fields.Number()
        is_connected = fields.Bool()
        ontology_uri = fields.Str(required=True)
        gateway_url = fields.Url(required=True, require_tld=False)
        use_count = fields.Method('model_usage_count', dump_only=True, default=0)
        can_execute = fields.Method('has_execute_permission', dump_only=True, default=False)

        def has_execute_permission(self, model_info) -> bool:
            company_id = self.context.get('company_id', None)
            return model_info.owner_id == company_id or len(list(filter(
                lambda p: p.company_id == company_id and p.permission_type == ModelPermissionTypes.VIEW_AND_EXECUTE,
                model_info.permissions))) > 0

        def model_usage_count(self, model_info) -> int:
            from .simulation import ExecutedModel
            return len(ExecutedModel.query.get_where(ExecutedModel.model_id == model_info.id))

        def __init__(self, *args, **kwargs):
            super().__init__(ModelInfo, *args, **kwargs)


class ModelInfoWithParametersDtoSchema(ModelInfo.ModelInfoDbSchema, ModelInterfaceDefinitionSchema):

    @post_load
    def _after_load(self, data, **kwargs):
        class_name = f'{type(self).__name__}_generated'
        return type(class_name, (object,), data)


ModelBasicInfoReadonlyField = fields.Nested(ModelInfo.ModelInfoDbSchema,
                                            only=('id', 'name', 'owner', 'can_execute', 'is_connected', 'description',
                                                  'price', 'ontology_uri', 'gateway_url'), dump_only=True)


class ModelPermissionTypes(Enum):
    VIEW_ONLY = 'view'
    VIEW_AND_EXECUTE = 'execute'


class ModelPermission(BasePermission):
    __tablename__ = 'model_permissions'

    model_info_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('model_infos.id'), nullable=False)
    model_info = _db.relationship('ModelInfo')
    permission_type = _db.Column(_db.Enum(ModelPermissionTypes), nullable=False, default=ModelPermissionTypes.VIEW_ONLY)


class ModelPermissionDtoSchema(BasePermissionDtoSchema):
    model_info_id = fields.UUID(load_only=True)
    model_info = ModelBasicInfoReadonlyField
    permission_type = fields.Str(validate=validate.OneOf([a.value for a in ModelPermissionTypes]), required=True)


def get_schemas() -> list:
    return [ModelInfo.ModelInfoDbSchema, ModelPermissionDtoSchema, ModelInfoWithParametersDtoSchema]
