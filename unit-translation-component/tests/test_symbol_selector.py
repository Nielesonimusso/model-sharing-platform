from unit_translation_component import Unit

def test_selector_kg():
    NEW_MODEL = Unit('kg', True)
    assert(NEW_MODEL.label == 'kilogram')

def test_selector_ampere():
    NEW_MODEL = Unit('A', True)
    assert(NEW_MODEL.label == 'ampere')

def test_selector_gram():
    NEW_MODEL = Unit('g', True)
    assert(NEW_MODEL.label == 'gram')

def test_selector_tonne():
    NEW_MODEL = Unit('t', True)
    assert(NEW_MODEL.label == 'tonne')

def test_selector_minute_hourangle():  # m == 'metre' or 'minute-HourAngle'
    NEW_MODEL = Unit('m', True)
    assert(NEW_MODEL.label == 'minute-HourAngle' or NEW_MODEL.label == 'metre')

def test_selector_byte():
    NEW_MODEL = Unit('B', True)
    assert(NEW_MODEL.label == 'byte')

def test_selector_kb():
    NEW_MODEL = Unit('kB', True)
    assert(NEW_MODEL.label == 'kilobyte')

def test_selector_cubic_metre():
    NEW_MODEL = Unit('m3', True)
    assert(NEW_MODEL.label == 'cubicMetre')


