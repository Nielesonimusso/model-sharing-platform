import requests
from flask import current_app
from werkzeug.exceptions import abort

from common_data_access.dtos import IngredientInfoWithPropertyInfosDtoSchema


def get_ingredient_properties(name):
    ingredient_url = current_app.config['INGREDIENT_SERVICE_URL']
    response = requests.get(f'{ingredient_url}/api/get_ingredient/{name}')
    if response.status_code != 200:
        abort(400, f'ingredient with name {name} not found.')
    json = response.json()
    return IngredientInfoWithPropertyInfosDtoSchema().load(json)
