import json
from http.client import HTTPResponse
from typing import List

from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET

from model_sharing_backend.src.graph_db.model_data_structure import QueryResultSchema, QueryResult


class SparQlRunner:
    def __init__(self, db_url=None, repo_id=None):
        if db_url is None or repo_id is None:
            from flask import current_app
            self._db_url = current_app.config['GRAPH_DB_SERVER_URL']
            self.repo_id = current_app.config['GRAPH_DB_REPOSITORY_ID']
        else:
            self._db_url = db_url
            self.repo_id = repo_id

    def read(self, q: str) -> List[QueryResult]:
        sparql_client = SPARQLWrapper(f'{self._db_url}/repositories/{self.repo_id}', returnFormat=JSON)
        sparql_client.method = GET
        sparql_client.setQuery(q)
        response: HTTPResponse = sparql_client.query().response
        result = json.load(response)
        return QueryResultSchema(many=True).load(result['results']['bindings'])

    def write(self, q: str) -> bool:
        sparql_client = SPARQLWrapper(f'{self._db_url}/repositories/{self.repo_id}/statements', returnFormat=JSON)
        sparql_client.method = POST
        sparql_client.setQuery(q)
        sparql_client.query()
        return True
