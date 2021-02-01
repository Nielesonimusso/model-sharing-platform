from common_data_access.base_schema import BaseModel
from common_data_access.db import create_db_connection
from common_data_access.db_initialize import BaseDbInitialize
from common_data_access.dtos import ModelRunStatus

_db = create_db_connection()


class GatewayDbInitialize(BaseDbInitialize):

    def _seed_database(self, **kwargs):
        pass


class SimulationRun(BaseModel):
    __tablename__ = 'simulation_runs'

    parameters = _db.Column(_db.PickleType, nullable=False)
    result = _db.Column(_db.PickleType)
    submitted_on = _db.Column(_db.DateTime, nullable=False)
    submitted_by = _db.Column(_db.String, nullable=False)
    completed_on = _db.Column(_db.DateTime)
    status = _db.Column(_db.Enum(ModelRunStatus))
