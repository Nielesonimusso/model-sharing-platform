
from enum import Enum

from marshmallow import Schema, fields, post_load, validate, ValidationError
from marshmallow.validate import Validator


class BaseDto(Schema):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unknown = 'EXCLUDE'

    @post_load
    def __create_object(self, data, **kwargs):
        class_name = f'{type(self).__name__}_generated'
        return type(class_name, (object,), data)

    def __repr__(self):
        return f'<{type(self).__name__}>'


class IngredientPropertyInfoDtoSchema(BaseDto):
    name = fields.Str()
    value = fields.Number()
    unit = fields.Str()


class IngredientInfoDtoSchema(BaseDto):
    company_code = fields.Str()
    standard_code = fields.Str()
    name = fields.Str()


class IngredientInfoWithPropertyInfosDtoSchema(IngredientInfoDtoSchema):
    ingredient_properties = fields.List(fields.Nested(IngredientPropertyInfoDtoSchema))


class ModelRunStatus(Enum):
    SUBMITTED = 'submitted'
    SUCCESS = 'success'
    RUNNING = 'running'
    FAILED = 'failed'
    UNREACHABLE = 'unreachable'


class RunModelDtoSchema(BaseDto):
    simulation_id = fields.Str()
    # created_on = fields.DateTime()
    # created_by = fields.Str()


class ModelRunStatusDtoSchema(BaseDto):
    run_id = fields.Str()
    created_on = fields.DateTime()
    status = fields.Str(validate=validate.OneOf([a.value for a in ModelRunStatus]))


class ModelResultDtoSchema(BaseDto):
    model_name = fields.Str()
    created_on = fields.DateTime()
    ran_on = fields.DateTime()
    status = fields.Str(validate=validate.OneOf([a.value for a in ModelRunStatus]))
    result = fields.List(fields.Dict())


class GatewayPaths:
    model_run = 'api/run_model'
    model_status = 'api/get_model_run_state'
    model_result = 'api/get_result'


class NotEmptyString(Validator):

    def __init__(self):
        super().__init__()
        self._default_error_msg = 'string can not be empty'

    def __call__(self, value):
        if not isinstance(value, str):
            raise ValidationError('value is not a string')

        if value is None or len(value) < 1:
            raise ValidationError(self._default_error_msg)

        return value
