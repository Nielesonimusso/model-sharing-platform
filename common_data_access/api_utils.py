from flask import Flask
import requests
from requests import RequestException

def api_authorization_header(app: Flask) -> dict:
    api_token_endpoint = app.config['INOF_BASE'] + '/api/api_token'
    api_key = app.config['API_TOKEN']
    try:
        auth_token = requests.post(api_token_endpoint, json=dict(api_key=api_key)).json()
        return dict(authorization="Bearer "+auth_token)
    except RequestException as ex:
        print("Issue getting authorization key; ")
        return None