from marshmallow import fields
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr

from common_data_access.base_schema import BaseModel, DbSchema
from common_data_access.db import create_db_connection
from common_data_access.dtos import BaseDto
from model_sharing_backend.src.models.company import CompanyDtoSchema
from model_sharing_backend.src.models.user import UserBasicReadonlyInfo

_db = create_db_connection()


class BaseModelWithOwnerAndCreator(BaseModel):
    __abstract__ = True

    created_on = _db.Column(_db.DateTime)

    @declared_attr
    def created_by(self):
        return _db.relationship('User')

    @declared_attr
    def owner(self):
        return _db.relationship('Company')

    @declared_attr
    def owner_id(self):
        return _db.Column(UUID(as_uuid=True), _db.ForeignKey('companies.id'), nullable=False)

    @declared_attr
    def created_by_id(self):
        return _db.Column(UUID(as_uuid=True), _db.ForeignKey('users.id'), nullable=False)


class BaseDbSchemaWithOwnerAndCreator(DbSchema):
    created_on = fields.DateTime(dump_only=True)
    created_by = UserBasicReadonlyInfo
    owner = fields.Nested(CompanyDtoSchema, only=['id', 'name'], dump_only=True)


class BasePermission(BaseModel):
    __abstract__ = True

    @declared_attr
    def company_id(self):
        return _db.Column(UUID(as_uuid=True), _db.ForeignKey('companies.id'), nullable=False)

    @declared_attr
    def company(self):
        return _db.relationship('Company', uselist=False)


class BasePermissionDtoSchema(BaseDto):
    company_id = fields.UUID(load_only=True, required=True)
    company = fields.Nested(CompanyDtoSchema, dump_only=True)
