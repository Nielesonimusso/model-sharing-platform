import json

from faker import Faker

from model_sharing_backend.test.assert_utils import assert_dict_equal
from .dummy_data import create_model_info_dict, create_simulation_dict, create_food_product_map
from .web_client import client_with_auth

# noinspection PyStatementEffect
# importing this is necessary. this statement
# stops pyCharm from removing the import
client_with_auth

__faker = Faker()


def test_model_create_and_get(client_with_auth):
    model_info = create_model_info_dict()
    response = client_with_auth.post('/api/model', data=json.dumps(model_info),
                                     content_type='application/json', username='admin')
    assert response.status_code == 201
    response = client_with_auth.get(f'/api/model/{response.json["id"]}', username='admin')
    assert response.status_code == 200
    assert response.is_json
    assert_dict_equal(model_info, response.json, [])


def test_model_not_accessible_by_other_company(client_with_auth):
    response = client_with_auth.post('/api/model', data=json.dumps(create_model_info_dict()),
                                     content_type='application/json', username='admin')
    assert response.status_code == 201
    response = client_with_auth.get(f'/api/model/{response.json["id"]}', username='johndoe')
    assert response.status_code == 404


def test_model_create_and_delete(client_with_auth):
    response = client_with_auth.post('/api/model', data=json.dumps(create_model_info_dict()),
                                     content_type='application/json', username='johndoe')
    assert response.status_code == 201
    response = client_with_auth.delete(f'/api/model/{response.json["id"]}', username='johndoe')
    assert response.status_code == 200


def test_model_not_deletable_by_other_people(client_with_auth):
    response = client_with_auth.post('/api/model', data=json.dumps(create_model_info_dict()),
                                     content_type='application/json', username='johndoe')
    assert response.status_code == 201
    response = client_with_auth.delete(f'/api/model/{response.json["id"]}', username='janedoe')
    assert response.status_code == 404


def test_model_create_and_update(client_with_auth):
    model_info = create_model_info_dict()
    response = client_with_auth.post('/api/model', data=json.dumps(model_info), content_type='application/json')
    assert response.status_code == 201
    model_id = response.json['id']

    model_info_edited = create_model_info_dict()
    model_info_edited['id'] = model_id

    response = client_with_auth.put(f'/api/model/{model_id}', data=json.dumps(model_info_edited),
                                    content_type='application/json')
    assert response.status_code == 200

    response = client_with_auth.get(f'/api/model/{model_id}')
    assert response.is_json
    assert_dict_equal(model_info_edited, response.json, [])


def test_model_not_update_by_other_user(client_with_auth):
    model_info = create_model_info_dict()
    response = client_with_auth.post('/api/model', data=json.dumps(model_info), content_type='application/json',
                                     username='admin')
    assert response.status_code == 201
    model_id = response.json['id']

    model_info_edited = create_model_info_dict()
    model_info_edited['id'] = model_id

    response = client_with_auth.put(f'/api/model/{model_id}', data=json.dumps(model_info_edited),
                                    content_type='application/json', username='johndoe')
    assert response.status_code == 404


def test_model_access_to_other_company(client_with_auth):
    response = client_with_auth.post('/api/model', data=json.dumps(create_model_info_dict()),
                                     content_type='application/json', username='admin')
    assert response.status_code == 201
    assert response.json['can_execute']
    model_id = response.json['id']

    # owner can access
    response = client_with_auth.get(f'/api/model/{model_id}', content_type='application/json', username='admin')
    assert response.status_code == 200

    # other company can not access
    response = client_with_auth.get(f'/api/model/{model_id}', content_type='application/json', username='johndoe')
    assert response.status_code == 404

    response = client_with_auth.get('/api/companies')
    assert response.status_code == 200
    permissions = list(map(lambda i: {'company_id': i['id'], 'model_info_id': model_id, 'permission_type': 'execute'},
                           response.json))

    # allow permission to all companies
    response = client_with_auth.put(f'/api/model/permissions/{model_id}', data=json.dumps(permissions),
                                    content_type='application/json', username='admin')
    assert response.status_code == 200

    # other company can now see
    response = client_with_auth.get(f'/api/model/{model_id}', content_type='application/json', username='johndoe')
    assert response.status_code == 200
    assert response.json['can_execute']


def test_update_permissions(client_with_auth):
    response = client_with_auth.post('/api/model', data=json.dumps(create_model_info_dict()),
                                     content_type='application/json', username='admin')
    assert response.status_code == 201
    model_id = response.json['id']

    response = client_with_auth.get('/api/companies')
    assert response.status_code == 200
    permissions = list(map(lambda i: {'company_id': i['id'], 'model_info_id': model_id, 'permission_type': 'execute'},
                           response.json))

    # allow permission to all companies
    response = client_with_auth.put(f'/api/model/permissions/{model_id}', data=json.dumps(permissions),
                                    content_type='application/json', username='admin')
    assert response.status_code == 200

    response = client_with_auth.get(f'/api/model/permissions/{model_id}', content_type='application/json',
                                    username='admin')
    assert len(response.json) == len(permissions)

    # update permission to remove first company
    permissions = permissions[1:]
    response = client_with_auth.put(f'/api/model/permissions/{model_id}', data=json.dumps(permissions),
                                    content_type='application/json', username='admin')
    assert response.status_code == 200

    response = client_with_auth.get(f'/api/model/permissions/{model_id}', content_type='application/json',
                                    username='admin')
    assert len(response.json) == len(permissions)

def test_delete_model_used_in_simulation(client_with_auth):
    response = client_with_auth.post('/api/product', data=json.dumps(create_food_product_map()),
                                     content_type='application/json', username='admin')
    assert response.status_code == 201
    prod = response.json

    response = client_with_auth.post('/api/model', data=json.dumps(create_model_info_dict()),
                                     content_type='application/json', username='admin')
    assert response.status_code == 201
    model = response.json

    sim = create_simulation_dict([model['id']], prod['id'])
    response = client_with_auth.post('/api/simulation', data=json.dumps(sim), content_type='application/json',
                                     username='admin')
    assert response.status_code == 201

    response = client_with_auth.delete(f'/api/model/{model["id"]}', username='admin')
    assert response.status_code == 400