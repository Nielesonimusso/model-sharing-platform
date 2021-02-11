import math
import json
from typing import List

from .dtos import NutritionDto
from flask import current_app

def calculate_nutrition(recipe, ingredients: List) -> List[NutritionDto]:
    current_app.logger.info(recipe)
    current_app.logger.info(ingredients)

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

    current_app.logger.info(total_ingredient_properties)

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

    current_app.logger.info(json.dumps(relevant_ingredients))

    nutrition_table = {
        'Energy':        [4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 9, 4],
        'Fats':          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        'Carbohydrates': [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        'Sugars':        [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'Protein':       [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        'Salt':          [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        'Water':         [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    }

    current_app.logger.info(json.dumps(nutrition_table))

    nutritions = []
    for nutrition_name, table in nutrition_table.items():
        nutritions.append(NutritionDto(nutrition_name, 
            sum([x*y for x,y in zip(table, relevant_ingredients)]), 
            'kcal' if nutrition_name == "Energy" else 'gram'))

    return nutritions