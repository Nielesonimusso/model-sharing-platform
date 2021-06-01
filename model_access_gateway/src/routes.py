from datetime import datetime
from functools import partial
from typing import Any, Dict

from flask import request, current_app, make_response
from flask.blueprints import Blueprint
from marshmallow import fields

from common_data_access.dtos import ModelRunStatus, ModelRunStatusDtoSchema, \
    ModelResultDtoSchema, RunModelDtoSchema
from common_data_access.json_extension import get_json
from model_access_gateway.run import shared_scheduler
from model_access_gateway.src.models.model import Model
from model_access_gateway.src.models.nutrition_model import NutritionModel
from .db import SimulationRun
from .models.tomato_soup_taste_model import TasteModel
from concurrent.futures import Future

routes_blueprint = Blueprint('gateway', __name__)


@routes_blueprint.route('/', methods=['GET'])
def index():
    return 'This is the front page of the gateway'


def get_model(app) -> Model:
    models: Dict[str, Model] = dict(
        taste=TasteModel(app.config.get('TASTES_TO_CALCULATE', None)),
        nutrition=NutritionModel(),
        pasteurization=None,
        shelflife=None,
        calibration=None,
        dropletsize=None
    )

    model: Model = models.get(app.config['MODEL'])

    return model
    

@routes_blueprint.route('/ontology.ttl', methods=['GET'])
def get_ontology() -> str:

    model: Model = get_model(current_app)
    response = make_response(model.get_ontology(), 200)
    response.mimetype = 'text/plain'
    return response

@routes_blueprint.route('/run_model', methods=['POST'])
def run_model():

    model: Model = get_model(current_app)

    input_dto = type(f'Run{type(model).__name__}DtoSchema', (RunModelDtoSchema, ), dict(
        data = fields.Nested(model.input_dto),
        Meta = type(f'Run{type(model).__name__}DtoSchemaMeta',
            (getattr(RunModelDtoSchema, "Meta", object), ), dict(
                fields=('simulation_id','data',)
            ))
    ))

    model_run_request = input_dto().load(request.json)
    simulation_run = SimulationRun(submitted_on=datetime.utcnow(),
                                #    submitted_by=model_run_request.created_by,
                                   status=ModelRunStatus.SUBMITTED,
                                   parameters=request.json).save()

    def handle_result(run_id, future: Future):

        sr = SimulationRun.query.get(run_id)
        result = future.result()
        sr.result = model.output_dto(many=True).dump(result)

        sr.completed_on = datetime.utcnow()
        sr.status = ModelRunStatus.SUCCESS
        sr.save()

    shared_scheduler().submit(model.run_model, model_run_request.data).\
        add_done_callback(partial(handle_result, simulation_run.id))

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

