import json

from faker import Faker

from model_sharing_backend.test.assert_utils import assert_dict_equal
from .dummy_data import create_food_product_map, create_model_info_dict, create_simulation_dict
from .web_client import client_with_auth

# noinspection PyStatementEffect
# importing this is necessary. this statement
# stops pyCharm from removing the import
client_with_auth
__faker = Faker()


def test_update_permissions(client_with_auth):
    response = client_with_auth.post('/api/product', data=json.dumps(create_food_product_map()),
                                     content_type='application/json', username='test1_uni')
    product_id = response.json["id"]
    assert response.status_code == 201

    response = client_with_auth.get('/api/companies')
    assert response.status_code == 200
    company_ids = list(map(lambda i: i['id'], response.json))

    # allow permission to all companies
    response = client_with_auth.put(f'/api/product/permissions/{product_id}', data=json.dumps(company_ids),
                                    content_type='application/json', username='test1_uni')
    assert response.status_code == 200
    response = client_with_auth.get(f'/api/product/permissions/{product_id}', content_type='application/json',
                                    username='test1_uni')
    assert len(response.json) == len(company_ids)

    # update permission to remove first company
    company_ids = company_ids[1:]
    response = client_with_auth.put(f'/api/product/permissions/{product_id}', data=json.dumps(company_ids),
                                    content_type='application/json', username='test1_uni')
    assert response.status_code == 200
    response = client_with_auth.get(f'/api/product/permissions/{product_id}', content_type='application/json',
                                    username='test1_uni')
    assert len(response.json) == len(company_ids)


def test_set_permission_to_food_product(client_with_auth):
    response = client_with_auth.post('/api/product', data=json.dumps(create_food_product_map()),
                                     content_type='application/json', username='test1_uni')
    product_id = response.json["id"]
    assert response.status_code == 201

    # not accessible from other organization
    response = client_with_auth.get(f'/api/product/{product_id}', content_type='application/json', username='test2_tue')
    assert response.status_code == 404

    response = client_with_auth.get('/api/companies')
    assert response.status_code == 200
    company_ids = list(map(lambda i: i['id'], response.json))

    # allow permission to all companies
    response = client_with_auth.put(f'/api/product/permissions/{product_id}', data=json.dumps(company_ids),
                                    content_type='application/json', username='test1_uni')
    assert response.status_code == 200

    # product accessible from other company
    response = client_with_auth.get(f'/api/product/{product_id}', content_type='application/json', username='test2_tue')
    assert response.status_code == 200

    response = client_with_auth.get(f'/api/product/permissions/{product_id}', content_type='application/json',
                                    username='test1_uni')
    assert response.status_code == 200
    assert len(response.json) == len(company_ids)

    # permissions not visible to other companies
    response = client_with_auth.get(f'/api/product/permissions/{product_id}', content_type='application/json',
                                    username='test2_tue')
    assert response.status_code == 404


def test_create_and_get_accessible_product(client_with_auth):
    product_count = 5
    for _ in range(product_count):
        # test2_tue and test3_tue are from the same organization
        res = client_with_auth.post('/api/product', data=json.dumps(create_food_product_map()),
                                    content_type='application/json', username='test3_tue')
        assert res.status_code == 201
        res = client_with_auth.post('/api/product', data=json.dumps(create_food_product_map()),
                                    content_type='application/json', username='test2_tue')
        assert res.status_code == 201

    response = client_with_auth.get('/api/products', username='test3_tue')
    assert response.status_code == 200
    assert response.is_json
    assert len(response.json) == product_count * 2


def test_create_and_get_owned_product(client_with_auth):
    product_count = 5
    for _ in range(product_count):
        res = client_with_auth.post('/api/product', data=json.dumps(create_food_product_map()),
                                    content_type='application/json', username='test1_uni')
        assert res.status_code == 201
        res = client_with_auth.post('/api/product', data=json.dumps(create_food_product_map()),
                                    content_type='application/json', username='test2_tue')
        assert res.status_code == 201

    response = client_with_auth.get('/api/own_products')
    assert response.status_code == 200
    assert response.is_json
    assert len(response.json) == product_count


def test_create_and_get_one_food_product(client_with_auth):
    product_new = create_food_product_map()
    response = client_with_auth.post('/api/product', data=json.dumps(product_new), content_type='application/json')
    assert response.status_code == 201
    response = client_with_auth.get(f'/api/product/{response.json["id"]}')
    assert response.status_code == 200
    assert response.is_json
    assert_dict_equal(product_new, response.json, ['id'])


def test_create_and_update_one_food_product(client_with_auth):
    product = create_food_product_map()
    response = client_with_auth.post('/api/product', data=json.dumps(product), content_type='application/json',
                                     username='test2_tue')
    assert response.status_code == 201
    response = client_with_auth.get(f'/api/product/{response.json["id"]}', username='test2_tue')
    assert response.status_code == 200

    # change all properties
    product_saved = create_food_product_map()
    product_saved['id'] = response.json['id']

    response = client_with_auth.put(f'/api/product/{product_saved["id"]}', data=json.dumps(product_saved),
                                    content_type='application/json', username='test2_tue')
    assert response.status_code == 200

    response = client_with_auth.get(f'/api/product/{product_saved["id"]}', username='test2_tue')
    assert response.status_code == 200
    assert response.is_json
    assert_dict_equal(product_saved, response.json, [])

    # update should return 404 for different user
    response = client_with_auth.put(f'/api/product/{product_saved["id"]}', data=json.dumps(product_saved),
                                    content_type='application/json', username='test3_tue')
    assert response.status_code == 404


def test_create_and_get_all_food_products(client_with_auth):
    count = 5
    for _ in range(count):
        response = client_with_auth.post('/api/product', data=json.dumps(create_food_product_map()),
                                         content_type='application/json')
        assert response.status_code == 201
    response = client_with_auth.get('/api/products')
    assert response.status_code == 200
    assert response.is_json
    assert len(response.json) == count


def test_create_and_delete_food_products(client_with_auth):
    response = client_with_auth.post('/api/product', data=json.dumps(create_food_product_map()),
                                     content_type='application/json', username='test1_uni')
    assert response.status_code == 201
    response = client_with_auth.delete(f'/api/product/{response.json["id"]}', username='test1_uni')
    assert response.status_code == 200
    assert response.is_json

    # delete not owned food product
    response = client_with_auth.post('/api/product', data=json.dumps(create_food_product_map()),
                                     content_type='application/json', username='test1_uni')
    assert response.status_code == 201
    response = client_with_auth.delete(f'/api/product/{response.json["id"]}', username='test2_tue')
    assert response.status_code == 404


def test_delete_food_product_used_in_simulation(client_with_auth):
    response = client_with_auth.post('/api/product', data=json.dumps(create_food_product_map()),
                                     content_type='application/json', username='test1_uni')
    assert response.status_code == 201
    prod = response.json

    response = client_with_auth.post('/api/model', data=json.dumps(create_model_info_dict()),
                                     content_type='application/json', username='test1_uni')
    assert response.status_code == 201
    model = response.json

    sim = create_simulation_dict([model['id']], prod['id'])
    response = client_with_auth.post('/api/simulation', data=json.dumps(sim), content_type='application/json',
                                     username='test1_uni')
    assert response.status_code == 201

    response = client_with_auth.delete(f'/api/product/{prod["id"]}', username='test1_uni')
    assert response.status_code == 400


def test_get_all_ingredients(client_with_auth):
    response = client_with_auth.get('/api/product/ingredients')
    assert response.status_code == 200
    assert response.is_json
    assert type(response.json) == list
