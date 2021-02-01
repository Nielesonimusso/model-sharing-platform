import csv
from typing import List

from common_data_access.db import create_db_connection
from common_data_access.db_initialize import BaseDbInitialize
from .db_models import Ingredient, IngredientProperty

_db = create_db_connection()


class IngredientDbInitialize(BaseDbInitialize):

    def _seed_database(self, **kwargs):
        data_file_path = kwargs.get('data_file_path')
        ingredients = self._read_csv(data_file_path)
        for ing in ingredients:
            _db.session.add(ing)

    def _read_csv(self, file_path: str) -> List[Ingredient]:
        ingredient_dictionary = dict()
        with open(file_path, 'r') as input_file:
            next(input_file)
            for line in csv.reader(input_file):
                line = [str.strip(ln) for ln in line]
                ingredient = ingredient_dictionary.get(line[1], Ingredient(name=line[0], company_code=line[1],
                                                                           standard_code=line[1]))
                ingredient.ingredient_properties.append(
                    IngredientProperty(name=line[2], value_text=line[3], value=float(line[4]), unit=line[5]))
                ingredient_dictionary[line[1]] = ingredient
        return list(ingredient_dictionary.values())
