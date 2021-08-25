from datetime import datetime
from typing import Dict, Generator, List

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
from model_sharing_backend.src.models.simulation import ArgumentBinding, ExecutedModel, ExecutedModelDtoSchema, ExecutedSimulation, ExecutedSimulationDtoSchema, Simulation, SimulationBindingTypes
from model_sharing_backend.src.ontology_services.data_structures import TableDefinition
from model_sharing_backend.src.utils import gateway_service


def run_simulation(simulation: Simulation):
    executed_simulation = ExecutedSimulation(created_by=current_user, created_on=datetime.utcnow(),
                                             owner=current_user.company, simulation_id=simulation.id,
                                             executed_models=[])

    complete_models_list: List[ModelInfo] = []

    simulation_data: Dict = dict()
    # make data structure for holding data and model results
    for data_source in simulation.data_sources:
        data = gateway_service.fetch_data_source_data(data_source.gateway_url)
        metadata = gateway_service.fetch_data_source_metadata(data_source.gateway_url, data_source.ontology_uri)
        
        simulation_data[data_source.ontology_uri] = dict(
            data=data,
            metadata=metadata
        )

    print("entering while loop for simu")
    previous_complete_length = 0
    while len(complete_models_list) < len(simulation.models): 
        print("loop", len(complete_models_list), len(simulation.models))
        # loop over incomplete models
        for incomplete_model in (model for model in simulation.models if 
        not any((c_model.id == model.id for c_model in complete_models_list))):
                print("running model", incomplete_model.name)
            # try:
                # check access rights
                if incomplete_model.owner_id == current_user.company_id or any(
                filter(lambda p: p.company_id == current_user.company_id, incomplete_model.permissions)):
                    executed_model = run_model(incomplete_model, 
                        (binding for binding in simulation.bindings if binding.model_uri == incomplete_model.ontology_uri), 
                        simulation_data, current_user.username, simulation.id)
                    executed_simulation.executed_models.append(executed_model)
                    complete_models_list.append(incomplete_model)
                    
                    # add model results to simulation_data (for use by other models)
                    model_results = gateway_service.get_model_run_result(incomplete_model.gateway_url,
                        executed_model.client_run_id)
                    model_metadata = dict() # TODO add metadata from model outputs
                    simulation_data[incomplete_model.ontology_uri] = dict(
                        data=model_results,
                        metadata=model_metadata
                    )
                    
            # except Exception as ex:
                # pass #handle problem with preparing inputs (incomplete data for example)
        if len(complete_models_list) <= previous_complete_length:
            print("some models left that do not complete; failing them")
            # if no more models completed this loop, cancel remaining and set errors
            for incomplete_model in (model for model in simulation.models if 
            not any((c_model.id == model.id for c_model in complete_models_list))):
                failed_model = ExecutedModelDtoSchema.load(dict(
                    error_message="Not all input data available for this model",
                    created_on=datetime.utcnow(),
                    model_id=incomplete_model.id,
                ))
                executed_simulation.executed_models.append(failed_model)
            break
        else:
            print("completed new models this round")
            previous_complete_length = len(complete_models_list)
    print("no more model rounds")
    print(ExecutedSimulationDtoSchema().dumps(executed_simulation))
    return executed_simulation.save()
    # get list of models to run (incomplete)
    # make data structure containing all data related to simulation [grouped by source] -> [with metadata!]
    # {
    #   source: {
    #       data: [{...},...], <- fetched (gateway_service.py)
    #       metadata: {...} <- interpreted ontology (data_structures.py)
    #   }  
    # }
        # "fixed" sources (part of simulation definition)
        # TODO data sources
        # TODO model outputs (filled in once model is completed)
    # TODO loop over incomplete model list:
        # get simulation bindings of model
        # check whether data for all bindings is available =!> skip model for next run
        # build model input data using bindings
        # run model with input data
        # TODO store model output in data structure
    # leave loop with error if no models have all data available

    # get all bindings
    # fill all bindings (if possible)
        # if multiple columns from same source, then use label (ie "primary key") and match the others
        # also add extra information based on ontology (InterfaceProperties)
            # might require extra data sources other than the ones selected for the simulation!
        # ... implicit parameters not part of binding(?) (property - value - UNIT)
    # loop until all models complete:
        # run models that have completed bindings
        # update bindings with model results


def run_model(model: ModelInfo, model_bindings: Generator[ArgumentBinding, None, None], available_data: Dict,
    run_by: str, simulation_id: str) -> ExecutedModel:
    executed_model = ExecutedModel(model_id=model.id, created_on=datetime.utcnow())
    try:
        params = prepare_model_inputs(model_bindings, available_data)
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
        executed_model.error_message = f'unable to reach model gateway at {model.gateway_url}. {str(e)}. {str(e.response.content)}. {str(e.request.body)}'
    except GenericException as e:
        executed_model.error_message = \
            f'error occurred during normalization process. Error code: {e.error}. Error message: "{e.message}"'

    return executed_model


def prepare_model_inputs(model_bindings: Generator[ArgumentBinding, None, None], available_data: Dict) -> Dict:
    model_input = dict()

    for argument_binding in model_bindings:
        model_input[argument_binding.argument_name] = list()
        argument_per_column = dict()
        for column_binding in argument_binding.columns:
            
            if column_binding.source_type == SimulationBindingTypes.INPUT:
                # directly gather column data from source array
                argument_per_column[column_binding.target_column.name] = column_binding.source_name.split('|')
            else:
                # TODO gather data from available_data, if not available then raise exception
                pass

            # TODO apply unit conversion on column data

        # length of argument is the shortest of the columns 
        argument_length = min(len(arg_data) for arg_data in argument_per_column.values())

        for row in range(argument_length):
            row_dict = dict()
            for argument_column_name, argument_column_values in argument_per_column.items():
                row_dict[argument_column_name] = argument_column_values[row]
            model_input[argument_binding.argument_name].append(row_dict)

    # TODO unit conversion
    target_unit = column_binding.target_column.unit_uri # BUG NAIVE only for unit_type = "fixed"

    ### unit_type = none|fixed|column|concept
    ### unit_type = none -> unit-less: never convert
    ### unit_type = fixed -> unit from unit_uri (like above)
    ### unit_type = column -> unit from column referenced by unit_uri (ignore unit_source_uri)
    ### unit_type = concept -> unit from unit_uri property of unit_source_uri (unit_source_uri should be referenced in other column!!)
    ###     concept could be other referenced table

    ### required information for conversion target:
    ### `target_column` -> unit_type, unit_uri and unit_source_uri
    ### complete input data(!) to get column unit -> `model_input`
    ###     so only possible AFTER complete input is built
    ### (external) ontology information for CONCEPT type(?)

    ### required information for conversion source:
    ### `available_data` -> data and metadata
    ### (external) ontology information for CONCEPT type(?)


    return model_input


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
