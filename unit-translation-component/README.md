# Ontology Based Conversion Library

## Pip installation procedure
python -m pip install git+https://gitlab.tue.nl/sep-group-10/sep-2020-group-10.git

You might need to enter credentials in order to install the package.

## Library description
This Python library is based on the web resource OM2 found at http://www.ontology-of-units-of-measure.org/resource/om-2 . 
Below you can find more information about the library.

## Unit class initialisation options:
This Python library allows the user to instantiate a unit of measure based on 3 options:
* full unit name (e.g. 'degree Celsius', 'decimetre'). Example: `Unit('kilometre')`
* unit symbol (e.g. 'km' from kilometre, 'dm' for decimetre) => in order to enable this initialisation, the user also needs to provide an extra argument. Examples: `Unit('km', symbol = True)`, `Unit('dm', True)`
* URI reference. This option has been allowed in order to also improve code maintainability and code reusability => in order to enable this initialisation the user also needs to provide an extra argument *internal*. Examples: 
    * `Unit('http://www.ontology-of-units-of-measure.org/resource/om-2/attodegreeCelsius', internal = True)`
    * `Unit('http://www.ontology-of-units-of-measure.org/resource/om-2/terabyte', internal = True)`

## Value class initialisation options:
* basic initialisation: provide a float variable as parameter and a Unit class as the other parameter (example: `Values(1, Unit(terawatt hour))`)
* percentage initialisation: to enable percentage computations, provide an extra argument compared to the initialisation from above, a float between 0.0 - 100.0 depicting the percentage. Example: Values(10, Unit('kilogram'), 80.0) - which means 80% of 10 kilograms.

## General knowledge about the classes and methods:
**Values class is the functional class of the library**, such that the user only needs to import the Values file into their Python application. The Values class presents the functional method: to_unit(target_unit)<br/>
If the user wishes to **initialise Values modularly**, the user needs to also import the Unit class. 
Example:<br/>
```
initial_unit = Unit('kilometre')
initial_value = Values(10, initial_unit)
```

## Basic setup:
The library presents a two-step calling procedure:
1. First the user needs to create a Value, which is a coupling between a numerical value and a unit of measure class. Examples:
`Values(10, Unit('degree Rankine'))` / `Values(1, Unit('km', True))` / `Values(1, 'http://www.ontology-of-units-of-measure.org/resource/om-2/terabyte', internal = True)`
1. Second, the user needs to call the `to_unit()` method of the Value class instantiated at the previous point. The user needs to provide a Unit argument in this method. Example:`to_unit(Unit('kilometre'))`
1. Thus, a functional call of this python library would look like: 
```
initial_value = Values(10, Unit('kilometre'))
initial_value.to_unit(Unit('metre'))
```
## Units of measure not supported

### Application areas not supported by this library

**Typography**: units of measure such as: cicero, pica (ATA), pica (Postscript), pica (TeX), point (ATA), point (Didot), point (Postscript), point (TeX)<br/>
**Photometry**: units of measure such as: candela and all prefixed candela units, lumen and all prefixed lumen units, lux and all prefixed lux units and other units from http://www.ontology-of-units-of-measure.org/resource/om-2/photometry<br/>
**Cosmology**: units of measure from http://www.ontology-of-units-of-measure.org/resource/om-2/cosmology<br/>
**Astronomy and astrophysics**: units of measure from http://www.ontology-of-units-of-measure.org/resource/om-2/astronomyAndAstrophysics<br/>

### Currency units of measure
The Ontology Based Conversion Library does not support currency conversions as there is no information about the relation between these units. Below there are 2 examples of currency units web resources from OM2:<br/>
http://www.ontology-of-units-of-measure.org/resource/om-2/poundSterling<br/>
http://www.ontology-of-units-of-measure.org/resource/om-2/euro<br/>

### Units of measure not defined or whose values are wrongly defined in OM2

**specific catalytic activity** this dimension is not supported because OM2 does not define a factor for the unit of measure delta A450. For more information please refer to: http://www.ontology-of-units-of-measure.org/resource/om-2/deltaA450<br/>
**month** any conversion that includes this unit of measure is not supported because OM2 does not define a factor. For more information please refer to: http://www.ontology-of-units-of-measure.org/resource/om-2/month
<br/>
<br/>
***This Library has been designed as part of the 2IPE0 Software Engineering Project course of the Bachelor of Computer Science and Engineering at the Technical University of Eindhoven**.*
