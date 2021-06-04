from marshmallow import fields, validate
from sqlalchemy.dialects.postgresql import UUID

from common_data_access.base_schema import DbSchema, BaseModel
from common_data_access.db import create_db_connection
from common_data_access.dtos import NotEmptyString
from model_sharing_backend.src.models.base_model import BaseModelWithOwnerAndCreator, BaseDbSchemaWithOwnerAndCreator, \
    BasePermission, BasePermissionDtoSchema

_db = create_db_connection()


class _ModelWithIdAndName(BaseModel):
    __abstract__ = True

    name = _db.Column(_db.String, nullable=False)

    def __repr__(self):
        return f'<{type(self).name} id: {self.id}, name: {self.name}>'


class _SchemaWithIdAndName(DbSchema):
    name = fields.Str(required=True, validate=[NotEmptyString()])

    def __repr__(self):
        return f'<{type(self).name} id: {self.id}, name: {self.name}>'


class FoodProductProperty(_ModelWithIdAndName):
    __tablename__ = 'food_product_properties'

    value = _db.Column(_db.Float, nullable=False)
    unit = _db.Column(_db.String, nullable=False)
    method = _db.Column(_db.String)
    food_product_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('food_products.id'))

    class FoodProductPropertyDbSchema(_SchemaWithIdAndName):
        value = fields.Number(required=True)
        unit = fields.Str(required=True, validate=[NotEmptyString()])
        method = fields.Str()

        def __init__(self, *args, **kwargs):
            super().__init__(FoodProductProperty, *args, **kwargs)


class ProcessingStepProperty(_ModelWithIdAndName):
    __tablename__ = 'processing_step_properties'

    value = _db.Column(_db.Float, nullable=False)
    unit = _db.Column(_db.String, nullable=False)
    processing_step_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('food_product_processing_steps.id'))

    class ProcessingStepPropertySchema(_SchemaWithIdAndName):
        value = fields.Number(required=True)
        unit = fields.Str(required=True, validate=[NotEmptyString()])

        def __init__(self, *args, **kwargs):
            super().__init__(ProcessingStepProperty, *args, **kwargs)


class FoodProductProcessingStep(_ModelWithIdAndName):
    __tablename__ = 'food_product_processing_steps'

    equipment = _db.Column(_db.String, nullable=False)
    properties = _db.relationship('ProcessingStepProperty', cascade='delete-orphan, delete, save-update')
    food_product_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('food_products.id'))

    class FoodProductProcessingStepDbSchema(_SchemaWithIdAndName):
        equipment = fields.Str(required=True, validate=[NotEmptyString()])
        properties = fields.List(fields.Nested(ProcessingStepProperty.ProcessingStepPropertySchema),
                                 validate=[validate.Length(min=1)])

        def __init__(self, *args, **kwargs):
            super().__init__(FoodProductProcessingStep, *args, **kwargs)


class FoodProductPackaging(_ModelWithIdAndName):
    __tablename__ = 'food_product_packagings'

    company_code = _db.Column(_db.String, nullable=False)
    standard_code = _db.Column(_db.String)
    shape = _db.Column(_db.String, nullable=False)
    thickness = _db.Column(_db.Float, nullable=False)
    thickness_unit = _db.Column(_db.String, nullable=False)
    food_product_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('food_products.id'))

    class FoodProductPackagingDbSchema(_SchemaWithIdAndName):
        company_code = fields.Str(required=True, validate=[NotEmptyString()])
        standard_code = fields.Str()
        shape = fields.Str(required=True, validate=[NotEmptyString()])
        thickness = fields.Number(required=True)
        thickness_unit = fields.Str(required=True, validate=[NotEmptyString()])

        def __init__(self, *args, **kwargs):
            super().__init__(FoodProductPackaging, *args, **kwargs)


class Ingredient(_ModelWithIdAndName):
    __tablename__ = 'food_product_ingredients'

    company_code = _db.Column(_db.String, nullable=False)
    standard_code = _db.Column(_db.String)
    amount = _db.Column(_db.Float, nullable=False)
    amount_unit = _db.Column(_db.String, nullable=False)
    food_product_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('food_products.id'))

    class IngredientDbSchema(_SchemaWithIdAndName):
        company_code = fields.Str(required=True, validate=[NotEmptyString()])
        standard_code = fields.Str()
        amount = fields.Number(required=True)
        amount_unit = fields.Str(required=True, validate=[NotEmptyString()])

        def __init__(self, *args, **kwargs):
            super().__init__(Ingredient, *args, **kwargs)


class FoodProduct(_ModelWithIdAndName, BaseModelWithOwnerAndCreator):
    __tablename__ = 'food_products'

    company_code = _db.Column(_db.String, unique=True, nullable=False)
    standard_code = _db.Column(_db.String, unique=True)
    dosage = _db.Column(_db.Float, nullable=False)
    dosage_unit = _db.Column(_db.String, nullable=False)
    ingredients = _db.relationship('Ingredient', cascade='delete-orphan, delete , save-update')
    food_product_properties = _db.relationship('FoodProductProperty', cascade='delete-orphan, delete, save-update')
    processing_steps = _db.relationship('FoodProductProcessingStep', cascade='delete-orphan, delete, save-update')
    packagings = _db.relationship('FoodProductPackaging', cascade='delete-orphan, delete, save-update')
    permissions = _db.relationship('FoodProductPermission', cascade='delete-orphan, delete, save-update')
    # used_in_simulations = _db.relationship('Simulation')

    class FoodProductDbSchema(_SchemaWithIdAndName, BaseDbSchemaWithOwnerAndCreator):
        company_code = fields.Str(required=True, validate=[NotEmptyString()])
        standard_code = fields.Str()
        dosage = fields.Number(required=True)
        dosage_unit = fields.Str(required=True, validate=[NotEmptyString()])
        food_product_properties = fields.List(fields.Nested(FoodProductProperty.FoodProductPropertyDbSchema))
        ingredients = fields.List(fields.Nested(Ingredient.IngredientDbSchema), validate=[validate.Length(min=1)])
        processing_steps = fields.List(fields.Nested(FoodProductProcessingStep.FoodProductProcessingStepDbSchema))
        packagings = fields.List(fields.Nested(FoodProductPackaging.FoodProductPackagingDbSchema))

        def __init__(self, *args, **kwargs):
            super().__init__(FoodProduct, *args, **kwargs)


FoodProductBasicInfoReadOnlyField = fields.Nested(FoodProduct.FoodProductDbSchema,
                                                  only=('id', 'name', 'owner', 'company_code', 'standard_code'),
                                                  dump_only=True)


class FoodProductPermission(BasePermission):
    __tablename__ = 'food_product_permissions'

    food_product_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('food_products.id'), nullable=False)
    food_product = _db.relationship('FoodProduct', uselist=False)


class FoodProductPermissionDtoSchema(BasePermissionDtoSchema):
    food_product_id = fields.UUID(load_only=True)
    food_product = FoodProductBasicInfoReadOnlyField


def get_schemas() -> list:
    return [FoodProduct.FoodProductDbSchema, FoodProductPermissionDtoSchema]
