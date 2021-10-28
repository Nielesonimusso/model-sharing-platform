import sys
from datetime import datetime
from functools import partial
from typing import Any, Dict

from flask import request, current_app, make_response
from flask.blueprints import Blueprint
from marshmallow import fields
from marshmallow.schema import Schema

from common_data_access.dtos import ModelRunStatus, ModelRunStatusDtoSchema, \
    ModelResultDtoSchema, RunModelDtoSchema
from common_data_access.json_extension import get_json
from model_access_gateway.run import shared_scheduler
from model_access_gateway.src.models.model import Model
from model_access_gateway.src.models.nutrition_model import NutritionModel
from .db import SimulationRun
from .models.tomato_soup_taste_model import TasteModel
from concurrent.futures import Future
from ..src import get_model

routes_blueprint = Blueprint('gateway', __name__)


@routes_blueprint.route('/', methods=['GET'])
def index():
    return 'This is the front page of the gateway'


@routes_blueprint.route('/ontology.ttl', methods=['GET'])
def get_ontology() -> str:

    model: Model = get_model(current_app)
    response = make_response(model.get_ontology(), 200)
    response.mimetype = 'text/turtle'
    return response

@routes_blueprint.route('/run_model', methods=['POST'])
def run_model():

    model: Model = get_model(current_app)
    print(f'got model {model}', file=sys.stderr)
    input_dto = type(f'Run{type(model).__name__}DtoSchema', (RunModelDtoSchema, ), dict(
        data = fields.Nested(model.input_dto),
        Meta = type(f'Run{type(model).__name__}DtoSchemaMeta',
            (Schema.Meta, ), dict(register=False))
    ))
    print(f'got schema {input_dto}', file=sys.stderr)
    model_run_request = input_dto().load(request.json)
    print('got data', file=sys.stderr)
    simulation_run = SimulationRun(submitted_on=datetime.utcnow(),
                                #    submitted_by=model_run_request.created_by,
                                   status=ModelRunStatus.SUBMITTED,
                                   parameters=[]).save() # parameters are never used 
                                #   or displayed, but can be very large, so they are not stored

    print(f'saved simulation request entry')
    # TODO async model run code (as below); has issues with model chaining
    # def handle_result(run_id, future: Future):

    #     sr = SimulationRun.query.get(run_id)
    #     result = future.result()
    #     sr.result = result
    #     sr.completed_on = datetime.utcnow()
    #     if len(errors := model.output_dto(many=True).validate(result)) == 0 :
    #         sr.status = ModelRunStatus.SUCCESS
    #     else:
    #         sr.status = ModelRunStatus.FAILED
    #     sr.save()

    # shared_scheduler().submit(model.run_model, model_run_request.data).\
    #     add_done_callback(partial(handle_result, simulation_run.id))

    # return get_json({
    #     'created_on': simulation_run.submitted_on,
    #     'run_id': simulation_run.id,
    #     'status': ModelRunStatus.SUBMITTED.value
    # }, ModelRunStatusDtoSchema), 201
    print(f"running model...", file=sys.stderr)
    simulation_run.result = model.run_model(model_run_request.data)
    simulation_run.completed_on = datetime.utcnow()
    if len(errors := model.output_dto().validate(simulation_run.result)) == 0 :
        simulation_run.status = ModelRunStatus.SUCCESS
    else:
        simulation_run.status = ModelRunStatus.FAILED
    simulation_run.save()

    return get_json({
        'created_on': simulation_run.submitted_on,
        'run_id': simulation_run.id,
        'status': simulation_run.status.value
    }, ModelRunStatusDtoSchema), 201


@routes_blueprint.route('/get_result/<run_id>', methods=['GET'])
def get_result(run_id: str):
    simulation_run = SimulationRun.query.get_or_404(run_id)
    result = dict(
        created_on = simulation_run.submitted_on,
        model_name = get_model(current_app).name,
        ran_on = simulation_run.completed_on,
        status = simulation_run.status.value,
        result = simulation_run.result,
    )
    return get_json(result, ModelResultDtoSchema)


@routes_blueprint.route('/get_model_run_state/<run_id>', methods=['GET'])
def get_model_run_state(run_id: str):
    simulation_run = SimulationRun.query.get_or_404(run_id)
    return get_json({
        'created_on': simulation_run.submitted_on,
        'run_id': simulation_run.id,
        'status': simulation_run.status.value
    }, ModelRunStatusDtoSchema), 200

