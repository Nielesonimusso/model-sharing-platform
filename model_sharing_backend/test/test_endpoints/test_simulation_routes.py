import json

from .dummy_data import create_unilever_tomato_soup_map, create_model_info_dict, create_simulation_dict
from .web_client import client_with_auth

# noinspection PyStatementEffect
# importing this is necessary. this statement
# stops pyCharm from removing the import
client_with_auth


def test_create_and_get_simulations(client_with_auth):
    prod = __create_product(client_with_auth)
    model1 = __create_model(client_with_auth)
    model2 = __create_model(client_with_auth)

    simulation_dict = create_simulation_dict([model1['id'], model2['id']], prod['id'])
    response = client_with_auth.post('/api/simulation', data=json.dumps(simulation_dict),
                                     content_type='application/json', username='admin')
    assert response.status_code == 201

    response = client_with_auth.get(f'/api/simulation/{response.json["id"]}', content_type='application/json',
                                    username='admin')
    assert response.status_code == 200
    __assert_simulation_equal(simulation_dict, response.json)


def test_get_accessible_simulations_test(client_with_auth):
    model_count_per_user = [('admin', 10), ('johndoe', 20)]
    for username, count in model_count_per_user:
        model1 = __create_model(client_with_auth, username)
        model2 = __create_model(client_with_auth, username)
        prod = __create_product(client_with_auth, username)
        for _ in range(count):
            sim = create_simulation_dict([model1['id'], model2['id']], prod['id'])
            response = client_with_auth.post('/api/simulation', data=json.dumps(sim), content_type='application/json',
                                             username=username)
            assert response.status_code == 201

    for username, count in model_count_per_user:
        response = client_with_auth.get('/api/simulations', content_type='application/json', username=username)
        assert response.status_code == 200
        assert len(response.json) >= count


def test_simulation_not_accessible_from_other_organization(client_with_auth):
    model1 = __create_model(client_with_auth, 'admin')
    model2 = __create_model(client_with_auth, 'admin')
    prod = __create_product(client_with_auth, 'admin')
    sim = create_simulation_dict([model1['id'], model2['id']], prod['id'])
    response = client_with_auth.post('/api/simulation', data=json.dumps(sim), content_type='application/json',
                                     username='admin')
    assert response.status_code == 201

    response = client_with_auth.get(f'/api/simulation/{response.json["id"]}', content_type='application/json',
                                    username='johndoe')
    assert response.status_code == 404


def test_update_simulation(client_with_auth):
    model1 = __create_model(client_with_auth, 'admin')
    model2 = __create_model(client_with_auth, 'admin')
    prod1 = __create_product(client_with_auth, 'admin')
    sim1 = create_simulation_dict([model1['id'], model2['id']], prod1['id'])
    response = client_with_auth.post('/api/simulation', data=json.dumps(sim1), content_type='application/json',
                                     username='admin')
    assert response.status_code == 201

    prod2 = __create_product(client_with_auth, 'admin')
    model3 = __create_model(client_with_auth, 'admin')
    sim2 = create_simulation_dict([model3['id'], model2['id']], prod2['id'])
    response = client_with_auth.put(f'/api/simulation/{response.json["id"]}', data=json.dumps(sim2),
                                    content_type='application/json', username='admin')
    assert response.status_code == 200

    response = client_with_auth.get(f'/api/simulation/{response.json["id"]}', content_type='application/json',
                                    username='admin')
    assert response.status_code == 200
    __assert_simulation_equal(sim2, response.json)

    # update not possible by other user
    response = client_with_auth.get(f'/api/simulation/{response.json["id"]}', content_type='application/json',
                                    username='johndoe')
    assert response.status_code == 404


def test_delete_simulation(client_with_auth):
    model1 = __create_model(client_with_auth, 'admin')
    model2 = __create_model(client_with_auth, 'admin')
    prod1 = __create_product(client_with_auth, 'admin')
    sim1 = create_simulation_dict([model1['id'], model2['id']], prod1['id'])
    response = client_with_auth.post('/api/simulation', data=json.dumps(sim1), content_type='application/json',
                                     username='admin')
    assert response.status_code == 201
    response = client_with_auth.delete(f'/api/simulation/{response.json["id"]}', username='admin')
    assert response.status_code == 200


def test_no_delete_by_different_user(client_with_auth):
    model1 = __create_model(client_with_auth, 'admin')
    model2 = __create_model(client_with_auth, 'admin')
    prod1 = __create_product(client_with_auth, 'admin')
    sim1 = create_simulation_dict([model1['id'], model2['id']], prod1['id'])
    response = client_with_auth.post('/api/simulation', data=json.dumps(sim1), content_type='application/json',
                                     username='admin')
    assert response.status_code == 201
    response = client_with_auth.delete(f'/api/simulation/{response.json["id"]}', username='johndoe')
    assert response.status_code == 404


def test_use_unauthorized_model_or_product(client_with_auth):
    model1 = __create_model(client_with_auth, 'admin')
    model2 = __create_model(client_with_auth, 'johndoe')
    prod1 = __create_product(client_with_auth, 'janedoe')
    sim1 = create_simulation_dict([model1['id'], model2['id']], prod1['id'])
    response = client_with_auth.post('/api/simulation', data=json.dumps(sim1), content_type='application/json',
                                     username='admin')
    assert response.status_code == 404
    response = client_with_auth.post('/api/simulation', data=json.dumps(sim1), content_type='application/json',
                                     username='johndoe')
    assert response.status_code == 404


def test_use_model_with_execute_permission(client_with_auth):
    response = client_with_auth.get('/api/companies')
    assert response.status_code == 200
    company_ids = list(map(lambda i: i['id'], response.json))

    model1 = __create_model(client_with_auth, 'admin')
    model2 = __create_model(client_with_auth, 'johndoe')
    prod1 = __create_product(client_with_auth, 'janedoe')
    sim1 = create_simulation_dict([model1['id'], model2['id']], prod1['id'])

    # no permission to use
    response = client_with_auth.post('/api/simulation', data=json.dumps(sim1), content_type='application/json',
                                     username='admin')
    assert response.status_code == 404

    # allow permission to all companies
    permissions = list(
        map(lambda c_id: {'company_id': c_id, 'model_info_id': model2['id'], 'permission_type': 'execute'},
            company_ids))
    response = client_with_auth.put(f'/api/model/permissions/{model2["id"]}', data=json.dumps(permissions),
                                    content_type='application/json', username='johndoe')
    assert response.status_code == 200

    # allow permission to all companies
    response = client_with_auth.put(f'/api/product/permissions/{prod1["id"]}', data=json.dumps(company_ids),
                                    content_type='application/json', username='janedoe')
    assert response.status_code == 200

    response = client_with_auth.post('/api/simulation', data=json.dumps(sim1), content_type='application/json',
                                     username='admin')
    assert response.status_code == 201
    __assert_simulation_equal(sim1, response.json)


def test_use_model_with_view_permission_throw_error(client_with_auth):
    response = client_with_auth.get('/api/companies')
    assert response.status_code == 200
    company_ids = list(map(lambda i: i['id'], response.json))

    # add model and allow view permission to all companies
    model1 = __create_model(client_with_auth, 'admin')
    permissions = list(
        map(lambda c_id: {'company_id': c_id, 'model_info_id': model1['id'], 'permission_type': 'view'},
            company_ids))
    response = client_with_auth.put(f'/api/model/permissions/{model1["id"]}', data=json.dumps(permissions),
                                    content_type='application/json', username='admin')
    assert response.status_code == 200

    prod1 = __create_product(client_with_auth, 'janedoe')
    sim1 = create_simulation_dict([model1['id']], prod1['id'])
    response = client_with_auth.post('/api/simulation', data=json.dumps(sim1), content_type='application/json',
                                     username='janedoe')
    assert response.status_code == 404


def test_use_not_connected_model_throw_error(client_with_auth):
    model1 = __create_model(client_with_auth, 'admin')
    model2 = __create_model(client_with_auth, 'admin', is_connected=False)
    prod1 = __create_product(client_with_auth, 'admin')
    sim1 = create_simulation_dict([model1['id'], model2['id']], prod1['id'])
    response = client_with_auth.post('/api/simulation', data=json.dumps(sim1), content_type='application/json',
                                     username='admin')
    assert response.status_code == 404


def __create_product(client, username='admin'):
    response = client.post('/api/product', data=json.dumps(create_unilever_tomato_soup_map()),
                           content_type='application/json', username=username)
    assert response.status_code == 201
    return response.json


def __create_model(client, username='admin', is_connected=True):
    model_info_dict = create_model_info_dict()
    model_info_dict['is_connected'] = is_connected
    response = client.post('/api/model', data=json.dumps(model_info_dict),
                           content_type='application/json', username=username)
    assert response.status_code == 201
    return response.json


def __assert_simulation_equal(expected, reality):
    assert reality['name'] == expected['name']
    assert reality['description'] == expected['description']
    assert reality['food_product']['id'] == expected['food_product_id']
    assert len(reality['models']) == len(expected['model_ids'])
    for m in reality['models']:
        assert m['id'] in expected['model_ids']
        assert m['can_execute'] == True
