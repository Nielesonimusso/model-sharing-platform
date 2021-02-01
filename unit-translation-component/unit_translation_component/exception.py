from unit_translation_component import constant as ct


class GenericException(Exception):
    """Generic exception for unit conversion"""

    def __init__(self, msg: str = 'Undefined exception.', error: int = 100):
        super().__init__()
        self.message = msg
        self.error = error

    def __str__(self):
        return 'Error {0}: {1}'.format(self.error, self.message)


class UnitNotFoundException(GenericException):
    """Exception to indicate the provided unit was not found"""

    def __init__(self, label, error: int = 101):
        msg = 'The input unit "' + label + \
            '" could not be found in the OM2 web resource. Please make sure to enter a valid unit of measure.'
        super().__init__(msg, error)

    def __str__(self):
        return super().__str__()


class UnitsNotComparableException(GenericException):
    """Exception to indicate the provided units do not have the same measure"""

    def __init__(self, label_initial, dim_initial, label_target, dim_target, error: int = 102):
        msg = 'The units are not comparable, because unit "' + label_initial + '" measures ' + \
            ct.trim_uri(dim_initial)[
                0] + ' while unit "' + label_target + '" measures ' + ct.trim_uri(dim_target)[0]
        super().__init__(msg, error)

    def __str__(self):
        return super().__str__()


class ParameterMismatchException(GenericException):
    """Exception to indicate the unit could not be parsed"""

    def __init__(self, param, error: int = 103):
        msg = 'The requested target unit of measure : "' + param + \
            '" does not match the expected input format. Please specify the unit of measure as a string'
        super().__init__(msg, error)

    def __str__(self):
        return super().__str__()


class PercentConversionException(GenericException):
    def __init__(self, msg):
        super().__init__(msg, 104)

    def __str__(self):
        return super().__str__()
