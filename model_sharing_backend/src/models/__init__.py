from typing import List

from flask import Flask

from common_data_access.db import create_db_connection
from model_sharing_backend.src.models.query_classes.permission_query_class import PermissionFilteredQuery


def initialize_db_connections(app: Flask):
    create_db_connection(app, PermissionFilteredQuery)


def get_schema_classes() -> List:
    from .food_product_models import get_schemas as product_schemas
    from .model_info import get_schemas as model_schemas
    from .simulation import get_schemas as simulation_schemas
    from .user import get_schemas as user_schemas
    from .data_source_info import get_schemas as data_source_schemas
    from common_data_access.dtos import IngredientInfoDtoSchema, ModelResultDtoSchema, RunModelDtoSchema, \
        ModelRunStatusDtoSchema
    return [*product_schemas(), *model_schemas(), *data_source_schemas(), *simulation_schemas(), *user_schemas(), 
            IngredientInfoDtoSchema, ModelResultDtoSchema, RunModelDtoSchema, ModelRunStatusDtoSchema]


