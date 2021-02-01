import math
from typing import List

from .dtos import TasteDto


def calculate_taste(recipe, ingredients: List, tastes_to_calculate: List[str] = None) -> List[TasteDto]:
    tastes_to_calculate = tastes_to_calculate or ['sweetness', 'sourness', 'saltiness', 'tomato taste']
    product_density = 1
    water_to_add = 1000 - sum(ing.amount for ing in recipe.ingredients) * product_density
    total_ingredient_properties = dict()
    for ing in recipe.ingredients:
        ing.amount = ing.amount * recipe.dosage / 100
        ing.amount_unit = 'gram'

        ingredient = next(filter(lambda i: i.company_code == ing.company_code, ingredients), None)
        if ingredient == None:
            raise Exception(f'ingredient with code {ing.company_code} not found')

        for prp in ingredient.ingredient_properties:
            prp_in_recipe = ing.amount * prp.value / 100
            total_ingredient_properties[prp.name] = total_ingredient_properties.get(prp.name, 0) + prp_in_recipe

    if sum(a for a in total_ingredient_properties.values()) != recipe.dosage:
        print('dosage value does not match with calculated dosage')

    tastes = []
    if 'sweetness' in tastes_to_calculate:
        tastes.append(TasteDto('Sweetness',
                               calculate_sweetness(total_ingredient_properties.get('Sucrose', 0),
                                                   total_ingredient_properties.get('Fructose', 0),
                                                   total_ingredient_properties.get('Glucose', 0)),
                               'Sensory scale (0-100)'))
    if 'sourness' in tastes_to_calculate:
        tastes.append(TasteDto('Sourness',
                               calculate_sourness(total_ingredient_properties.get('AceticAcid', 0),
                                                  total_ingredient_properties.get('CitricAcid', 0)),
                               'Sensory scale (0-100)'))
    if 'saltiness' in tastes_to_calculate:
        tastes.append(TasteDto('Saltiness',
                               calculate_saltiness(total_ingredient_properties.get('Na', 0),
                                                   total_ingredient_properties.get('K', 0)),
                               'Sensory scale (0-100)'))
    if 'tomato taste' in tastes_to_calculate:
        tastes.append(TasteDto('Tomato Taste', calculate_tomato_taste(total_ingredient_properties.get('Protein', 0)),
                               'Sensory scale (0-100)'))

    return tastes


def calculate_sweetness(sucrose: float, fructose: float, glucose: float):
    # convert gram/litre to mmol/litre
    sucrose = sucrose / 342 * 1000
    fructose = fructose / 180 * 1000
    glucose = glucose / 180 * 1000

    # calculate taste
    return 100 * (1 - math.exp(-0.025 * (sucrose + 0.5 * fructose + 0.2 * glucose)))


def calculate_sourness(acetic_acid: float, citric_acid: float):
    # convert gram/litre to mmol/litre
    acetic_acid = acetic_acid / 60 * 1000
    citric_acid = citric_acid / 192 * 1000

    # calculate taste
    return 100 * (1 - math.exp(-0.02 * (acetic_acid + 4 * citric_acid)))


def calculate_saltiness(sodium: float, potassium: float):
    # convert gram/litre to mmol/litre
    sodium = sodium / 23 * 1000
    potassium = potassium / 39 * 1000

    # calculate taste
    return 100 * (1 - math.exp(-0.002 * (sodium + potassium)))


def calculate_tomato_taste(protein: float):
    return 100 * (1 - math.exp(-0.2 * protein))
