from enum import Enum
from typing import List
from marshmallow import fields, post_load, validate
from marshmallow.decorators import post_dump, pre_dump
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import load_only

from common_data_access.base_schema import BaseModel, DbSchema
from common_data_access.db import create_db_connection
from common_data_access.dtos import BaseDto, ModelResultDtoSchema, ModelRunStatusDtoSchema, NotEmptyString
from .association_models import model_simulation_association, data_source_simulation_association
from .base_model import BaseDbSchemaWithOwnerAndCreator, BaseModelWithOwnerAndCreator
from .model_info import ModelInfo, ModelBasicInfoReadonlyField
from .data_source_info import DataSourceInfo, DataSourceBasicInfoReadonlyField
from .user import UserBasicReadonlyInfo

_db = create_db_connection()


class SimulationBindingTypes(Enum):
    DATA_SOURCE = 'data'
    MODEL = 'model'
    FIXED = 'fixed'


class ColumnBinding(BaseModel):
    __tablename__ = 'simulation_bindings'

    argument_binding_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('argument_bindings.id'), 
        nullable=False)
    source_name = _db.Column(_db.String)
    source_uri = _db.Column(_db.String)
    source_argument_name = _db.Column(_db.String, nullable=True)
    source_argument_uri = _db.Column(_db.String, nullable=True)
    source_column_name = _db.Column(_db.String, nullable=True)
    source_column_uri = _db.Column(_db.String, nullable=True)
    source_type = _db.Column(_db.Enum(SimulationBindingTypes), nullable=False, 
        default=SimulationBindingTypes.FIXED)

    target_column_name = _db.Column(_db.String)
    target_column_uri = _db.Column(_db.String)

    class ColumnBindingDtoSchema(DbSchema):
        source_name = fields.String()
        source_uri = fields.String()
        source_argument_name = fields.String()
        source_argument_uri = fields.String()
        source_column_name = fields.String()
        source_column_uri = fields.String()
        source_type = fields.Str(required=True,
            validate=validate.OneOf([sbt.value for sbt in SimulationBindingTypes]))
        
        target_column_name = fields.String()
        target_column_uri = fields.String(required=True)

        def __init__(self, *args, **kwargs):
            super().__init__(ColumnBinding, *args, **kwargs)

        @post_load
        def _after_load(self, data, **kwargs):
            new_object = super()._after_load(data, **kwargs)
            new_object.source_type = SimulationBindingTypes(new_object.source_type)
            return new_object

        @post_dump
        def _after_dump(self, data, **kwargs):
            # turn enum type into its value
            data['source_type'] = SimulationBindingTypes[data['source_type'].split('.')[1]].value
            return data


class ArgumentBinding(BaseModel):
    __tablename__ = 'argument_bindings'

    simulation_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('simulations.id'))
    length = _db.Column(_db.Integer)
    model_name = _db.Column(_db.String)
    model_uri = _db.Column(_db.String)
    argument_uri = _db.Column(_db.String)
    argument_name = _db.Column(_db.String)
    columns = _db.relationship('ColumnBinding', cascade='delete, save-update')

    class ArgumentBindingDtoSchema(DbSchema):
        length = fields.Integer()
        model_name = fields.String()
        model_uri = fields.String()
        argument_uri = fields.String()
        argument_name = fields.String()
        columns = fields.List(fields.Nested(ColumnBinding.ColumnBindingDtoSchema))

        def __init__(self, *args, **kwargs):
            super().__init__(ArgumentBinding, *args, **kwargs)


class Simulation(BaseModelWithOwnerAndCreator):
    __tablename__ = 'simulations'

    name = _db.Column(_db.String, nullable=False)
    description = _db.Column(_db.String)
    # food_product_id = _db.Column(UUID(as_uuid=True), _db.ForeignKey('food_products.id'))
    # food_product = _db.relationship('FoodProduct')
    models = _db.relationship('ModelInfo', secondary=model_simulation_association)
    data_sources = _db.relationship('DataSourceInfo', secondary=data_source_simulation_association)
    executions = _db.relationship('ExecutedSimulation', cascade='delete, save-update')
    bindings = _db.relationship('ArgumentBinding', cascade='delete, save-update')

    class SimulationDbSchema(BaseDbSchemaWithOwnerAndCreator):
        name = fields.Str(required=True, validate=[NotEmptyString()])
        description = fields.Str()
        # food_product_id = fields.UUID(required=True, load_only=True)
        # food_product = FoodProductBasicInfoReadOnlyField
        model_ids = fields.List(fields.UUID(), required=True, load_only=True, 
            validate=[validate.Length(min=1)])
        models = fields.List(ModelBasicInfoReadonlyField, dump_only=True)
        data_source_ids = fields.List(fields.UUID(), required=True, load_only=True)
        data_sources = fields.List(DataSourceBasicInfoReadonlyField, dump_only=True)
        bindings = fields.List(fields.Nested(ArgumentBinding.ArgumentBindingDtoSchema))

        def __init__(self, *args, **kwargs):
            super().__init__(Simulation, *args, **kwargs)

        @post_load
        def _after_load(self, data: dict, **kwargs):
            model_ids = data.get('model_ids', [])
            data_source_ids = data.get('data_source_ids', [])
            del data['model_ids']
            del data['data_source_ids']
            sim = super()._after_load(data, **kwargs)
            company_id = self.context.get('company_id', None)
            # sim.food_product = FoodProduct.query.get_accessible_or_404(company_id, sim.food_product_id)
            sim.models = [ModelInfo.query.get_executable_or_404(company_id, model_id) for model_id in model_ids]
            sim.data_sources = [DataSourceInfo.query.get_data_accessible_or_404(company_id, data_source_id) for data_source_id in data_source_ids]
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
    return [ ColumnBinding.ColumnBindingDtoSchema, ArgumentBinding.ArgumentBindingDtoSchema, 
            Simulation.SimulationDbSchema, ModelResultDtoWithModelIdSchema, 
            ExecutedSimulationDtoSchema, SimulationResultsDtoSchema, 
            SimulationWithExecutionsSchema, ModelRunStatusWithModelIdDtoSchema, 
            SimulationStatusDtoSchema]
