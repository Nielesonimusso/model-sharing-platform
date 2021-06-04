from enum import Enum
from typing import List
from marshmallow import fields, post_load, validate
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import load_only

from common_data_access.base_schema import BaseModel
from common_data_access.db import create_db_connection
from common_data_access.dtos import BaseDto, ModelResultDtoSchema, ModelRunStatusDtoSchema, NotEmptyString
from .association_models import model_simulation_association, data_source_simulation_association
from .base_model import BaseDbSchemaWithOwnerAndCreator, BaseModelWithOwnerAndCreator
from .food_product_models import FoodProduct, FoodProductBasicInfoReadOnlyField
from .model_info import ModelInfo, ModelBasicInfoReadonlyField
from .data_source_info import DataSourceInfo, DataSourceBasicInfoReadonlyField
from .user import UserBasicReadonlyInfo

_db = create_db_connection()


class SimulationBindingTypes(Enum):
    DATA_SOURCE = 'data'
    MODEL = 'model'
    FIXED = 'fixed'


class SimulationBinding(BaseModel):
    __tablename__ = 'simulation_bindings'

    model_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('simulations.id'), 
        nullable=False)
    source = _db.Column(_db.String)
    source_type = _db.Column(_db.Enum(SimulationBindingTypes), nullable=False, 
        default=SimulationBindingTypes.FIXED)
    target = _db.Column(_db.String)

    class SimulationBindingDtoSchema(BaseDto):
        source = fields.String()
        source_type = fields.Str(required=True,
            validate=validate.OneOf([sbt.value for sbt in SimulationBindingTypes]))
        target = fields.String()

class Simulation(BaseModelWithOwnerAndCreator):
    __tablename__ = 'simulations'

    name = _db.Column(_db.String, nullable=False)
    description = _db.Column(_db.String)
    # food_product_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('food_products.id'))
    # food_product = _db.relationship('FoodProduct')
    models = _db.relationship('ModelInfo', secondary=model_simulation_association)
    datasources = _db.relationship('DataSourceInfo', secondary=data_source_simulation_association)
    executions = _db.relationship('ExecutedSimulation', cascade='delete, save-update')
    bindings = _db.relationship('SimulationBinding', cascade='delete, save-update')

    class SimulationDbSchema(BaseDbSchemaWithOwnerAndCreator):
        name = fields.Str(required=True, validate=[NotEmptyString()])
        description = fields.Str()
        # food_product_id = fields.UUID(required=True, load_only=True)
        # food_product = FoodProductBasicInfoReadOnlyField
        model_ids = fields.List(fields.UUID(), required=True, load_only=True, 
            validate=[validate.Length(min=1)])
        models = fields.List(ModelBasicInfoReadonlyField, dump_only=True)
        datasource_ids = fields.List(fields.UUID(), required=True, load_only=True,
            validate=[validate.Length(min=1)])
        datasources = fields.List(DataSourceBasicInfoReadonlyField, dump_only=True)
        bindings = fields.List(fields.Nested(SimulationBinding.SimulationBindingDtoSchema, 
            validate=validate.Predicate(method='validate_bindings', 
                error='No duplicate bindings for sources allowed')))

        def validate_bindings(bindings: List[dict]) -> bool:
            sources = set()
            return not any (b['source'] in sources or sources.add(b['source']) for b in bindings)

        def __init__(self, *args, **kwargs):
            super().__init__(Simulation, *args, **kwargs)

        @post_load
        def _after_load(self, data: dict, **kwargs):
            model_ids = data.get('model_ids', [])
            data_source_ids = data.get('datasource_ids', [])
            del data['model_ids']
            sim = super()._after_load(data, **kwargs)
            company_id = self.context.get('company_id', None)
            # sim.food_product = FoodProduct.query.get_accessible_or_404(company_id, sim.food_product_id)
            sim.models = [ModelInfo.query.get_executable_or_404(company_id, model_id) for model_id in model_ids]
            sim.datasources = [DataSourceInfo.query.get_executable_or_404(company_id, data_source_id) for data_source_id in data_source_ids]
            return sim


class ExecutedModel(BaseModel):
    __tablename__ = 'executed_models'

    client_run_id = _db.Column(_db.String)
    error_message = _db.Column(_db.String)
    created_on = _db.Column(_db.DateTime)
    model_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('model_infos.id'), nullable=False)
    model = _db.relationship('ModelInfo', uselist=False)
    executed_simulation_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('executed_simulations.id'))


class ExecutedSimulation(BaseModelWithOwnerAndCreator):
    __tablename__ = 'executed_simulations'

    simulation_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('simulations.id'), nullable=False)
    simulation = _db.relationship('Simulation', uselist=False)
    executed_models = _db.relationship('ExecutedModel', cascade='delete, save-update')


SimulationBasicInfoReadonlyField = fields.Nested(Simulation.SimulationDbSchema, only=('id', 'name', 'owner'),
                                                 dump_only=True)


class ExecutedModelDtoSchema(BaseDto):
    id = fields.UUID(data_key='model_execution_id')
    client_run_id = fields.Str()
    model = ModelBasicInfoReadonlyField


class ModelResultDtoWithModelIdSchema(ModelResultDtoSchema):
    model_id = fields.UUID()


class ModelRunStatusWithModelIdDtoSchema(ModelRunStatusDtoSchema):
    model_id = fields.UUID()


class ExecutedSimulationDtoSchema(BaseDto):
    id = fields.UUID(data_key='simulation_execution_id')
    created_by = UserBasicReadonlyInfo
    created_on = fields.DateTime()
    simulation = SimulationBasicInfoReadonlyField
    executed_models = fields.List(fields.Nested(ExecutedModelDtoSchema))


class SimulationStatusDtoSchema(ExecutedSimulationDtoSchema):
    model_statuses = fields.List(fields.Nested(ModelRunStatusWithModelIdDtoSchema, exclude=['run_id']))


class SimulationWithExecutionsSchema(Simulation.SimulationDbSchema):
    executions = fields.List(fields.Nested(ExecutedSimulationDtoSchema, dump_only=True))


class SimulationResultsDtoSchema(ExecutedSimulationDtoSchema):
    results = fields.List(fields.Nested(ModelResultDtoWithModelIdSchema))


def get_schemas() -> list:
    return [ SimulationBinding.SimulationBindingDtoSchema, Simulation.SimulationDbSchema, 
            ModelResultDtoWithModelIdSchema, ExecutedSimulationDtoSchema,
            SimulationResultsDtoSchema, SimulationWithExecutionsSchema,
            ModelRunStatusWithModelIdDtoSchema, SimulationStatusDtoSchema]
