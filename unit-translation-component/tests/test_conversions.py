from unit_translation_component import Values, Unit, floatequal
# Tests for conversion between two unit of measures within the same dimnesion

# WAVENUMBER DIMENSION
# 10 kayser to reciprocal meter
def test_conversion_w1():
    NEW_MODEL = Values(10, Unit('kayser'))
    TARGET_UNIT = 'reciprocal metre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1000))

# VOLUMETRIC FLOW RATE DIMENSION
# 1 cubic metre per year to cubic metre per second
def test_conversion_vfr1():
    NEW_MODEL = Values(1, Unit('cubic metre per year'))
    TARGET_UNIT = 'cubic metre per second'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 3.1709791983764586e-08))

# 1 litre per hour to cubic metre per second
def test_division_1():  # Waiting on Dimension class story
    NEW_MODEL = Values(1, Unit('litre per hour'))
    TARGET_UNIT = 'cubic metre per second'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 2.7777777777777776e-07))

# VOLUME DIMENSION
# 25 decilitre to tablespoon (US)
def test_values_v1():
    NEW_MODEL = Values(25, Unit('decilitre'))
    TARGET_UNIT = 'tablespoon (US)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 169.0701681774777))

# 10 liquid pint (US) to tablespoon (US)
def test_values_v2():
    NEW_MODEL = Values(10, Unit('liquid pint (US)'))
    TARGET_UNIT = 'tablespoon (US)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 320.00012173052113))

# 100 deciliters to cords
def test_values_v3():
    NEW_MODEL = Values(100, Unit('decilitre'))
    TARGET_UNIT = 'cord'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.0027589586145171986))

# 1000 milliliters to cubic meter
def test_values_v4():
    NEW_MODEL = Values(100, Unit('millilitre'))
    TARGET_UNIT = 'cubic metre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.0001))

# 0.1 kiloliters to dessertspoon
def test_values_v5():
    NEW_MODEL = Values(0.1, Unit('kilolitre'))
    TARGET_UNIT = 'dessertspoon'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 10144.205974450399))

# 0.0003 acre foot to deciliters
def test_values_v6():
    NEW_MODEL = Values(0.0003, Unit('acre foot'))
    TARGET_UNIT = 'decilitre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 3700.4669999999996))

# 1 zettalitre to ton (register)
def test_conversion_v7():
    NEW_MODEL = Values(10, Unit('zettalitre'))
    TARGET_UNIT = 'ton (register)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 3.5314999198349517e+18))

# 1 cubic metre to cubic decimetre
def test_exponentiation_v8():
    NEW_MODEL = Values(1, Unit('cubic metre'))
    TARGET_UNIT = 'cubic decimetre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1000.0))

# 10 stere to barrel (US)
def test_conversion_v9():
    NEW_MODEL = Values(10, Unit('stere'))
    TARGET_UNIT = 'barrel (US)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 62.8981056977507))

# 2 cup (US customary) to ml
def test_conversion_v10():
    NEW_MODEL = Values(2, Unit('cup (US customary)'))
    TARGET_UNIT = 'millilitre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 473.1764))

# 25 peck (US) to gallon (US)
def test_conversion_v11():
    NEW_MODEL = Values(25, Unit('peck (US)'))
    TARGET_UNIT = 'gallon (US)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 58.18235901402543))

# 10 pint (imperial) to fluid ounce (US)
def test_conversion_v12():
    NEW_MODEL = Values(10, Unit('pint (imperial)'))
    TARGET_UNIT = 'fluid ounce (US)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 192.15198523815047))

# 34 liquid quart (US) to bushel (US)
def test_conversion_v13():
    NEW_MODEL = Values(34, Unit('liquid quart (US)'))
    TARGET_UNIT = 'bushel (US)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.9130774052777216))

# 1 cup (US customary) to tablespoon # cup is wrong on OM2
def test_conversion_v14():
    NEW_MODEL = Values(2, Unit('cup (US customary)'))
    TARGET_UNIT = 'tablespoon (US)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 32.00000541024538))

# 230 cubic terametre to gill (US)
def test_conversion_v15():
    NEW_MODEL = Values(230, Unit('cubic terametre'))
    TARGET_UNIT = 'gill (US)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.944306605316749e+42))

# 1 exalitre to quart (imperial)
def test_conversion_v16():
    NEW_MODEL = Values(1, Unit('exalitre'))
    TARGET_UNIT = 'quart (imperial)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 8.798944126704795e+17))


# TIME DIMENSION
# 12 hours to day
def test_values_t1():
    NEW_MODEL = Values(12, Unit('hour'))
    TARGET_UNIT = 'day'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.5))

# 1 year to day
def test_values_t2():
    NEW_MODEL = Values(1, Unit('year'))
    TARGET_UNIT = 'day'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 365))

# 12 weeks to shake
def test_values_t3():
    NEW_MODEL = Values(12, Unit('week'))
    TARGET_UNIT = 'shake'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 725760000000000))

# 675 hours to months #Exceeding recurdion depth -> nothing about month on OM2 library
# def test_values_k21():
#    NEW_MODEL = Values(675, Unit('hour'))
#    TARGET_UNIT = 'month'
#    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
#    assert(floatequal(RES, 0.924657))

# 675 nanosecond to minute
def test_values_t4():
    NEW_MODEL = Values(675, Unit('nanosecond'))
    TARGET_UNIT = 'minute'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.125e-8))


# 675 gigayear to minute
def test_values_t5():
    NEW_MODEL = Values(675, Unit('gigayear'))
    TARGET_UNIT = 'minute'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 3.5478e+17))

# SPEED DIMENSION
# 30 mile (statute) per hour to kilometre per hour
def test_conversion_s1():
    NEW_MODEL = Values(30, Unit('mile (statute) per hour'))
    TARGET_UNIT = 'kilometre per hour'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 48.28032))

# 15 knot (international) to metre per second
def test_conversion_s2():
    NEW_MODEL = Values(15, Unit('knot (international)'))
    TARGET_UNIT = 'metre per second'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 7.716666666666667))

# 1 attometre per second to metre per kilosecond
def test_conversion_s3():
    NEW_MODEL = Values(1, Unit('attometre per second'))
    TARGET_UNIT = 'metre per kilosecond'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.e-15))

# 230 kilometre per second to decimetre per second
def test_conversion_s4():
    NEW_MODEL = Values(230, Unit('kilometre per second'))
    TARGET_UNIT = 'decimetre per second'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 2.3e+06))

# 15 metre per terasecond to metre per kilosecond
def test_conversion_s5():
    NEW_MODEL = Values(15, Unit('metre per terasecond'))
    TARGET_UNIT = 'metre per kilosecond'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.5e-08))

# SPECIFIC ENERGY OR ABSORBED DOSE OR DOSE EQUIVALENT
# 12 kilojoule per hectogram to joule per kilogram
def test_conversion_se1():
    NEW_MODEL = Values(12, Unit('kilojoule per hectogram'))
    TARGET_UNIT = 'joule per kilogram'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 120000))

# 1 sievert to rem
def test_conversion_se2():
    NEW_MODEL = Values(1, Unit('sievert'))
    TARGET_UNIT = 'rem'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 100))

# 175 rad to gray
def test_conversion_se3():
    NEW_MODEL = Values(175, Unit('rad'))
    TARGET_UNIT = 'gray'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.75))

# 175 centigray to millisievert
def test_conversion_se4():
    NEW_MODEL = Values(175, Unit('centigray'))
    TARGET_UNIT = 'millisievert'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1750))


# 453 rad to decagray
def test_conversion_se5():
    NEW_MODEL = Values(453, Unit('rad'))
    TARGET_UNIT = 'decagray'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.453))

# SPECIFIC CATALYTIC ACTIVITY
# nothing to convert, as one of the unit of measures has no factor

# PRESSURE DIMENSION
# 31 torr to newton per square metre
def test_values_p1():
    NEW_MODEL = Values(31, Unit('torr'))
    TARGET_UNIT = 'newton per square metre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 4132.993421052643))

# 65 pascal to millibar
def test_values_p2():
    NEW_MODEL = Values(65, Unit('pascal'))
    TARGET_UNIT = 'millibar'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.65))

# 645 milliimetre of mercury to atmosphere (standard)
def test_values_p3():
    NEW_MODEL = Values(645, Unit('millimetre of mercury'))
    TARGET_UNIT = 'atmosphere (standard)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.8486818652849741))

# 854 barye to decibar
def test_values_p4():
    NEW_MODEL = Values(854, Unit('barye'))
    TARGET_UNIT = 'decibar'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.00854))

# 1 atmosphere (technical) to pascal
def test_values_p5():
    NEW_MODEL = Values(1, Unit('atmosphere (technical)'))
    TARGET_UNIT = 'pascal'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 9.80665e4))

# POWER DIMENSION
# 523 watt to horsepower (metric)
def test_values_pw1():
    NEW_MODEL = Values(523, Unit('watt'))
    TARGET_UNIT = 'horsepower (metric)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.7110820575098151))

# 342 watt to horsepower (water)
def test_values_pw2():
    NEW_MODEL = Values(342, Unit('watt'))
    TARGET_UNIT = 'horsepower (water)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.45841861662129396))

# 543 joule per second to ton of refrigeration
def test_values_pw3():
    NEW_MODEL = Values(543, Unit('joule per second'))
    TARGET_UNIT = 'ton of refrigeration'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.1543994019653366))

# 43 joule per second to milliwatt
def test_values_pw4():
    NEW_MODEL = Values(43, Unit('joule per second'))
    TARGET_UNIT = 'milliwatt'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 43000.00))

# PERMEANCE (MATERIAL SCIENCE)
# 21 perm (23 °C) to kilogram per pascal second square metre
def test_values_per1():
    NEW_MODEL = Values(21, Unit('perm (23 °C)'))
    TARGET_UNIT = 'kilogram per pascal second square metre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.2065025e-9))

# 32 kilogram per pascal second square metre to perm (0 °C)
def test_values_per2():
    NEW_MODEL = Values(32, Unit('kilogram per pascal second square metre'))
    TARGET_UNIT = 'perm (0 °C)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 559308554799.1))

# 167 perm (0 °C) to perm (23 °C)
def test_values_per3():
    NEW_MODEL = Values(167, Unit('perm (0 °C)'))
    TARGET_UNIT = 'perm (23 °C)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 166.3052869762))

# NUMBER DENSITY
# 1 reciprocal cubic centimetre to reciprocal cubic metre
def test_exponentiation_n1():
    NEW_MODEL = Values(1, Unit('reciprocal cubic centimetre'))
    TARGET_UNIT = 'reciprocal cubic metre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1000000.0))

# 1 reciprocal cubic parsec to reciprical cubic metre
def test_exponentiation_n2():
    NEW_MODEL = Values(1, Unit('reciprocal cubic parsec'))
    TARGET_UNIT = 'reciprocal cubic metre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 3.4036771909965277e-50))

# MASS DIMENSION
# 1 gram to milligram
def test_values_m1():
    NEW_MODEL = Values(1, Unit('gram'))
    TARGET_UNIT = 'milligram'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1000.0))

# 1 kilotonne to kilogram
def test_values_m2():
    NEW_MODEL = Values(1, Unit('kilotonne'))
    TARGET_UNIT = 'kilogram'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1000000.0))

# 0.2 slug to decigram
def test_values_m3():
    NEW_MODEL = Values(0.2, Unit('slug'))
    TARGET_UNIT = 'decigram'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 29187.8))

# 100 centigram to grain
def test_values_m4():
    NEW_MODEL = Values(100, Unit('centigram'))
    TARGET_UNIT = 'grain'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 15.432358352941433))

# 1 pound (apthecaries') to gram
def test_values_m5():
    NEW_MODEL = Values(1, Unit('pound (apthecaries\')'))
    TARGET_UNIT = 'gram'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 373.2417))

# 8 Troy pennyweight to gram
def test_values_m6():
    NEW_MODEL = Values(8, Unit('pennyweight (Troy)'))
    TARGET_UNIT = 'gram'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 12.441392))

# 7568 exagram to pounds avoirdupois
def test_values_m7():
    NEW_MODEL = Values(7568, Unit('exagram'))
    TARGET_UNIT = 'pound (avoirdupois)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.6684584002151535e+19))


# MAGNETIC FLUX
# 1200 weber to kiloweber
def test_values_mf1():
    NEW_MODEL = Values(1200, Unit('weber'))
    TARGET_UNIT = 'kiloweber'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.2))

# 3 weber to volt second
def test_values_mf2():
    NEW_MODEL = Values(3, Unit('weber'))
    TARGET_UNIT = 'volt second'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 3))

# 0.0002 volt second to unit pole
def test_values_mf3():
    NEW_MODEL = Values(0.0002, Unit('volt second'))
    TARGET_UNIT = 'unit pole'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1591.5495087284555))

# 23 unit pole to maxwell
def test_values_mf4():
    NEW_MODEL = Values(23, Unit('unit pole'))
    TARGET_UNIT = 'maxwell'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 289.02651000000003))

# 1500 volt second to milliweber
def test_values_mf5():
    NEW_MODEL = Values(1500, Unit('volt second'))
    TARGET_UNIT = 'milliweber'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1500000))


# MAGNETIC FLUX DENSITY
# 10 microtesla to millitesla
def test_values_mfd1():
    NEW_MODEL = Values(10, Unit('microtesla'))
    TARGET_UNIT = 'millitesla'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.01))

# 0.02 microtesla to gamma
def test_values_mfd2():
    NEW_MODEL = Values(0.02, Unit('microtesla'))
    TARGET_UNIT = 'gamma'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 20))

# 0.03 milligaus to picotesla
def test_values_mfd3():
    NEW_MODEL = Values(0.03, Unit('milligauss'))
    TARGET_UNIT = 'picotesla'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 3000))

# 0.021 weber per square metre to millitesla
def test_values_mfd4():
    NEW_MODEL = Values(0.021, Unit('weber per square metre'))
    TARGET_UNIT = 'millitesla'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 21))

# MAGNETIC FIELD
# 0.15 oersted to ampere per metre
def test_values_magf1():
    NEW_MODEL = Values(0.15, Unit('oersted'))
    TARGET_UNIT = 'ampere per metre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 11.9366205))

# LENGTH DIMENSION
# 500000 angstrom to yard (international)
def test_values_l1():
    NEW_MODEL = Values(500000, Unit('ångström'))
    TARGET_UNIT = 'yard (international)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 5.46806649e-5))

# 12 zettametre to yoctometre
def test_values_l2():
    NEW_MODEL = Values(12, Unit('zettametre'))
    TARGET_UNIT = 'yoctometre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.2e+46))

# 12 rod (US) to solar radius
def test_values_l3():
    NEW_MODEL = Values(12, Unit('rod (US)'))
    TARGET_UNIT = 'solar radius'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 8.677285406182603e-08))

# 0.02 parsec to point (TeX)
def test_values_l4():
    NEW_MODEL = Values(0.02, Unit('parsec'))
    TARGET_UNIT = 'point (TeX)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.7559206203061e+18))

# convert 120 point (Didot) to micron
# The result is correct using the factor on Foodvoc, however using online conversion it yields a different result
def test_values_l5():
    NEW_MODEL = Values(120, Unit('point (Didot)'))
    TARGET_UNIT = 'micron'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 45108.0))

# 150 point (ATA) to light year
def test_values_l6():
    NEW_MODEL = Values(150, Unit('point (ATA)'))
    TARGET_UNIT = 'light year'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 5.572399804243436e-18))

# 115 point (Postscript) to mil (length)
def test_values_l7():
    NEW_MODEL = Values(115, Unit('point (Postscript)'))
    TARGET_UNIT = 'mil (length)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1597.2222222222222))

# 2000 pica (ATA) to yard (international)
def test_values_l8():
    NEW_MODEL = Values(2000, Unit('pica (ATA)'))
    TARGET_UNIT = 'yard (international)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 9.224666666666666))

# 20 foot (US survey) to pica (Postscript)
def test_values_l9():
    NEW_MODEL = Values(20, Unit('foot (US survey)'))
    TARGET_UNIT = 'pica (Postscript)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1440.0028346456695))

# 100 mile (statute) to mile (US survey)
def test_values_l10():
    NEW_MODEL = Values(100, Unit('mile (statute)'))
    TARGET_UNIT = 'mile (US survey)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 99.99981358898982))

# 0.02 light year to solar radius
def test_values_l11():
    NEW_MODEL = Values(0.02, Unit('light year'))
    TARGET_UNIT = 'solar radius'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 272055.4996405464))

# 2 inch (international) to micron
def test_values_l12():
    NEW_MODEL = Values(2, Unit('inch (international)'))
    TARGET_UNIT = 'micron'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 50800))

# 150 furlong (international) to chain
def test_values_l13():
    NEW_MODEL = Values(150, Unit('furlong (international)'))
    TARGET_UNIT = 'chain'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1499.9970174242078))

# 3600 cicero to foot (US survey)
def test_values_l14():
    NEW_MODEL = Values(3600, Unit('cicero'))
    TARGET_UNIT = 'foot (US survey)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 53.277060478227405))

# 30 chain to fathom (US survey)
def test_values_l15():
    NEW_MODEL = Values(30, Unit('chain'))
    TARGET_UNIT = 'fathom (US survey)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 329.9999343833456))

# 20 inch (international) to centimetre
def test_values_l16():
    NEW_MODEL = Values(20, Unit('inch (international)'))
    TARGET_UNIT = 'centimetre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 50.8))

# 10 kilometre to hectometre
def test_values_l17():
    NEW_MODEL = Values(10, Unit('kilometre'))
    TARGET_UNIT = 'hectometre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 100.0))

# 0.000004 parsec to kilometre
def test_values_l18():
    NEW_MODEL = Values(0.000004, Unit('parsec'))
    TARGET_UNIT = 'kilometre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 123427103.25))

# KINEMATIC VISCOSITY
# 2 stokes to square metre per second
def test_values_kv1():
    NEW_MODEL = Values(2, Unit('stokes'))
    TARGET_UNIT = 'square metre per second'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.0002))

# 100 square metre per second to centistokes
def test_values_kv2():
    NEW_MODEL = Values(100, Unit('square metre per second'))
    TARGET_UNIT = 'centistokes'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 100000000))

# INDUCTANCE OR PERMEANCE (ELECTROMAGNETIC)
# 2 zettahenry to yoctohenry
def test_values_inper1():
    NEW_MODEL = Values(2, Unit('zettahenry'))
    TARGET_UNIT = 'yoctohenry'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 2e+45))

# 12 picohenry to weber per ampere
def test_values_inper2():
    NEW_MODEL = Values(12, Unit('picohenry'))
    TARGET_UNIT = 'weber per ampere'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.2e-11))

# FREQUENCY DIMENSION
# 15 zettahertz to yoctohertz
def test_values_fr1():
    NEW_MODEL = Values(15, Unit('zettahertz'))
    TARGET_UNIT = 'yoctohertz'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.5e+46))

# 0.005 curie to bacquerel
def test_values_fr2():
    NEW_MODEL = Values(0.005, Unit('curie'))
    TARGET_UNIT = 'becquerel'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 185000000))

# 23 centibecquerel to terabecquerel
def test_values_fr3():
    NEW_MODEL = Values(23, Unit('centibecquerel'))
    TARGET_UNIT = 'terabecquerel'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 2.3e-13))

# FORCE DIMENSION
# 15 centinewton to decanewton
def test_values_fo0():
    NEW_MODEL = Values(15, Unit('centinewton'))
    TARGET_UNIT = 'decanewton'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.015))

# 5 dyne to kip
def test_values_fo1():
    NEW_MODEL = Values(5, Unit('dyne'))
    TARGET_UNIT = 'kip'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.124044618276696e-08))

# 120 poundal to decanewton
def test_values_fo2():
    NEW_MODEL = Values(120, Unit('poundal'))
    TARGET_UNIT = 'decanewton'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.65906))

# 1 ton-force (short) to newton
def test_values_fo3():
    NEW_MODEL = Values(1, Unit('ton-force (short)'))
    TARGET_UNIT = 'newton'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 8896.443))

# 10 pund-force to kip
def test_values_fo4():
    NEW_MODEL = Values(10, Unit('pound-force'))
    TARGET_UNIT = 'kip'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.01))

# EXPOSURE TO X AND GAMMA RAYS
# 1600 röntgen to coulomb per kilogram
def test_values_exp1():
    NEW_MODEL = Values(1600, Unit('röntgen'))
    TARGET_UNIT = 'coulomb per kilogram'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.4128))

# ENERGY DIMENSION
# 1 terawatt hour to kilowatt hour
def test_values_e1():
    NEW_MODEL = Values(1, Unit('terawatt hour'))
    TARGET_UNIT = 'kilowatt hour'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1e09))

# 2 ton of TNT to joule
def test_values_e2():
    NEW_MODEL = Values(2, Unit('ton of TNT'))
    TARGET_UNIT = 'joule'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 8.368e+9))

# 0.2 quad to petajoule
def test_values_e3():
    NEW_MODEL = Values(0.2, Unit('quad'))
    TARGET_UNIT = 'petajoule'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 211.0112))

# 15 newton metre to foot poundal
def test_values_e4():
    NEW_MODEL = Values(15, Unit('newton metre'))
    TARGET_UNIT = 'foot poundal'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 355.9554068558435))

# 12 erg to joule
def test_values_e5():
    NEW_MODEL = Values(12, Unit('erg'))
    TARGET_UNIT = 'joule'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.2e-6))

# 0.12 therm (EC) to millijoule
def test_values_e6():
    NEW_MODEL = Values(0.12, Unit('therm (EC)'))
    TARGET_UNIT = 'millijoule'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 12660720000.0))

# ELECTRICAL RESISTANCE
# 4.7 kilohm to ohm
def test_values_er1():
    NEW_MODEL = Values(4.7, Unit('kilohm'))
    TARGET_UNIT = 'ohm'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 4700.0))

# 12 volt per ampere to teraohm
def test_values_er2():
    NEW_MODEL = Values(12, Unit('volt per ampere'))
    TARGET_UNIT = 'teraohm'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.2e-11))

# 12 kilohm to gigaohm
def test_values_er3():
    NEW_MODEL = Values(12, Unit('kilohm'))
    TARGET_UNIT = 'gigaohm'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.000012))

# ELECTRICAL CONDUCTANCE
# 0.29 abmho to ampere per volt
def test_values_elcond1():
    NEW_MODEL = Values(0.29, Unit('abmho'))
    TARGET_UNIT = 'ampere per volt'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 290000000))

# 0.44 mho to megasiemens
def test_values_elcond2():
    NEW_MODEL = Values(0.44, Unit('mho'))
    TARGET_UNIT = 'megasiemens'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 4.4e-7))

# 0.56 millisiemens to microsiemens
def test_values_elcond3():
    NEW_MODEL = Values(0.56, Unit('millisiemens'))
    TARGET_UNIT = 'microsiemens'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 560))

# ELECTRIC POTENTIAL
# 1 watt per ampere to volt
def test_values_ep1():
    NEW_MODEL = Values(1, Unit('watt per ampere'))
    TARGET_UNIT = 'volt'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.0))

# 19 yottavolt to teravolt
def test_values_ep2():
    NEW_MODEL = Values(19, Unit('yottavolt'))
    TARGET_UNIT = 'teravolt'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.9e+13))

# ELECTRIC FIELD DIMENSION
# 19 volt per metre to newton per coulomb
def test_values_ef1():
    NEW_MODEL = Values(19, Unit('volt per metre'))
    TARGET_UNIT = 'newton per coulomb'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 19))


# ELECTRIC DIPOLE MOMENT
def test_values_edp1():
    NEW_MODEL = Values(1, Unit('debye'))
    TARGET_UNIT = 'coulomb metre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 3.33564e-30))

# ELECTRIC CURRENT
# 100 abampere to ampere
def test_values_ecr1():
    NEW_MODEL = Values(100, Unit('abampere'))
    TARGET_UNIT = 'ampere'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1000.0))

# 15 biot to ampere
def test_values_ecr2():
    NEW_MODEL = Values(15, Unit('biot'))
    TARGET_UNIT = 'ampere'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 150))

# 17 milliampere to gilbert
def test_values_ecr3():
    NEW_MODEL = Values(17, Unit('milliampere'))
    TARGET_UNIT = 'gilbert'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.021362830459425265))

# 17 picoampere to milliampere
def test_values_ecr4():
    NEW_MODEL = Values(17, Unit('picoampere'))
    TARGET_UNIT = 'milliampere'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.7e-8))

# ELECTRIC CHARGE
# 9 faraday to decacoulomb
def test_values_ech1():
    NEW_MODEL = Values(9, Unit('faraday'))
    TARGET_UNIT = 'decacoulomb'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 86836.77900000001))

# 0.13 millicoulomb to franklin
def test_values_ech2():
    NEW_MODEL = Values(0.13, Unit('millicoulomb'))
    TARGET_UNIT = 'franklin'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 389730.1897896087))

# 100 nanocoulomb to picocoulomb
def test_values_ech3():
    NEW_MODEL = Values(100, Unit('nanocoulomb'))
    TARGET_UNIT = 'picocoulomb'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 100000))

# DYNAMIC VISCOSITY
# 45 poise to centipoise
def test_values_edv1():
    NEW_MODEL = Values(45, Unit('poise'))
    TARGET_UNIT = 'centipoise'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 4500))

# 100 poise to pascal second
def test_values_edv2():
    NEW_MODEL = Values(100, Unit('poise'))
    TARGET_UNIT = 'pascal second'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 10))

# DENSITY DIMENSION
# 100 gram per centilitre to tonne per cubic metre
def test_division_d1():  # Waiting on Dimension class story
    NEW_MODEL = Values(100, Unit('gram per centilitre'))
    TARGET_UNIT = 'tonne per cubic metre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 10.0))

# 1 megagarm per litre to gram per litre
def test_division_d2():
    NEW_MODEL = Values(1, Unit('megagram per litre'))
    TARGET_UNIT = 'gram per litre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1e06))

# 12 solar mass per cubic parsec to gram per litre
def test_division_d3():
    NEW_MODEL = Values(12, Unit('solar mass per cubic parsec'))
    TARGET_UNIT = 'gram per litre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 8.123569966460175e-19))

# 21 kilogram per cubic decimetre to gram per picolitre
def test_division_d4():
    NEW_MODEL = Values(21, Unit('kilogram per cubic decimetre'))
    TARGET_UNIT = 'gram per picolitre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 2.1e-8))

# COLOUMN NUMBER DENSITY DIMENSION
# 1 reciprocal square metre to reciprocal square centimetre
def test_values_cnd1():
    NEW_MODEL = Values(1, Unit('reciprocal square metre'))
    TARGET_UNIT = 'reciprocal square centimetre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.0001))

# CATALYC ACTIVITY DIMENSION
# amylase unit is both under catalyc activity and under singular unit; no info about it on OM2
# same comment delta A450 per second

# 7345 katal to mole per second
def test_values_cact1():
    NEW_MODEL = Values(7345, Unit('katal'))
    TARGET_UNIT = 'mole per second'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 7345))

# 654 micromole per second to picokatal
def test_values_cact2():
    NEW_MODEL = Values(654, Unit('micromole per second'))
    TARGET_UNIT = 'picokatal'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 654000000))

# CAPACITANCE DIMENSION
# 0.00620 megafarad to coulomb per volt
def test_values_cap1():
    NEW_MODEL = Values(0.00620, Unit('megafarad'))
    TARGET_UNIT = 'coulomb per volt'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 6200))

# 0.054 terafarad to centifarad
def test_values_cap2():
    NEW_MODEL = Values(0.054, Unit('terafarad'))
    TARGET_UNIT = 'centifarad'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 5.4e+12))

# AREA DIMENSION
# 167534 darcy to square metre
def test_values_area1():
    NEW_MODEL = Values(167534, Unit('darcy'))
    TARGET_UNIT = 'square metre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 1.653432081422e-7))

# 6543 circular mil to square millimetre
def test_values_area2():
    NEW_MODEL = Values(6543, Unit('circular mil'))
    TARGET_UNIT = 'square millimetre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 3.3153871725000004))

# 0.065 hectare to acre (international)
def test_values_area3():
    NEW_MODEL = Values(0.065, Unit('hectare'))
    TARGET_UNIT = 'acre (international)'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.16061849795365746))

# 93425 barn to square centimetre
def test_values_area4():
    NEW_MODEL = Values(93425, Unit('barn'))
    TARGET_UNIT = 'square centimetre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 9.3425e-20))

# 100 are to square centimetre
def test_values_area5():
    NEW_MODEL = Values(100, Unit('are'))
    TARGET_UNIT = 'square metre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 10000))

# ANGULAR SPEED
# cannot suport due to OM2 'millisecond (angle) per year' unit; there is no information about it
# No unit 'radian per millisecond' or 'cycle per millisecond' (not in OM2, but they exist and are convertible)

# 0.054 radian per second to millisecond (angle) per year
def test_values_ang1():
    NEW_MODEL = Values(0.054, Unit('radian per second'))
    TARGET_UNIT = 'millisecond (angle) per year'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 351257400523128.8))

# AMOUNT OF SUBSTANCE DIMENSION - ONLY PREFIX
# 0.054 hectomole to centimole
def test_values_as1():
    NEW_MODEL = Values(0.054, Unit('hectomole'))
    TARGET_UNIT = 'centimole'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 540))

# 0.0004 zettamole to attomole
def test_values_as2():
    NEW_MODEL = Values(0.0004, Unit('zettamole'))
    TARGET_UNIT = 'attomole'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 4e+35))

# AMOUNT OF SUBSTANCE CONCENTRATION DIMENSION
# 0.0074 mole per millilitre to micromolair
def test_values_subcon1():
    NEW_MODEL = Values(0.0074, Unit('mole per millilitre'))
    TARGET_UNIT = 'micromolair'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 7400000))

# 324 millimolair to mole per cubic metre
def test_values_subcon2():
    NEW_MODEL = Values(324, Unit('millimolair'))
    TARGET_UNIT = 'mole per cubic metre'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 324))

# ACTION OR ANGULAR MOMENTUM
# 0.00045 joule per second squared to erg per second
def test_values_aa1():
    NEW_MODEL = Values(0.00045, Unit('joule second'))
    TARGET_UNIT = 'erg second'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 4500))

# ACCELERATION
# 4.7 hectometre per second squared to gal
def test_values_a1():
    NEW_MODEL = Values(4.7, Unit('hectometre per second squared'))
    TARGET_UNIT = 'gal'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 47000))

# SINGULAR UNIT DIMENSION
# 1000 MB to TB
def test_values_s1():
    NEW_MODEL = Values(1000, Unit('megabyte'))
    TARGET_UNIT = 'terabyte'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 0.001))

# DIMENSION ONE
# 100 metre per metre to radian
def test_values_one1():
    NEW_MODEL = Values(100, Unit('metre per metre'))
    TARGET_UNIT = 'radian'
    RES = NEW_MODEL.to_unit(Unit(TARGET_UNIT))
    assert(floatequal(RES, 100.0))
