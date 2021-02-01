from unit_translation_component.unit import Unit
from unit_translation_component.values import Values


#REQUIREMENT URRB1 - When  the  Ontology  Based  Unit  Conversion  is  called,  the  AVERAGE  time  to  perform  a  Unit  conversion  shall  not  exceed  20 milliseconds.

import time
start = time.time()
RES1 = Values(10, Unit('kayser')).to_unit(Unit('reciprocal metre'))
RES2 = Values(1, Unit('cubic metre')).to_unit(Unit('cubic decimetre'))
RES3 = Values(12, Unit('hour')).to_unit(Unit('day'))
RES4 = Values(10000, Unit('second')).to_unit(Unit('year'))
RES5 = Values(10, Unit('degree Celsius')).to_unit(Unit('degree Fahrenheit'))
RES6 = Values(45.88, Unit('degree Celsius')).to_unit(Unit('reciprocal degree Celsius'))
RES7 = Values(10, Unit('degree Réaumur')).to_unit(Unit('degree Rankine'))
RES8 = Values(-3, Unit('degree Rankine')).to_unit(Unit('degree Fahrenheit'))
RES9 = Values(10, Unit('kiloampere')).to_unit(Unit('biot'))
RES10 = Values(30.2, Unit('slug')).to_unit(Unit('tonne'))
RES11 = Values(30.2, Unit('ounce (avoirdupois)')).to_unit(Unit('gram'))
RES12 = Values(25, Unit('carat (mass)')).to_unit(Unit('gram')) 
RES13 = Values(1000, Unit('gram')).to_unit(Unit('kilogram'))
RES14 = Values(13, Unit('peck (US)')).to_unit(Unit('gallon (US)'))
RES15 = Values(1, Unit('metre')).to_unit(Unit('kilometre'))
RES16 = Values(88, Unit('year')).to_unit(Unit('day'))
RES17 = Values(32, Unit('pascal')).to_unit(Unit('millibar'))
RES18 = Values(1, Unit('volt per ampere')).to_unit(Unit('ohm'))
RES19 = Values(0, Unit('metre')).to_unit(Unit('centimetre'))
RES20 = Values(331, Unit('inch (international)')).to_unit(Unit('metre'))
end = time.time()
print('Proving requirement URRB1')
print(str('Confirm that the average time for a conversion is: ') + str((end-start)/20*1000) + ' ms')
print('')

