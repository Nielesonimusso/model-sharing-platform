from datetime import datetime

import requests
from flask_jwt_extended import current_user
from unit_translation_component import Unit, Values
from unit_translation_component.exception import GenericException

from common_data_access.dtos import RunModelDtoSchema
from model_sharing_backend.src.graph_db.model_data_structure import GraphDbModelParameter
from model_sharing_backend.src.graph_db.queries.query_model import get_model
from model_sharing_backend.src.graph_db.queries.query_runner import SparQlRunner
from model_sharing_backend.src.models.food_product_models import FoodProduct
from model_sharing_backend.src.models.model_info import ModelInfo
from model_sharing_backend.src.models.simulation import ExecutedModel, ExecutedSimulation, Simulation
from model_sharing_backend.src.utils import gateway_service


def run_simulation(simulation: Simulation):
    executed_simulation = ExecutedSimulation(created_by=current_user, created_on=datetime.utcnow(),
                                             owner=current_user.company, simulation_id=simulation.id,
                                             executed_models=[])

    # TODO get list of models to run (incomplete)
    # TODO make data structure containing all data related to simulation [grouped by source] -> [with metadata!]
    # {
    #   source: {
    #       data: [{...},...], <- fetched (gateway_service.py)
    #       metadata: {...} <- interpreted ontology (data_structures.py)
    #   }  
    # }
        # TODO "fixed" sources (part of simulation definition)
        # TODO data sources
        # TODO model outputs (filled in once model is completed)
    # TODO loop over incomplete model list:
        # TODO get simulation bindings of model
        # TODO check whether data for all bindings is available =!> put model at end of incomplete model list
        # TODO build model input data using bindings
        # TODO run model with input data
        # TODO store model output in data structure
    # TODO leave loop with error if no models have all data available

    # get all bindings
    # fill all bindings (if possible)
        # if multiple columns from same source, then use label (ie "primary key") and match the others
        # also add extra information based on ontology (InterfaceProperties)
            # might require extra data sources other than the ones selected for the simulation!
        # ... implicit parameters not part of binding(?) (property - value - UNIT)
    # loop until all models complete:
        # run models that have completed bindings
        # update bindings with model results

    for model in simulation.models:
        if model.owner_id == current_user.company_id or any(
                filter(lambda p: p.company_id == current_user.company_id, model.permissions)):
            executed_model = run_model(model, simulation.food_product, current_user.username, simulation.id)
            executed_simulation.executed_models.append(executed_model)
    return executed_simulation.save()


def run_model(model: ModelInfo, food_product: FoodProduct, run_by: str, simulation_id: str) -> ExecutedModel:
    executed_model = ExecutedModel(model_id=model.id, created_on=datetime.utcnow())
    try:
        params = prepare_model_inputs(model, food_product)
        run_model_json = RunModelDtoSchema().dump({
            'simulation_id': simulation_id,
            'created_on': datetime.utcnow(),
            'created_by': run_by,
            'data': params
        })
        run_status = gateway_service.request_model_run(model.gateway_url, run_model_json)
        executed_model.client_run_id = run_status.run_id
    except ValueError as e:
        executed_model.error_message = str(e)
    except requests.RequestException as e:
        executed_model.error_message = f'unable to reach model gateway at {model.gateway_url}. {str(e)}'
    except GenericException as e:
        executed_model.error_message = \
            f'error occurred during normalization process. Error code: {e.error}. Error message: "{e.message}"'

    return executed_model


def prepare_model_inputs(model: ModelInfo, food_product: FoodProduct) -> list:
    food_product_property_values = [{
        'name': 'product dosage',
        'amount': food_product.dosage,
        'amount_unit': food_product.dosage_unit
    }]
    food_product_property_values.extend(map(lambda ing:
                                            {
                                                'name': ing.name,
                                                'amount': ing.amount,
                                                'amount_unit': ing.amount_unit,
                                                'company_code': ing.company_code,
                                                'standard_code': ing.standard_code
                                            }, food_product.ingredients))
    # todo add other food product properties in the mapping

    model_inputs = get_model(model.ontology_uri, SparQlRunner()).inputs
    model_params = []
    food_prod_prop_name_map = dict(
        zip(map(lambda val: val['name'].casefold(), food_product_property_values), food_product_property_values))
    unavailable_params = []
    for model_input in model_inputs:
        param = None
        for label in model_input.labels:
            param = param or food_prod_prop_name_map.get(label.name.casefold(), None)

        if param is None:
            unavailable_params.append(model_input)
        else:
            param = _convert_param_to_input_unit(param, model_input, food_product.dosage, food_product.dosage_unit)
            model_params.append(param)

    if len(unavailable_params) > 0:
        err_msg = f'Following input parameters are missing for executing model "{model.name}": '
        err_msg += ' and '.join([f'{" or ".join(map(lambda l: l.name, p.labels))}' for p in unavailable_params])
        raise ValueError(err_msg)

    return model_params


def _convert_param_to_input_unit(param: dict, model_input: GraphDbModelParameter, dosage: float, dosage_unit_name: str):
    param_unit = Unit(param['amount_unit'])
    input_unit = Unit(model_input.unit.uri, internal=True)
    if param_unit != input_unit:
        dosage_unit = Unit(dosage_unit_name)
        param_value = Values(dosage, dosage_unit, param['amount']) if param_unit == Unit('%', symbol=True) \
            else Values(param['amount'], param_unit)
        param['amount'] = param_value.to_unit(input_unit, Values(dosage, dosage_unit))
        param['amount_unit'] = input_unit.label
    return param
