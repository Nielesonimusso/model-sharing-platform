import json
from typing import List, Tuple

from marshmallow import fields
import rdflib

from common_data_access.dtos import BaseDto, RunModelDtoSchema
from model_access_gateway.src.ingredient_store import get_ingredient_properties
from model_access_gateway.src.models.model import Model

class IngredientDto(BaseDto):
    name = fields.Str(required=True) # reference to IngredientDatabase.ingredient
    amount = fields.Number(required=True) # mass(?)-percent

    __OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')
    __IDB = rdflib.Namespace('http://ingredient-access-gateway:5020/IngredientDatabase/ontology.ttl#')
        # based on configuration! is different when not using docker
        # requires ontology import of 'http://ingredient-access-gateway:5020/IngredientDatabase/ontology.ttl'

    units = dict(
        name = None,
        amount = __OM.percent
        # amount = 'name' # local unit column
        # amount = rdflib.URIRef('URI of unit column') # for external unit column
            # would also require an ontology import of the source of the column
    )

    references = dict(
        name = dict(
            source=__IDB.IngredientDatabase,
            chain=[__IDB.Ingredient]
            # list of property chain
        ),
        amount = None
    )

class DosageDto(BaseDto):
    dosage = fields.Number(required=True) # gram per liter

    __OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')

    units = dict(
        dosage = __OM.gramPerLitre
    )

    references = dict(
        dosage = None
    )

# input schema
class NutritionInputDto(BaseDto):
    IngredientsTable = fields.Nested(IngredientDto, many=True)
    DosageTable = fields.Nested(DosageDto, many=True)
    

class NutritionSchema(BaseDto):
    nutrition_name = fields.Str()
    nutrition_value = fields.Number()
    nutrition_unit = fields.Str()

    units = dict(
        nutrition_name = None,
        nutrition_value = 'nutrition_unit',
        nutrition_unit = None
    )

    references = dict(
        nutrition_name = None,
        nutrition_value = None,
        nutrition_unit = None
    )


# output schema
class NutritionOutputDto(BaseDto):
    NutritionTable = fields.Nested(NutritionSchema, many=True)


class NutritionModel(Model):
    @property
    def input_dto(self) -> type:
        return NutritionInputDto

    @property
    def output_dto(self) -> type:
        return NutritionOutputDto

    @property
    def ontology_imports(self) ->  List[Tuple[rdflib.URIRef, str]]:
        return [
            ('http://ingredient-access-gateway:5020/IngredientDatabase/ontology.ttl#', 'idb')
        ]

    @property
    def description(self) -> str:
        return """Model that calculates the nutritional values of a food product"""

    @property
    def price(self) -> float:
        return 4

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