import sys

import requests

from common_data_access.dtos import GatewayPaths, ModelResultDtoSchema, ModelRunStatusDtoSchema
from model_sharing_backend.src.models.simulation import ModelRunStatusWithModelIdDtoSchema


def request_model_run(gateway_url: str, data: any):
    try:
        response_json = __make_request(f'{gateway_url.rstrip("/")}/{GatewayPaths.model_run}', requests.post, json=data)
        return ModelRunStatusDtoSchema().load(response_json)
    except requests.RequestException as e:
        print(f'error while communicating {gateway_url}. {str(e)}', file=sys.stdout)
        raise e


def get_model_run_result(gateway_url: str, run_id: str):
    try:
        response_json = __make_request(f'{gateway_url.rstrip("/")}/{GatewayPaths.model_result}/{run_id}', requests.get)
        return ModelResultDtoSchema().load(response_json)
    except requests.RequestException as e:
        print(f'error while communicating {gateway_url}. {str(e)}', file=sys.stdout)
        raise e


def get_model_run_status(gateway_url: str, run_id: str):
    try:
        response_json = __make_request(f'{gateway_url.rstrip("/")}/{GatewayPaths.model_status}/{run_id}', requests.get)
        return ModelRunStatusWithModelIdDtoSchema().load(response_json)
    except requests.RequestException as e:
        print(f'error while communicating {gateway_url}. {str(e)}', file=sys.stdout)
        raise e


def fetch_data_source_data(gateway_url: str):
    try:
        return __make_request(f'{gateway_url.rstrip("/")}/data.json', requests.get)
    except requests.RequestException as e:
        print(f'error while communicating {gateway_url}. {str(e)}', file=sys.stdout)
        raise e


def __make_request(url: str, method: any, **kwargs):
    try:
        response = method(url, timeout=5, **kwargs)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, requests.HTTPError) as e:
        print(e, file=sys.stderr)
        raise e
