from datetime import datetime

import requests
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user
from werkzeug.exceptions import abort

from common_data_access.dtos import ModelResultDtoSchema, ModelRunStatusDtoSchema, ModelRunStatus
from common_data_access.json_extension import get_json
from model_sharing_backend.src.models.simulation import Simulation, ExecutedSimulation, \
    ExecutedSimulationDtoSchema, SimulationResultsDtoSchema, SimulationWithExecutionsSchema, \
    SimulationStatusDtoSchema
from model_sharing_backend.src.utils import model_runner, gateway_service

simulation_bp = Blueprint('Simulation', __name__)


@simulation_bp.route('/simulations', methods=['GET'])
@jwt_required
def get_all_simulations():
    """
    Get all Simulations owned by logged in users organization
    ---
    tags:
        -   Simulation
    security:
        - bearer: []
    responses:
        200:
            description: A list of all simulations.
            schema:
                type: array
                items:
                    $ref: '#/definitions/SimulationDb'
    """
    return get_json(Simulation.query.get_all_owned_by(current_user.company_id), Simulation.SimulationDbSchema,
                    {'company_id': current_user.company_id})


@simulation_bp.route('/simulation/<simulation_id>', methods=['GET'])
@jwt_required
def get_simulation(simulation_id: str):
    """
    Get a simulation by id
    ---
    tags:
        -   Simulation
    security:
        - bearer: []
    parameters:
        -   name: simulation_id
            in: path
            description: id of the simulation to fetch
            required: true
            type: string
    responses:
        200:
            description: Simulation with specified id
            schema:
                $ref: '#/definitions/SimulationWithExecutions'
        404:
            description: Simulation with this ID does not exist or not owned by current user's company
    """
    return get_json(Simulation.query.get_owned_or_404(current_user.company_id, simulation_id),
                    SimulationWithExecutionsSchema, {'company_id': current_user.company_id})


@simulation_bp.route('/simulation/<simulation_id>', methods=['DELETE'])
@jwt_required
def delete_simulation(simulation_id: str):
    """
    Remove simulation by id from DB
    ---
    tags:
        -   Simulation
    security:
        - bearer: []
    parameters:
        -   name: simulation_id
            in: path
            description: id of the simulation to remove
            required: true
            type: string
    responses:
        200:
            description: Successfully removed simulation
        404:
            description: Simulation with this ID does not exist or not deletable by current user
        400:
            description: Simulation can not be deleted. It has already been executed.
    """
    simulation = Simulation.query.get_created_by_or_404(current_user.id, simulation_id)
    if len(simulation.executions or []):
        abort(400, description='simulation has already been executed')
    simulation.delete()
    return {}


@simulation_bp.route('/run_simulation/<simulation_id>', methods=['POST'])
@jwt_required
def run_simulation(simulation_id: str):
    """
    Run one or more models on a product
    ---
    tags:
        -   Simulation
    security:
        - bearer: []
    parameters:
        -   name: simulation_id
            in: path
            description: id of simulation
            required: true
    responses:
        200:
            description: simulation submitted for run
            schema:
                $ref: '#/definitions/ExecutedSimulationDto'
        404:
            description: simulation not found or not owned by current user's company
        400:
            description: simulation execution failed
    """
    simulation = Simulation.query.get_owned_or_404(current_user.company_id, simulation_id)
    simulation.models = simulation.models or []
    executed_simulation = model_runner.run_simulation(simulation)
    return get_json(executed_simulation, ExecutedSimulationDtoSchema)


@simulation_bp.route('/simulation/<simulation_id>', methods=['PUT'])
@jwt_required
def update_simulation(simulation_id: str):
    """
    Update a simulation
    ---
    tags:
        -   Simulation
    security:
        - bearer: []
    parameters:
        -   name: simulation_id
            in: path
            description: id of simulation
            required: true
        -   name: simulation
            in: body
            description: simulation data
            required: true
            schema:
                $ref: '#/definitions/SimulationDb'
    responses:
        200:
            description: simulation updated
            schema:
                $ref: '#/definitions/SimulationDb'
        404:
            description: simulation not found or not owned by current user's company or not connected
    """
    simulation_db = Simulation.query.get_created_by_or_404(current_user.id, simulation_id)
    simulation_new = Simulation.SimulationDbSchema(context={'company_id': current_user.company_id}).load(request.json)
    simulation_db.name = simulation_new.name
    simulation_db.description = simulation_new.description
    simulation_db.food_product_id = simulation_new.food_product_id
    simulation_db.models = simulation_new.models
    return get_json(simulation_db.update(), Simulation.SimulationDbSchema, {'company_id': current_user.company_id})


@simulation_bp.route('/simulation', methods=['POST'])
@jwt_required
def create_simulation():
    """
    Create a simulation
    ---
    tags:
        -   Simulation
    security:
        - bearer: []
    parameters:
        -   name: simulation
            in: body
            description: simulation data
            required: true
            schema:
                $ref: '#/definitions/SimulationDb'
    responses:
        201:
            description: simulation created
            schema:
                $ref: '#/definitions/SimulationDb'
        404:
            description: used models/products not found or not accessible or not connected
    """
    simulation = Simulation.SimulationDbSchema(context={'company_id': current_user.company_id}).load(request.json)
    simulation.created_by = current_user
    simulation.owner = current_user.company
    simulation.created_on = datetime.utcnow()
    return get_json(simulation.add(), Simulation.SimulationDbSchema, {'company_id': current_user.company_id}), 201


@simulation_bp.route('/simulation_result/<simulation_execution_id>', methods=['GET'])
@jwt_required
def get_simulation_results(simulation_execution_id: str):
    """
    Get the results of a simulation
    ---
    tags:
        -   Simulation
    security:
        - bearer: []
    parameters:
        -   name: simulation_execution_id
            in: path
            description: id of the simulation job/run
            required: true
            schema:
                type: string
    responses:
        200:
            description: Simulation results for specified job id
            schema:
                $ref: '#/definitions/SimulationResultsDto'
        404:
            description: simulation job with simulation_execution_id not found or not accessible
    """
    executed_simulation = ExecutedSimulation.query.get_owned_or_404(current_user.company_id, simulation_execution_id)
    executed_simulation.results = []
    for executed_model in executed_simulation.executed_models:
        if not executed_model.client_run_id:
            model_result = ModelResultDtoSchema().load(
                {'model_name': executed_model.model.name, 'result': [{'error': executed_model.error_message}],
                 'status': ModelRunStatus.FAILED.value, 'created_on': str(executed_model.created_on)})
        else:
            try:
                model_result = gateway_service.get_model_run_result(executed_model.model.gateway_url,
                                                                    executed_model.client_run_id)
            except requests.RequestException as e:
                model_result = ModelResultDtoSchema().load(
                    {'model_name': executed_model.model.name,
                     'result': [{'error': f'error while communicating {executed_model.model.gateway_url}. {str(e)}'}],
                     'status': ModelRunStatus.UNREACHABLE.value, 'created_on': str(executed_model.created_on)})

        model_result.model_id = executed_model.model_id
        executed_simulation.results.append(model_result)
    return get_json(executed_simulation, SimulationResultsDtoSchema)


@simulation_bp.route('/simulation_status/<simulation_execution_id>', methods=['GET'])
@jwt_required
def get_simulation_status(simulation_execution_id):
    """
    Get status of a specific simulation run
    ---
    tags:
        -   Simulation
    security:
        - bearer: []
    parameters:
        -   name: simulation_execution_id
            in: path
            description: id of the simulation job/run
            required: true
    responses:
        200:
            description: status of all models in the simulation
            schema:
                $ref: '#/definitions/SimulationStatusDto'
        404:
            description: simulation run was not found or not accessible
    """
    executed_simulation = ExecutedSimulation.query.get_owned_or_404(current_user.company_id, simulation_execution_id)
    executed_simulation.model_statuses = []
    for executed_model in executed_simulation.executed_models:
        if not executed_model.client_run_id:
            model_status = ModelRunStatusDtoSchema().load(
                {'created_on': str(executed_model.created_on), 'status': ModelRunStatus.FAILED.value})
        else:
            try:
                model_status = gateway_service.get_model_run_status(executed_model.model.gateway_url,
                                                                    executed_model.client_run_id)
            except:
                model_status = ModelRunStatusDtoSchema().load(
                    {'created_on': str(executed_model.created_on), 'status': ModelRunStatus.UNREACHABLE.value})
        model_status.model_id = executed_model.model_id
        executed_simulation.model_statuses.append(model_status)
    return get_json(executed_simulation, SimulationStatusDtoSchema)
