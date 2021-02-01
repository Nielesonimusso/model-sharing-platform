from unit_translation_component import Values, Unit, floatequal

# TERMODINAMIC TEMPERATURE
# 1 degree Celsius to decidegree Celsius
def test_temperatures_1():
    NEW_MODEL = Values(1, Unit('degree Celsius'))
    TARGET_UNIT = 'decidegree Celsius'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.1))

# 20 degree Réaumur to degree Rankine
def test_temperatures_2():
    NEW_MODEL = Values(20, Unit('degree Réaumur'))
    TARGET_UNIT = 'degree Rankine'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 536.6699570664035))

# 1 gram to milligram
def test_temperatures_3():
    NEW_MODEL = Values(460.67, Unit('degree Rankine'))
    TARGET_UNIT = 'degree Fahrenheit'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1))

# 10 degree Celsius to degree Fahrenheit
def test_temperatures_4():
    NEW_MODEL = Values(10, Unit('degree Celsius'))
    TARGET_UNIT = 'degree Fahrenheit'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 49.99995922640318))

# 70 degree Fahrenheit to degree Celsius
def test_temperatures_5():
    NEW_MODEL = Values(70, Unit('degree Fahrenheit'))
    TARGET_UNIT = 'degree Celsius'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 21.11113465200009))

# 34.25 degree Fahrenheit to degree Réaumur
def test_temperatures_6():
    NEW_MODEL = Values(34.25, Unit('degree Fahrenheit'))
    TARGET_UNIT = 'degree Réaumur'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.000017561600032))

# def test_temperatures_5():  TODO fix
#    NEW_MODEL = Values(34.25, Unit('femtodegree Celsius'))
#    TARGET_UNIT = 'degree Rankine'
#    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
#    assert(floatequal(RES, 5.533199557344035e-13))

# PERCENTAGE DIMENSION
# 80% of 10 stere to barrel (US)
def test_converstion_p1():
    NEW_MODEL = Values(10, Unit('stere'), 80.0)
    TARGET_UNIT = 'barrel (US)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 50.318484558200566))

# 10% of 10 degree Rankine to centidegree Celsius
def test_temperatures_p2():
    NEW_MODEL = Values(10, Unit('degree Rankine'), 10.0)
    TARGET_UNIT = 'centidegree Celsius'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, -0.26759444399999993))

# 10% of 10 degree Celsius to degree Celsius
def test_temperatures_p3():
    NEW_MODEL = Values(10, Unit('degree Celsius'), 10.0)
    TARGET_UNIT = 'degree Celsius'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.0))

# 50% of 0 degree Rankine to degree Réaumur
def test_temperatures_p4():
    NEW_MODEL = Values(0, Unit('degree Rankine'), 50.0)
    TARGET_UNIT = 'degree Réaumur'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, -109.26))

# 100% of 80 degree Réaumur to degree Fahrenheit
def test_temperatures_p5():
    NEW_MODEL = Values(80, Unit('degree Réaumur'), 100.0)
    TARGET_UNIT = 'degree Fahrenheit'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 211.99994626640427))

# 100% of 30 degree Réaumur to degree Celsius
def test_temperatures_p6():
    NEW_MODEL = Values(30, Unit('degree Réaumur'), 100.0)
    TARGET_UNIT = 'degree Celsius'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 37.5))

def test_conversion_rd():
    NEW_MODEL = Values(10, Unit('degree Celsius'))
    TARGET_UNIT = 'reciprocal degree Celsius'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.1))

# def test_temperatures_12():  TODO fix
#    NEW_MODEL = Values(1, Unit('attodegree Celsius'), 100.0)
#    TARGET_UNIT = 'degree Fahrenheit'
#    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
#    assert(floatequal(RES, -459.67))

# THERMAL RESISTNACE
# only one instance

# THERMAL INSULANCE
# only one instance

# THERMAL CONDUCTIVITY
# only one instance
