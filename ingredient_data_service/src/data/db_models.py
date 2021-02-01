from marshmallow import post_load
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from common_data_access.base_schema import BaseModel
from common_data_access.db import create_db_connection
from common_data_access.dtos import IngredientPropertyInfoDtoSchema, IngredientInfoDtoSchema, \
    IngredientInfoWithPropertyInfosDtoSchema

_db = create_db_connection()


class IngredientProperty(BaseModel):
    __tablename__ = 'ingredient_properties'

    name = _db.Column(_db.String, nullable=False)
    value_text = _db.Column(_db.String)
    value = _db.Column(_db.Float, nullable=False)
    unit = _db.Column(_db.String, nullable=False)
    ingredient_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('ingredients.id'))
    ingredient = relationship('Ingredient', back_populates='ingredient_properties')

    def __repr__(self):
        return f'<IngredientProperty name: {self.name}, value: {self.value_number}, unit: {self.unit_of_measurement}>'

    class IngredientPropertySchema(IngredientPropertyInfoDtoSchema):
        @post_load
        def __create_object(self, data, **kwargs):
            return IngredientProperty(**data)


class Ingredient(BaseModel):
    __tablename__ = 'ingredients'

    name = _db.Column(_db.String, nullable=False)
    company_code = _db.Column(_db.String, unique=True, nullable=False)
    standard_code = _db.Column(_db.String, unique=True, nullable=False)
    ingredient_properties = relationship('IngredientProperty')

    def __repr__(self):
        return f'<Ingredient name: {self.name}, code: {self.code}, ' \
               f'ingredients: {",".join((str(item) for item in self.ingredient_properties))}>'

    class IngredientSchema(IngredientInfoDtoSchema):
        @post_load
        def __create_object(self, data, **kwargs):
            return Ingredient(**data)

    class IngredientWithPropertiesSchema(IngredientInfoWithPropertyInfosDtoSchema):
        @post_load
        def __create_object(self, data, **kwargs):
            return Ingredient(**data)
