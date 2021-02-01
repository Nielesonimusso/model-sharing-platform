from unit_translation_component import Unit

def test_mistyped_kilogram():
	NEW_MODEL = Unit('klogram')
	assert(NEW_MODEL.label == 'kilogram')

def test_mistyped_metre():
	NEW_MODEL = Unit('meter')
	assert(NEW_MODEL.label == 'metre')

def test_mistyped_centimetre_per_second_squared():
	NEW_MODEL = Unit('centimetre per second sqred')
	assert(NEW_MODEL.label == 'centimetrePerSecond-TimeSquared')

def test_mistyped_gallon_us():
	NEW_MODEL = Unit('gallon US')
	assert(NEW_MODEL.label == 'gallon-US')
