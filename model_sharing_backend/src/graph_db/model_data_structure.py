from dataclasses import dataclass
from enum import Enum
from typing import List

from marshmallow import Schema, fields, validate, post_load

from common_data_access import string_utils


class TypeEnum(Enum):
    LITERAL = 'literal'
    URI = 'uri'


@dataclass
class TypeValuePair:
    type: TypeEnum
    value: str
    language: str = None


@dataclass
class QueryResult:
    item: TypeValuePair
    property: TypeValuePair
    value: TypeValuePair


class DataclassSchema(Schema):

    def __init__(self, data_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unknown = 'EXCLUDE'
        self._data_type = data_type

    @post_load
    def _after_load(self, data, **kwargs):
        return self._data_type(**data)


class TypeValuePairSchema(DataclassSchema):
    type = fields.Str(validate=validate.OneOf([a.value for a in TypeEnum]), required=True)
    value = fields.Str(required=True)
    language = fields.Str(data_key='xml:lang')

    def __init__(self, *args, **kwargs):
        super().__init__(TypeValuePair, *args, **kwargs)


class QueryResultSchema(DataclassSchema):
    item = fields.Nested(TypeValuePairSchema, required=True)
    property = fields.Nested(TypeValuePairSchema, required=True)
    value = fields.Nested(TypeValuePairSchema, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(QueryResult, *args, **kwargs)


@dataclass
class Label:
    name: str
    language: str


class ModelParameterLabelSchema(DataclassSchema):
    name = fields.Str(required=True)
    language = fields.Str(missing='en', validate=validate.OneOf(['en', 'nl']))

    def __init__(self, *args, **kwargs):
        super().__init__(Label, *args, **kwargs)


@dataclass
class Unit:
    uri: str
    label: Label


class ModelParamUnitSchema(DataclassSchema):
    uri = fields.Str(required=True)
    label = fields.Nested(ModelParameterLabelSchema, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(Label, *args, **kwargs)


@dataclass
class GraphDbModelParameter:
    labels: List[Label]
    description: str
    unit: Unit


class ModelParameterSchema(DataclassSchema):
    labels = fields.List(fields.Nested(ModelParameterLabelSchema, required=True), validate=validate.Length(min=1))
    description = fields.Str(required=True)
    unit = fields.Method(serialize='get_unit_dict', deserialize='get_unit', required=True)

    def get_unit_dict(self, obj) -> str:
        return obj.unit.label.name

    def get_unit(self, unit_name) -> Unit:
        # todo query om here
        return Unit(label=Label(unit_name, 'en'),
                    uri=f'http://www.ontology-of-units-of-measure.org/resource/om-2/' +
                        string_utils.to_camel_case(unit_name))

    def __init__(self, *args, **kwargs):
        super().__init__(GraphDbModelParameter, *args, **kwargs)


@dataclass
class GraphDbModel:
    name: str
    inputs: List[GraphDbModelParameter]
    outputs: List[GraphDbModelParameter]
    uri: str = None


class GraphDbModelSchema(DataclassSchema):
    uri = fields.Url(dump_only=True)
    name = fields.Str(required=True)
    inputs = fields.List(fields.Nested(ModelParameterSchema), data_key='input_descriptions',
                         validate=[validate.Length(min=1)], required=True)
    outputs = fields.List(fields.Nested(ModelParameterSchema), data_key='output_descriptions',
                          validate=[validate.Length(min=1)], required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(GraphDbModel, *args, **kwargs)


def get_dto_schemas():
    return [ModelParameterSchema, GraphDbModelSchema, ModelParameterLabelSchema]
