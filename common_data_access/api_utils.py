from flask import Flask
import requests
from requests import RequestException
import random, time

def api_authorization_header(app: Flask) -> dict:
    api_token_endpoint = app.config['INOF_BASE'] + '/api/api_token'
    api_key = app.config['API_TOKEN']
    random.seed() # seeding for random back-off times
    for i in range(0, 5):
        try:
            auth_token = requests.post(api_token_endpoint, json=dict(api_key=api_key)).json()
            return dict(authorization="Bearer "+auth_token)
        except RequestException as ex:
            backoff_time = random.uniform(3, 6)
            print(i, "Issue getting authorization key; waiting ", 
                backoff_time, ex)
            time.sleep(backoff_time)
            continue
    print('no authorization key acquired; ')
    return None