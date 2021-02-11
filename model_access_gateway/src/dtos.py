from marshmallow import fields

from common_data_access.dtos import BaseDto, ModelRunParameterSchema


class RecipeSchema(BaseDto):
    dosage = fields.Number()
    dosage_unit = fields.Str()
    ingredients = fields.List(fields.Nested(ModelRunParameterSchema))


class TasteDto:
    def __init__(self, taste_name: str, taste_value: float, description: str):
        self.taste_name = taste_name
        self.taste_value = taste_value
        self.description = description


class TasteSchema(BaseDto):
    taste_name = fields.Str()
    taste_value = fields.Number()
    description = fields.Str()


class NutritionDto:
    def __init__(self, nutrition_name: str, nutrition_value: float, nutrition_unit: str):
        self.nutrition_name = nutrition_name
        self.nutrition_value = nutrition_value
        self.nutrition_unit = nutrition_unit


class NutritionSchema(BaseDto):
    nutrition_name = fields.Str()
    nutrition_value = fields.Number()
    nutrition_unit = fields.Str()