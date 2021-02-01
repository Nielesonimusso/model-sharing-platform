from unit_translation_component import Values, Unit, floatequal
from unit_translation_component.exception import UnitNotFoundException, ParameterMismatchException, UnitsNotComparableException

def test_parameter_mismatch_exception():
    try:
        Unit('gram').can_convert_to('litre')
    except Exception as e:
        assert isinstance(e, ParameterMismatchException)

def test_unit_not_found_exception():
    try:
        Unit('not a unit')
    except Exception as e:
        assert isinstance(e, UnitNotFoundException)

def test_units_not_comparable_exception():
    try:
        Unit('gram').can_convert_to(Unit('litre'))
    except Exception as e:
        assert isinstance(e, UnitsNotComparableException)
