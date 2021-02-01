import time

import pytest

from model_sharing_backend.src.graph_db.queries import query_model
from model_sharing_backend.src.graph_db.queries.query_runner import SparQlRunner
from model_sharing_backend.src.graph_db.seed.seed import seed_graph_db_with_inof_ontology


@pytest.fixture
def sparql_client():
    server_url = 'http://localhost:7200'
    repo_id = 'INoF_TEST'
    seed_graph_db_with_inof_ontology(server_url, repo_id)
    time.sleep(2) # time delay for the graph db to complete seeding
    return SparQlRunner(server_url, repo_id)


def test_get_model_by_uri(sparql_client):
    soup_model_uri = 'http://www.foodvoc.org/resource/InternetOfFoodModel/tomatoSoupModel'
    model = query_model.get_model(soup_model_uri, sparql_client)
    assert len(model.inputs) == 6
    assert len(model.outputs) == 4
    assert model.uri == soup_model_uri


def test_get_all_models_from_graph_db(sparql_client):
    models = query_model.get_all_models(sparql_client)
    assert isinstance(models, list)
    assert len(models) > 0
