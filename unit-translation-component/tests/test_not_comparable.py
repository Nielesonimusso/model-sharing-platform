from unit_translation_component import Values, Unit
from unit_translation_component.exception import UnitsNotComparableException

def test_units_not_comparable_exception_1():
    try:
        Unit('gram').can_convert_to(Unit('litre'))
    except Exception as e:
        assert isinstance(e, UnitsNotComparableException)

def test_units_not_comparable_exception_2():
    try:
        Unit('attogray').can_convert_to(Unit('attohertz'))
    except Exception as e:
        assert isinstance(e, UnitsNotComparableException)

def test_units_not_comparable_exception_3():
    try:
        Unit('degree Celsius per hour').can_convert_to(Unit('degree Celsius day'))
    except Exception as e:
        assert isinstance(e, UnitsNotComparableException)

def test_units_not_comparable_exception_4():
    try:
        Unit('newton per square metre').can_convert_to(Unit('newton per metre'))
    except Exception as e:
        assert isinstance(e, UnitsNotComparableException)
