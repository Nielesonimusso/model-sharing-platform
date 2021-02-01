from __future__ import annotations
from unit_translation_component.unit import Unit
from unit_translation_component.redis_instance import RedisObject
from unit_translation_component.exception import PercentConversionException


class Values:
    # each object of type Values has a numerical attribute "quantity" (i.e 1000)
    # and a categorical attribute "unity" (i.e gram)

    # function __init__ initializes the newly created object with preset
    # values for quantity and unity

    def __init__(self, q: float, u: Unit, p: float = 100.0):
        self.quantity = q
        self.unit = u
        self.percentage = p

    # Get cached factors or calculate if redis not available
    def __get_units_factors(self, param: Unit):
        if RedisObject.available():
            factors = []
            redis_instance = RedisObject.get_instance()
            for target in [self.unit, param]:
                if redis_instance.hexists(target.URIRef, 'factor_si'):
                    factor = float(redis_instance.hget(
                        target.URIRef, 'factor_si'))
                    factors.append(factor)
                else:
                    factor = target.get_factor_si()
                    factors.append(factor)
                    redis_instance.hmset(target.URIRef, {'factor_si': factor})
            return (factors[0], factors[1])
        else:
            return (self.unit.get_factor_si(), param.get_factor_si())

    def to_unit(self, param: Unit, whole: Values = None):
        if param == Unit('%', symbol=True):
            if whole is None:
                raise PercentConversionException('Converting to percent (%) requires a whole value')
            value_in_whole_unit = self.to_unit(whole.unit)
            return (value_in_whole_unit * 100) / whole.quantity

        self.unit.can_convert_to(param)
        # Handle non-temperatures units
        if not (self.unit.f_temperature or param.f_temperature):
            (f1, f2) = self.__get_units_factors(param)
            return (self.quantity * f1 / f2) * (self.percentage / 100.0)
        else:
            # Handle temperatures
            return param.from_kelvin(self.unit.to_kelvin(self.quantity)) * (self.percentage / 100.0)

    def __repr__(self):
        return f'<{type(self).__name__} quantity: {self.quantity}, unit: {self.unit}, percentage: {self.percentage}>'
