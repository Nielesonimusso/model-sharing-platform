from unit_translation_component import Unit
from unit_translation_component.exception import UnitNotFoundException

def test_unit_non_existent_exception_1():
    try:
        Unit('gallitre')
    except Exception as e:
        assert isinstance(e, UnitNotFoundException)

def test_unit_non_existent_exception_2():
    try:
        Unit('lambda')
    except Exception as e:
        assert isinstance(e, UnitNotFoundException)

def test_unit_non_existent_exception_3():
    try:
        Unit('alpha')
    except Exception as e:
        assert isinstance(e, UnitNotFoundException)

def test_unit_non_existent_exception_4():
    try:
        Unit('beta')
    except Exception as e:
        assert isinstance(e, UnitNotFoundException)
