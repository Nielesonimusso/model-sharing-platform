from marshmallow import fields

from common_data_access.base_schema import BaseModel
from common_data_access.db import create_db_connection
from common_data_access.dtos import BaseDto

_db = create_db_connection()


class Company(BaseModel):
    __tablename__ = 'companies'

    name = _db.Column(_db.String, nullable=False)
    address = _db.Column(_db.String)


class CompanyDtoSchema(BaseDto):
    id = fields.UUID()
    name = fields.Str()
    address = fields.Str()


def get_schemas() -> list:
    return [CompanyDtoSchema]
