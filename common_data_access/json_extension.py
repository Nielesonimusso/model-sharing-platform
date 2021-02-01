from typing import List, Union, Type, TypeVar

from flask import jsonify
from marshmallow import Schema

T = TypeVar('T', bound=Schema)


def get_json(data: Union[List[any], any], schema_type: Type[T], context: dict = None) -> Union[List[any], any]:
    schema = schema_type(many=isinstance(data, list), context = context)
    return jsonify(schema.dump(data))
