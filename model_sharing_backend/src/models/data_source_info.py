from enum import Enum

from marshmallow import fields, validate, post_load
from sqlalchemy.dialects.postgresql import UUID

from common_data_access.base_schema import DbSchema, BaseModel
from common_data_access.db import create_db_connection
from common_data_access.dtos import NotEmptyString
from .base_model import BaseModelWithOwnerAndCreator, BaseDbSchemaWithOwnerAndCreator, \
    BasePermission, BasePermissionDtoSchema
from .query_classes.data_source_info_query_class import DataSourceInfoQuery
from .association_models import data_source_simulation_association

_db = create_db_connection()

class DataSourceInfo(BaseModelWithOwnerAndCreator):
    __tablename__ = 'data_source_infos'
    query_class = DataSourceInfoQuery

    name = _db.Column(_db.String, nullable=False)
    price = _db.Column(_db.Float)
    is_connected = _db.Column(_db.Boolean, default=True)
    gateway_url = _db.Column(_db.String, nullable=False)
    permissions = _db.relationship('DataSourcePermission', cascade='delete-orphan, delete, save-update')
    used_in_simulations = _db.relationship('Simulation', secondary=data_source_simulation_association)


    class DataSourceInfoDbSchema(BaseDbSchemaWithOwnerAndCreator):
        name = fields.Str(required=True, validate=[NotEmptyString()])
        price = fields.Number()
        is_connected = fields.Bool()
        gateway_url = fields.Url(required=True, require_tld=False)
        use_count = fields.Method('data_source_usage_count', dump_only=True, default=0)
        can_access = fields.Method('has_access_permission', dump_only=True, default=False)

        def has_access_permission(self, data_source_info) -> bool:
            company_id = self.context.get('company_id', None)
            return data_source_info.owner_id == company_id or len(list(filter(
                lambda p: p.company_id == company_id and p.permission_type == DataSourcePermissionTypes.VIEW_AND_ACCESS,
                data_source_info.permissions))) > 0
        
        def data_source_usage_count(self, data_source_info) -> int:
            return 0 # TODO based on simulation runs involving data

        def __init__(self, *args, **kwargs):
            super().__init__(DataSourceInfo, *args, **kwargs)


DataSourceBasicInfoReadonlyField = fields.Nested(DataSourceInfo.DataSourceInfoDbSchema,
        only=('id', 'name', 'owner', 'can_access', 'is_connected', 'price'), 
        dump_only=True)

class DataSourcePermissionTypes(Enum):
    VIEW_ONLY = 'view'
    VIEW_AND_ACCESS = 'access'

class DataSourcePermission(BasePermission):
    __tablename__ = 'data_source_permissions'

    data_source_info_id = _db.Column(UUID(as_uuid=True), 
            _db.ForeignKey('data_source_infos.id'), nullable=False)
    data_source_info = _db.relationship('DataSourceInfo')
    permission_type = _db.Column(_db.Enum(DataSourcePermissionTypes), nullable=False,
            default = DataSourcePermissionTypes.VIEW_ONLY)

    class DataSourcePermissionDtoSchema(BasePermissionDtoSchema):
        data_source_info_id = fields.UUID(load_only=True)
        data_source_info = DataSourceBasicInfoReadonlyField
        permission_type = fields.Str(validate=validate.OneOf(
            [a.value for a in DataSourcePermissionTypes]), required=True)

def get_schemas() -> list:
    return [DataSourceInfo.DataSourceInfoDbSchema, 
        DataSourcePermission.DataSourcePermissionDtoSchema]