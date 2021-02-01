import json

from model_sharing_backend.test.assert_utils import assert_dict_equal
from .dummy_data import create_registration_dict, create_login_dict
from .web_client import client, client_with_auth

# noinspection PyStatementEffect
# importing this is necessary. this statement
# stops pyCharm from removing the import
client, client_with_auth


def test_user_registration_and_login(client):
    user_reg = create_registration_dict(client.get('/api/companies').json[0]['id'])
    response = client.post('/api/user/register', data=json.dumps(user_reg), content_type='application/json')
    assert response.status_code == 200

    user_login = create_login_dict(user_reg['username'], user_reg['password'])
    response = client.post('/api/auth_token', data=json.dumps(user_login), content_type='application/json')
    assert response.status_code == 200

    response = client.get('/api/own_profile', content_type='application/json',
                          headers={'Authorization': f'Bearer {response.json}'})
    assert response.status_code == 200
    assert_dict_equal(user_reg, response.json, ['password'])


def test_check_authorization(client):
    user_reg = create_registration_dict(client.get('/api/companies').json[0]['id'])
    response = client.post('/api/user/register', data=json.dumps(user_reg), content_type='application/json')
    assert response.status_code == 200

    user_login = create_login_dict(user_reg['username'], user_reg['password'])
    response = client.post('/api/auth_token', data=json.dumps(user_login), content_type='application/json')
    token = response.json
    assert response.status_code == 200
    assert token is not None
    response = client.get('/api/check_auth', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200

    response = client.get('/api/check_auth', headers={'Authorization': f'Bearer invalid_token'})
    assert response.status_code == 401

    response = client.get('/api/check_auth')
    assert response.status_code == 401


def test_login_wrong_credential(client):
    user_reg = create_registration_dict(client.get('/api/companies').json[0]['id'])
    response = client.post('/api/user/register', data=json.dumps(user_reg), content_type='application/json')
    assert response.status_code == 200

    user_login = create_login_dict(user_reg['username'])
    response = client.post('/api/auth_token', data=json.dumps(user_login), content_type='application/json')
    assert response.status_code == 401

    response = client.post('/api/auth_token', data=json.dumps(create_login_dict()), content_type='application/json')
    assert response.status_code == 401
