import json
import os
from datetime import datetime
from tempfile import TemporaryFile

import requests


def seed_graph_db_with_inof_ontology(server_url: str, repository_id: str):
    __remove_existing_repository(server_url, repository_id)
    __create_new_repository(server_url, repository_id)
    __upload_ontology(server_url, repository_id)


def __remove_existing_repository(server_url: str, repository_id: str):
    del_endpoint = '/'.join([server_url.rstrip("/"), 'rest', 'repositories', repository_id])
    response = requests.delete(del_endpoint)
    if not (response.status_code == 204 or response.status_code == 200):
        raise IOError(f'can not remove repository {repository_id}')


def __create_new_repository(server_url: str, repository_id: str, description: str = ''):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'repo_config_template.ttl')) as config_template:
        repo_config = config_template.read()

    repo_config = repo_config.replace('<repository_name>', repository_id, 1)
    repo_config = repo_config.replace('<repository_description>', description, 1)

    with TemporaryFile('r+') as config_file:
        config_file.write(repo_config)
        config_file.seek(0)
        create_endpoint = '/'.join([server_url.rstrip("/"), 'rest', 'repositories'])
        response = requests.post(create_endpoint, files={'config': config_file})
        print(response.text)
        if not response.status_code == 201:
            raise IOError(f'unable to create repository {repository_id}')


def __upload_ontology(server_url: str, repository_id: str):
    ontology_file_name = 'InternetOfFoodModel.ttl'

    # upload file to server
    data = dict(name=ontology_file_name, status="NONE", message="", context=None, replaceGraphs=[],
                baseURI=None, forceSerial=False, type=None, format=None, data=None,
                timestamp=datetime.timestamp(datetime.now()),
                parserSettings={"preserveBNodeIds": False, "failOnUnknownDataTypes": False,
                                "verifyDataTypeValues": False, "normalizeDataTypeValues": False,
                                "failOnUnknownLanguageTags": False, "verifyLanguageTags": True,
                                "normalizeLanguageTags": False, "stopOnError": True}, xRequestIdHeaders=None)
    file_upload_endpoint = '/'.join(
        [server_url.rstrip("/"), 'rest', 'data', 'import', 'upload', repository_id, 'update', 'file'])
    with TemporaryFile('r+') as config_file:
        config_file.write(json.dumps(data))
        config_file.seek(0)
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ontology_file_name), 'rb') as inof_ontology:
            response = requests.post(file_upload_endpoint, files={
                'file': (ontology_file_name, inof_ontology, 'text/turtle'),
                'importSettings': ('blob', config_file, 'application/json')})
            print(f'{response.text} {response.status_code}')

    # get server file
    file_list_endpoint = '/'.join([server_url.rstrip("/"), 'rest', 'data', 'import', 'upload', repository_id])
    response = requests.get(file_list_endpoint)
    files = response.json()
    ontology_file_entry = next(filter(lambda f: f['name'] == ontology_file_name, files))

    # import uploaded ontology
    file_import_endpoint = '/'.join([server_url.rstrip("/"), 'rest', 'data', 'import', 'upload', repository_id, 'file'])
    with TemporaryFile('r+') as config_file:
        config_file.write(json.dumps(ontology_file_entry))
        config_file.seek(0)
        response = requests.post(file_import_endpoint,
                                 files={'importSettings': ('blob', config_file, 'application/json')})
        print(f'{response.text} {response.status_code}')
