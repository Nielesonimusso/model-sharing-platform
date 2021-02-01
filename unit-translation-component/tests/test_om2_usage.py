from unit_translation_component import Unit, constant

def test_om2_usage_1():
    NEW_MODEL = Unit('kayser')
    assert(constant.OM2 in NEW_MODEL.get_dimension_attribute() and constant.OM2 in NEW_MODEL.get_unit_attribute())

def test_om2_usage_2():
    NEW_MODEL = Unit('newton metre')
    assert(constant.OM2 in NEW_MODEL.get_dimension_attribute() and constant.OM2 in NEW_MODEL.get_unit_attribute())
    
def test_om2_usage_3():
    NEW_MODEL = Unit('joule per cubic metre kelvin')
    assert(constant.OM2 in NEW_MODEL.get_dimension_attribute() and constant.OM2 in NEW_MODEL.get_unit_attribute())

def test_om2_usage_4():
    NEW_MODEL = Unit('degree Réaumur')
    assert(constant.OM2 in NEW_MODEL.get_dimension_attribute() and constant.OM2 in NEW_MODEL.get_unit_attribute())
