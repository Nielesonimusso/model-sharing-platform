from datetime import datetime

from flask import request, current_app
from flask.blueprints import Blueprint
from werkzeug.exceptions import abort

from common_data_access import string_utils
from common_data_access.dtos import ModelRunStatus, ModelRunStatusDtoSchema, \
    ModelResultDtoSchema, RunModelDtoSchema, ModelRunParameterSchema
from common_data_access.json_extension import get_json
from .db import SimulationRun
from .dtos import TasteSchema, RecipeSchema
from .ingredient_store import get_ingredient_properties
from .tomato_soup_taste_model import calculate_taste

routes_blueprint = Blueprint('gateway', __name__)


@routes_blueprint.route('/', methods=['GET'])
def index():
    return 'This is the front page of the gateway'


@routes_blueprint.route('/run_model', methods=['POST'])
def run_model():
    model_run_request = RunModelDtoSchema().load(request.json)
    simulation_run = SimulationRun(submitted_on=datetime.utcnow(),
                                   submitted_by=model_run_request.created_by,
                                   status=ModelRunStatus.SUBMITTED,
                                   parameters=request.json).save()

    recipe = __create_recipe_from_data(model_run_request.data)
    taste = calculate_taste(recipe, [get_ingredient_properties(i.company_code) for i in recipe.ingredients],
                            current_app.config['TASTES_TO_CALCULATE'])
    simulation_run.result = TasteSchema().dump(taste, many=True)
    simulation_run.completed_on = datetime.utcnow()
    simulation_run.status = ModelRunStatus.SUCCESS
    simulation_run.save()

    return get_json({
        'created_on': simulation_run.submitted_on,
        'run_id': simulation_run.id,
        'status': ModelRunStatus.SUBMITTED.value
    }, ModelRunStatusDtoSchema), 201


@routes_blueprint.route('/get_result/<run_id>', methods=['GET'])
def get_result(run_id: str):
    simulation_run = SimulationRun.query.get_or_404(run_id)
    result = ModelResultDtoSchema()
    result.created_on = simulation_run.submitted_on
    result.model_name = 'tomato soup taste'
    result.ran_on = simulation_run.completed_on
    result.status = simulation_run.status.value
    result.result = simulation_run.result
    return get_json(result, ModelResultDtoSchema)


@routes_blueprint.route('/get_model_run_state/<run_id>', methods=['GET'])
def get_model_run_state(run_id: str):
    simulation_run = SimulationRun.query.get_or_404(run_id)
    return get_json({
        'created_on': simulation_run.submitted_on,
        'run_id': simulation_run.id,
        'status': simulation_run.status.value
    }, ModelRunStatusDtoSchema), 200


def __create_recipe_from_data(params: list):
    dosage = __filter_dosage(params)
    params.remove(dosage)
    return RecipeSchema().load(
        dict(dosage=dosage.amount, dosage_unit=dosage.amount_unit,
             ingredients=ModelRunParameterSchema(many=True).dump(params)))


def __filter_dosage(params: list):
    try:
        return next(filter(
            lambda i: string_utils.are_almost_equal(i.name, 'product dosage', mismatch_ratio=.3), params))
    except StopIteration:
        abort(400, description='model requires product dosage but not found')
