from unit_translation_component import Values, Unit, floatequal

def test_conversion_en_nl():
    NEW_MODEL = Values(1000, Unit('kilogram'))
    TARGET_UNIT = 'ton'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT, lang = 'nl'))
    assert(floatequal(RES, 1.0))

def test_converion_nl_nl():
    NEW_MODEL = Values(1, Unit('decaliter', lang = 'nl'))
    TARGET_UNIT = 'liter'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT, lang = 'nl'))
    assert(floatequal(RES, 10.0))

def test_conversion_nl_en():
    NEW_MODEL = Values(1000, Unit('kilogram', lang = 'nl'))
    TARGET_UNIT = 'tonne'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT, lang = 'en'))
    assert(floatequal(RES, 1.0))

def test_conversion_en_en():
    NEW_MODEL = Values(1000, Unit('kilogram', lang = 'en'))
    TARGET_UNIT = 'tonne'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT, lang = 'en'))
    assert(floatequal(RES, 1.0))
