from unit_translation_component import Values, Unit, floatequal

# 20 degree Réaumur to degree Rankine and back to 20 Réaumur
def test_reliability_1():
    NEW_MODEL = Values(20, Unit('degree Réaumur'))
    TARGET_UNIT = 'degree Rankine'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    NEW_RESULT = Values(RES, Unit(TARGET_UNIT)).to_unit(Unit('degree Réaumur'))
    assert(floatequal(NEW_RESULT, 20))
    
# 34.25 degree Fahrenheit to degree Réaumur and back to 34.25 Fahrenheit
def test_reliability_2():
    NEW_MODEL = Values(34.25, Unit('degree Fahrenheit'))
    TARGET_UNIT = 'degree Réaumur'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    NEW_RESULT = Values(RES, Unit(TARGET_UNIT)).to_unit(Unit('degree Fahrenheit'))
    assert(floatequal(NEW_RESULT, 34.25))
    
# PERCENTAGE DIMENSION
# 80% of 10 stere to barrel (US) = 8 stere to barrel and back to 8 stere
def test_reliability_3():
    NEW_MODEL = Values(10, Unit('stere'), 80.0)
    TARGET_UNIT = 'barrel (US)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    NEW_RESULT = Values(RES, Unit(TARGET_UNIT)).to_unit(Unit('stere'))
    assert(floatequal(NEW_RESULT, 8.0))