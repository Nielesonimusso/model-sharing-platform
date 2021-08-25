import math
from typing import List, Tuple

from marshmallow import fields
import rdflib

from common_data_access.dtos import BaseDto, RunModelDtoSchema
from model_access_gateway.src.ingredient_store import get_ingredient_properties
from model_access_gateway.src.models.model import Model

class IngredientDto(BaseDto):
    name = fields.Str(required=True)
    amount = fields.Number(required=True) # mass(?)-percent

    __OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')
    __IDB = rdflib.Namespace('http://ingredient-access-gateway:5020/api/IngredientDatabase/ontology.ttl#')

    units = dict(
        name = None,
        amount = __OM.percent
    )

    references = dict(
        name = dict(
            source=__IDB.IngredientDatabase,
            property=__IDB.Ingredient
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
class RecipeInputDto(BaseDto):
    IngredientsTable = fields.Nested(IngredientDto, many=True)
    DosageTable = fields.Nested(DosageDto, many=True)

# output schema
class TasteDto(BaseDto):
    taste_name = fields.Str()
    taste_value = fields.Number()
    description = fields.Str()

    __OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')

    units = dict(
        taste_name = None,
        taste_value = __OM['_0-100'],
        description = None
    )

    references = dict(
        taste_name = None, # TODO potential for refernce to ontology concept
        taste_value = None,
        description = None
    )

class TasteOutputDto(BaseDto):
    TasteTable = fields.Nested(TasteDto, many=True, required=True)

class TasteModel(Model):
    
    def __init__(self, tastes_to_calculate):
        self.tastes_to_calculate = tastes_to_calculate

    @property
    def input_dto(self) -> type:
        return RecipeInputDto

    @property
    def output_dto(self) -> type:
        return TasteOutputDto

    @property
    def ontology_imports(self) -> List[Tuple[rdflib.URIRef, str]]:
        return [
            ('http://ingredient-access-gateway:5020/api/IngredientDatabase/ontology.ttl#', 'idb')
        ]

    @property
    def name(self) -> str:
        return f'{super().name}: {", ".join(self.tastes_to_calculate)}'

    @property
    def description(self) -> str:
        return f"""Model that calculates the following tastes of a food product: 
    {", ".join(self.tastes_to_calculate)}"""

    @property
    def price(self) -> float:
        return 3.5

    def run_model(self, input) -> list:
        ingredients = [get_ingredient_properties(i.name) for i in input.IngredientsTable]
        
        tastes_to_calculate = self.tastes_to_calculate or ['sweetness', 'sourness', 'saltiness', 'tomato taste']
        product_density = 1
        water_to_add = 1000 - sum(ing.amount for ing in input.IngredientsTable) * product_density
        total_ingredient_properties = dict()
        for ing in input.IngredientsTable:
            ing.amount = ing.amount * input.DosageTable[0].dosage / 100
            ing.amount_unit = 'gram'

            ingredient = next(filter(lambda i: i.name == ing.name, ingredients), None)
            if ingredient == None:
                raise Exception(f'ingredient with code {ing.name} not found')

            for prp in ingredient.ingredient_properties:
                prp_in_recipe = ing.amount * prp.value / 100
                total_ingredient_properties[prp.name] = total_ingredient_properties.get(prp.name, 0) + prp_in_recipe

        if sum(a for a in total_ingredient_properties.values()) != input.DosageTable[0].dosage:
            print('dosage value does not match with calculated dosage')

        tastes = []
        if 'sweetness' in tastes_to_calculate:
            tastes.append(dict(taste_name='Sweetness',
                                taste_value=self.calculate_sweetness(total_ingredient_properties.get('Sucrose', 0),
                                                    total_ingredient_properties.get('Fructose', 0),
                                                    total_ingredient_properties.get('Glucose', 0)),
                                description='Sensory scale (0-100)'))
        if 'sourness' in tastes_to_calculate:
            tastes.append(dict(taste_name='Sourness',
                                taste_value=self.calculate_sourness(total_ingredient_properties.get('AceticAcid', 0),
                                                    total_ingredient_properties.get('CitricAcid', 0)),
                                description='Sensory scale (0-100)'))
        if 'saltiness' in tastes_to_calculate:
            tastes.append(dict(taste_name='Saltiness',
                                taste_value=self.calculate_saltiness(total_ingredient_properties.get('Na', 0),
                                                    total_ingredient_properties.get('K', 0)),
                                description='Sensory scale (0-100)'))
        if 'tomato taste' in tastes_to_calculate:
            tastes.append(dict(taste_name='Tomato Taste', 
                                taste_value=self.calculate_tomato_taste(total_ingredient_properties.get('Protein', 0)),
                                description='Sensory scale (0-100)'))

        return dict(TasteTable=tastes)


    def calculate_sweetness(self, sucrose: float, fructose: float, glucose: float):
        # convert gram/litre to mmol/litre
        sucrose = sucrose / 342 * 1000
        fructose = fructose / 180 * 1000
        glucose = glucose / 180 * 1000

        # calculate taste
        return 100 * (1 - math.exp(-0.025 * (sucrose + 0.5 * fructose + 0.2 * glucose)))


    def calculate_sourness(self, acetic_acid: float, citric_acid: float):
        # convert gram/litre to mmol/litre
        acetic_acid = acetic_acid / 60 * 1000
        citric_acid = citric_acid / 192 * 1000

        # calculate taste
        return 100 * (1 - math.exp(-0.02 * (acetic_acid + 4 * citric_acid)))


    def calculate_saltiness(self, sodium: float, potassium: float):
        # convert gram/litre to mmol/litre
        sodium = sodium / 23 * 1000
        potassium = potassium / 39 * 1000

        # calculate taste
        return 100 * (1 - math.exp(-0.002 * (sodium + potassium)))


    def calculate_tomato_taste(self, protein: float):
        return 100 * (1 - math.exp(-0.2 * protein))
