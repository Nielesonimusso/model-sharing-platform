from marshmallow import fields, validate
from sqlalchemy.dialects.postgresql import UUID

from common_data_access.base_schema import BaseModel
from common_data_access.db import create_db_connection
from common_data_access.dtos import BaseDto, NotEmptyString
from model_sharing_backend.src.models.company import CompanyDtoSchema

_db = create_db_connection()

email_validator = validate.Email(error='invalid email address')
password_validators = [validate.Length(min=6, max=36)]


class User(BaseModel):
    __tablename__ = 'users'

    username = _db.Column(_db.String, unique=True, nullable=False)
    full_name = _db.Column(_db.String, nullable=False)
    email = _db.Column(_db.String, nullable=False)
    password_hash = _db.Column(_db.LargeBinary, nullable=False)
    company_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('companies.id'), nullable=False)
    company = _db.relationship('Company')

    def __repr__(self):
        return f'<USER {self.__hash__()}> {self.full_name} ({self.username})'


class PasswordReset(BaseModel):
    __tablename__ = 'password_resets'
    reset_code = _db.Column(_db.String, nullable=False)
    created_on = _db.Column(_db.DateTime, nullable=False)
    is_used = _db.Column(_db.Boolean, default=False)
    user_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('users.id'), nullable=False)
    user = _db.relationship('User')


class UserProfileDtoSchema(BaseDto):
    username = fields.String(required=True, validate=[NotEmptyString()])
    email = fields.Email(required=True, validate=[email_validator])
    full_name = fields.String(required=True, validate=[NotEmptyString()])
    company_id = fields.UUID(required=True)
    company = fields.Nested(CompanyDtoSchema, dump_only=True)


class UserRegistrationDtoSchema(UserProfileDtoSchema):
    password = fields.String(required=True, validate=password_validators)

    def __init__(self, *args, **kwargs):
        kwargs['exclude'] = [*kwargs['exclude'], 'company'] if 'exclude' in kwargs else ['company']
        super().__init__(*args, **kwargs)


class UserProfileUpdateDtoSchema(BaseDto):
    email = fields.Email(required=True, validate=[email_validator])
    full_name = fields.String(required=True)


class UserLoginDtoSchema(BaseDto):
    username = fields.String()
    password = fields.String()


UserBasicReadonlyInfo = fields.Nested(UserProfileDtoSchema, only=('username', 'full_name'), dump_only=True)


class ChangePasswordDtoSchema(BaseDto):
    current_password = fields.String(required=True)
    new_password = fields.String(required=True, validate=password_validators)


class PasswordResetDtoSchema(BaseDto):
    reset_code = fields.Str(required=True, validate=[NotEmptyString()])
    new_password = fields.Str(required=True, validate=password_validators)
    email = fields.Str(required=True, validate=[email_validator])


def get_schemas() -> list:
    return [UserLoginDtoSchema, UserRegistrationDtoSchema, UserProfileUpdateDtoSchema, ChangePasswordDtoSchema,
            PasswordResetDtoSchema]
