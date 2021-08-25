from flask import Blueprint

from common_data_access.json_extension import get_json
from ingredient_data_service.src.data.db_models import Ingredient

routes_blueprint = Blueprint('ingredient_data', __name__)

@routes_blueprint.route('/get_all_ingredients', methods=['GET'])
def get_all_ingredients():
    return get_json(Ingredient.query.get_all(), Ingredient.IngredientSchema)


@routes_blueprint.route('/get_similar_ingredient/<name>', methods=['GET'])
def get_similar_ingredient(name: str):
    return get_json(Ingredient.query.get_column_like(name, Ingredient.name),
                    Ingredient.IngredientSchema)


@routes_blueprint.route('/get_ingredient/<name>', methods=['GET'])
def get_ingredient(name: str):
    return get_json(Ingredient.query.get_one_where_or_404(Ingredient.name == name),
                    Ingredient.IngredientWithPropertiesSchema)
