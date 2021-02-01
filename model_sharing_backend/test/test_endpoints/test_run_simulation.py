import json

from .dummy_data import create_simulation_dict, create_unilever_tomato_soup_map, create_unilever_tomato_soup_model, \
    create_model_info_dict, create_food_product_map, create_unilever_tomato_soup_map_with_different_units
from .web_client import client_with_auth

# noinspection PyStatementEffect
# importing this is necessary. this statement
# stops pyCharm from removing the import
client_with_auth


def test_end_to_end_with_invalid_model_gateway_url(client_with_auth):
    # create product
    response = client_with_auth.post('/api/product', data=json.dumps(create_unilever_tomato_soup_map()),
                                     content_type='application/json')
    assert response.status_code == 201
    product_id = response.json['id']

    # create model
    model = create_unilever_tomato_soup_model()
    model['gateway_url'] = 'http://tomatosoup:8080'
    response = client_with_auth.post('/api/model', data=json.dumps(model),
                                     content_type='application/json')
    assert response.status_code == 201
    model_id = response.json['id']

    simulation_execution_id = _assert_successfully_create_and_run_simulation(client_with_auth, [model_id], product_id)
    _assert_model_status_and_result(client_with_auth, simulation_execution_id, 'failed')


def test_end_to_end_with_invalid_model_and_food_product(client_with_auth):
    # create product
    response = client_with_auth.post('/api/product', data=json.dumps(create_food_product_map()),
                                     content_type='application/json')
    assert response.status_code == 201
    product_id = response.json['id']

    # create model
    response = client_with_auth.post('/api/model', data=json.dumps(create_model_info_dict()),
                                     content_type='application/json')
    assert response.status_code == 201
    model_id = response.json['id']

    simulation_execution_id = _assert_successfully_create_and_run_simulation(client_with_auth, [model_id], product_id)
    _assert_model_status_and_result(client_with_auth, simulation_execution_id, 'failed')


def test_end_to_end_with_valid_tomato_soup(client_with_auth):
    # create product
    response = client_with_auth.post('/api/product', data=json.dumps(create_unilever_tomato_soup_map()),
                                     content_type='application/json')
    assert response.status_code == 201
    product_id = response.json['id']

    # create model
    response = client_with_auth.post('/api/model', data=json.dumps(create_unilever_tomato_soup_model()),
                                     content_type='application/json')
    assert response.status_code == 201
    model_id = response.json['id']

    simulation_execution_id = _assert_successfully_create_and_run_simulation(client_with_auth, [model_id], product_id)
    _assert_model_status_and_result(client_with_auth, simulation_execution_id, 'success')


def test_end_to_end_with_valid_tomato_soup_with_different_units(client_with_auth):
    # create product
    response = client_with_auth.post('/api/product', content_type='application/json',
                                     data=json.dumps(create_unilever_tomato_soup_map_with_different_units()))
    assert response.status_code == 201
    product_id = response.json['id']

    # create model
    response = client_with_auth.post('/api/model', data=json.dumps(create_unilever_tomato_soup_model()),
                                     content_type='application/json')
    assert response.status_code == 201
    model_id = response.json['id']

    simulation_execution_id = _assert_successfully_create_and_run_simulation(client_with_auth, [model_id], product_id)
    _assert_model_status_and_result(client_with_auth, simulation_execution_id, 'success')


def _assert_successfully_create_and_run_simulation(client_with_auth, model_ids, product_id):
    # create simulation
    response = client_with_auth.post('/api/simulation', data=json.dumps(create_simulation_dict(model_ids, product_id)),
                                     content_type='application/json')
    assert response.status_code == 201
    simulation_id = response.json['id']
    models = response.json['models']

    # run simulation
    response = client_with_auth.post(f'/api/run_simulation/{simulation_id}', content_type='application/json')
    assert response.status_code == 200
    simulation_execution_id = response.json['simulation_execution_id']
    assert len(models) == len(response.json['executed_models'])
    return simulation_execution_id


def _assert_model_status_and_result(client_with_auth, simulation_execution_id, status):
    # get simulation status
    response = client_with_auth.get(f'/api/simulation_status/{simulation_execution_id}',
                                    content_type='application/json')
    assert response.status_code == 200
    assert response.is_json
    assert len(response.json['model_statuses']) > 0
    assert all(map(lambda s: s['status'] == status, response.json['model_statuses']))

    # get simulation results
    response = client_with_auth.get(f'/api/simulation_result/{simulation_execution_id}',
                                    content_type='application/json')
    assert response.status_code == 200
    assert response.is_json
    assert len(response.json['results']) > 0
    assert all(map(lambda s: s['status'] == status, response.json['results']))
