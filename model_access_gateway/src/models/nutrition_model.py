import json
from typing import List

from marshmallow import fields

from common_data_access.dtos import BaseDto, RunModelDtoSchema
from model_access_gateway.src.ingredient_store import get_ingredient_properties
from model_access_gateway.src.models.model import Model

class IngredientDto(BaseDto):
    name = fields.Str(required=True)
    amount = fields.Number(required=True) # mass(?)-percent
    company_code = fields.Str()
    standard_code = fields.Str()

class DosageDto(BaseDto):
    dosage = fields.Number(required=True) # gram per liter

# input schema
class NutritionInputDto(BaseDto):
    IngredientsTable = fields.Nested(IngredientDto, many=True)
    DosageTable = fields.Nested(DosageDto, many=True)

# output schema
class NutritionSchema(BaseDto):
    nutrition_name = fields.Str()
    nutrition_value = fields.Number()
    nutrition_unit = fields.Str()

class NutritionModel(Model):
    @property
    def input_dto(self) -> type:
        return NutritionInputDto

    @property
    def output_dto(self) -> type:
        return NutritionSchema

    def run_model(self, input) -> list:
        ingredients = [get_ingredient_properties(i.company_code) for i in input.IngredientsTable]
    
# def calculate_nutrition(recipe, ingredients: List) -> list:

        total_ingredient_properties = dict()
        for ing in input.IngredientsTable:
            ing.amount = ing.amount * input.DosageTable[0].dosage / 100
            ing.amount_unit = 'gram'

            ingredient = next(filter(lambda i: i.company_code == ing.company_code, ingredients), None)
            if ingredient == None:
                raise Exception(f'ingredient with code {ing.company_code} not found')

            for prp in ingredient.ingredient_properties:
                prp_in_recipe = ing.amount * prp.value / 100
                total_ingredient_properties[prp.name] = total_ingredient_properties.get(prp.name, 0) + prp_in_recipe

        if sum(a for a in total_ingredient_properties.values()) != input.DosageTable[0].dosage:
            print('dosage value does not match with calculated dosage')


        relevant_ingredients = [
            total_ingredient_properties.get('Sucrose', 0),
            total_ingredient_properties.get('Fructose', 0), 
            total_ingredient_properties.get('Glucose', 0),
            total_ingredient_properties.get('AceticAcid', 0),
            total_ingredient_properties.get('CitricAcid', 0),
            total_ingredient_properties.get('Water', 0),
            total_ingredient_properties.get('Na', 0),
            total_ingredient_properties.get('K', 0),
            total_ingredient_properties.get('Cl', 0),
            total_ingredient_properties.get('Protein', 0),
            total_ingredient_properties.get('Fats', 0),
            total_ingredient_properties.get('Carbohydrates', 0),
            ]


        nutrition_table = {
            'Energy':        [4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 9, 4],
            'Fats':          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            'Carbohydrates': [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            'Sugars':        [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Protein':       [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            'Salt':          [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            'Water':         [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
        }


        nutritions = []
        for nutrition_name, table in nutrition_table.items():
            nutritions.append(dict(nutrition_name=nutrition_name, 
                nutrition_value=sum([x*y for x,y in zip(table, relevant_ingredients)]), 
                nutrition_unit='kcal' if nutrition_name == "Energy" else 'gram'))

        return nutritions