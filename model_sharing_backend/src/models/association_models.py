from sqlalchemy.dialects.postgresql import UUID

from common_data_access.db import create_db_connection

_db = create_db_connection()

model_simulation_association = _db.Table('model_simulation_association', _db.Model.metadata,
                                         _db.Column('simulations_id', UUID(as_uuid=True),
                                                    _db.ForeignKey('simulations.id')),
                                         _db.Column('model_infos_id', UUID(as_uuid=True),
                                                    _db.ForeignKey('model_infos.id')))
