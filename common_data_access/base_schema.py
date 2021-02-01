import uuid
from typing import Type, TypeVar, Generic

from marshmallow import Schema, post_load, fields, EXCLUDE
from sqlalchemy.dialects.postgresql import UUID

from .db import create_db_connection

_db = create_db_connection()

S = TypeVar('S', bound=Schema)


class BaseModel(_db.Model):
    __abstract__ = True

    id = _db.Column(UUID(as_uuid=True), primary_key=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = kwargs.get('id', None) or uuid.uuid4()

    def add(self):
        _db.session.add(self)
        _db.session.commit()
        return self

    def save(self):
        if self.exists():
            self.update()
        else:
            self.add()
        return self

    def exists(self):
        return _db.session.query(self.query.filter_by(id=self.id).exists()).scalar()

    def update(self):
        # model already has updated values just commit it.
        # todo: may not work when loading from schema
        _db.session.commit()
        return self

    def delete(self):
        _db.session.delete(self)
        _db.session.commit()

    def __repr__(self):
        return f'<{type(self).__name__} id: {self.id}>'


M = TypeVar('M', bound=BaseModel)


class DbSchema(Schema, Generic[M]):
    id = fields.UUID(dump_only=True)

    def __init__(self, type: Type[M], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__type = type
        self.unknown = EXCLUDE
        self.partial = False

    @post_load
    def _after_load(self, data, **kwargs):
        return self.__type(**data)

    def __repr__(self):
        return f'<{type(self).__name__} id: {self.id}>'
