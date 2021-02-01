from __future__ import annotations
import unit_translation_component.constant as ct
from unit_translation_component.prefix import Prefix
from unit_translation_component.exception import UnitNotFoundException, ParameterMismatchException, UnitsNotComparableException, GenericException
from unit_translation_component.dimension import Dimension
from unit_translation_component.scale import TemperatureScale
from unit_translation_component.redis_instance import RedisObject
from unit_translation_component.corrector import SpellCheckerObject
from progress.bar import Bar
import json


class Unit:
    # Represents a unit of measure
    # Uses the Ontology of unit of measure to provide conversions between units
    # Can make use of Redis for caching to speed up the conversion process

    def __init__(self, unit_string: str, symbol: bool = False, lang: str = "en", internal: bool = False):
        self.__init_flags()

        # Find unit_string in graph, if not found, raise exception
        # We need to include this exception to be sure the initial unit is correctly input
        def q_find_unit():
            return '''
                PREFIX OM2: ''' + ct.PREFIX_OM2 + '''
                PREFIX rdfs: ''' + ct.PREFIX_RDFS + '''
                PREFIX rdf: ''' + ct.PREFIX_RDF + '''

                select distinct ?u where {
                    ?u rdf:type ?o .FILTER regex(str(?o), "Unit|Prefixed")'''

        def searchlabel(unit_string: str, lang: str = 'en'):
            return '''
                        ?u rdfs:label "''' + str(unit_string) + '''"@''' + lang + ''' .
                }'''

        def q_labels(URIRef):
            return '''
                PREFIX OM2: ''' + ct.PREFIX_OM2 + '''
                PREFIX rdfs: ''' + ct.PREFIX_RDFS + '''
                PREFIX rdf: ''' + ct.PREFIX_RDF + '''

                select ?o where {
                    <''' + str(URIRef) + '''> rdfs:label ?o .
            }'''

        find_symbol = '''
                        ?u ''' + ct.PREFIX_SYMBOL + ''' "''' + str(unit_string) + '''" .
                    }'''
        query_unit = ''
        if symbol is True:
            query_unit = q_find_unit() + find_symbol
        else:
            query_unit = q_find_unit() + searchlabel(unit_string, lang)

        # First, search for the unit string
        r_find_unit = ct.OMGraph.query(query_unit)
        if len(r_find_unit) == 0 and not internal:
            # If not found, search for the symbol
            query_unit = q_find_unit() + find_symbol
            r_find_unit = ct.OMGraph.query(query_unit)
            if len(r_find_unit) == 0:
                # If still not found, try to correct the unit string and query again
                query_unit = q_find_unit() + \
                    searchlabel(SpellCheckerObject.get_instance(
                    ).correction(str(unit_string)))
                r_find_unit = ct.OMGraph.query(query_unit)

                # If still not found, raise exception
                if len(r_find_unit) == 0:
                    raise UnitNotFoundException(unit_string)

        if not internal:
            for row in r_find_unit:
                self.label, self.URIRef = ct.trim_uri(row)
                break
        else:
            self.label, self.URIRef = ct.trim_uri(unit_string)

        if len(r_find_unit) > 1 and not internal:
            print(
                "Warning: More units with the same label/symbol found. Using %s." % (self.label))

        # Get english labels needed for dictionary
        self.labels = []
        r_labels = ct.OMGraph.query(q_labels(self.URIRef))
        for rrow in r_labels:
            language = str(rrow.asdict()).partition("lang=")
            if language[2][1] == 'e' and language[2][2] == 'n':
                self.labels.append(str(rrow).partition('\'')
                                   [2].partition('\'')[0])

        q_get_attributes = '''
                            select ?p ?o where {
                                <''' + self.URIRef + '''> ?p ?o
                            }'''

        self.__init_unit_from_rdf(q_get_attributes)

    def __init_unit_from_rdf(self, query_attributes: str):
        # Get attributes of specific unit and add them as fields to the object
        # Compare keys in predicate with pre-defined constants to determine the attributes
        r_get_attributes = ct.OMGraph.query(query_attributes)
        for pred, out in r_get_attributes:
            if str(pred) == ct.PREFIX_TYPE:
                if "UnitDivision" in ct.trim_uri(out)[0]:
                    self.f_division = True
                if "UnitExponentiation" in ct.trim_uri(out)[0]:
                    self.f_exponentiation = True
                if "UnitMultiplication" in ct.trim_uri(out)[0]:
                    self.f_multiplication = True
            if str(pred) == ct.HAS_DIMENSION:
                self.__has_dimension = out
                if str(self.__has_dimension) == ct.PREFIX_TEMP:
                    self.f_temperature = True
            if str(pred) == ct.HAS_FACTOR:
                self.__has_factor = out
            if str(pred) == ct.HAS_PREFIX:
                self.__has_prefix = Prefix(out)
                self.f_prefixed = True
            if str(pred) == ct.HAS_UNIT:
                self.__has_unit = out
            if str(pred) == ct.HAS_EXPONENT:
                self.__has_exponent = out
            if str(pred) == ct.HAS_NUMERATOR:
                self.f_division = True
                self.__has_numerator = out
            if str(pred) == ct.HAS_DENOMINATOR:
                self.f_division = True
                self.__has_denominator = out
            if str(pred) == ct.HAS_BASE:
                self.f_exponentiation = True
                self.__has_base = out
            if str(pred) == ct.HAS_TERM1:
                self.f_multiplication = True
                self.__has_term1 = out
            if str(pred) == ct.HAS_TERM2:
                self.__has_term2 = out
            if str(pred) == ct.HAS_QUANTITY and str(out) == ct.IT_QUANTITY:
                self.f_it_quantity = True
            if str(pred) == ct.RDF_SCHEMA_LABEL:
                if not hasattr(self, 'labels'):
                    self.labels = []
        self.f_singular = not (
            self.f_division or self.f_exponentiation or self.f_multiplication or self.f_it_quantity)

    def __init_flags(self):
        # Init flags
        self.f_division = False
        self.f_exponentiation = False
        self.f_multiplication = False
        self.f_temperature = False
        self.f_it_quantity = False
        self.f_prefixed = False

    def can_convert_to(self, param):
        # Checks if the provided unit can be converted into this unit
        if not isinstance(param, Unit):
            raise ParameterMismatchException(param)
        if self.get_dimension_attribute() == "undefined" or param.get_dimension_attribute() == "undefined":
            # If dimension is not defined for a unit, calculate and compare them.
            d_self = self.get_dimension_object()
            d_param = param.get_dimension_object()
            if d_self.dim_equals(d_param):
                return True
        if self.get_dimension_attribute() != param.get_dimension_attribute():
            raise UnitsNotComparableException(self.label, self.get_dimension_attribute(
            ), param.label, param.get_dimension_attribute())
        return True

    # Getters
    def get_dimension_attribute(self):
        # Get the dimension attribute of this unit
        if hasattr(self, '_Unit__has_dimension'):
            return self.__has_dimension
        return "undefined"

    def get_dimension_object(self):
        # Get the dimension of this unit.
        # Creates and returns an object of type Dimension
        if self.f_division is True:
            return Dimension(self.get_numerator_unit().get_dimension_attribute()).dim_sub(Dimension(self.get_denominator_unit().get_dimension_attribute()))
        elif self.f_multiplication is True:
            return Dimension(self.get_term1_unit().get_dimension_attribute()).dim_sum(Dimension(self.get_term2_unit().get_dimension_attribute()))
        elif self.f_exponentiation is True:
            return Dimension(self.get_base_unit().get_dimension_attribute())
        else:
            return Dimension(self.get_dimension_attribute())

    def get_unit_attribute(self):
        # Get the unit attribute of this unit instance
        if hasattr(self, '_Unit__has_unit'):
            return self.__has_unit
        return self.URIRef

    def get_factor_only_attribute(self):
        # Get the factor attribute of this unit""
        if hasattr(self, '_Unit__has_factor'):
            return float(self.__has_factor)
        return 1.0

    def get_prefix_factor(self):
        # Get the factor of the prefix (milli, centi, etc)
        if self.f_prefixed:
            return float(self.__has_prefix.get_factor())
        return 1.0

    def get_factor_attribute(self):
        # Get the factor if possible, otherwise return the prefix factor
        if hasattr(self, '_Unit__has_factor'):
            return float(self.__has_factor)
        if self.f_prefixed:
            return float(self.__has_prefix.get_factor())
        return 1.0

    def get_exponent_attribute(self):
        # Get the exponent of this unit
        if hasattr(self, '_Unit__has_exponent'):
            return float(self.__has_exponent)
        return "undefined"

    def get_numerator_attribute(self):
        # Get the numerator of this unit
        if hasattr(self, '_Unit__has_numerator'):
            return self.__has_numerator
        return "undefined"

    def get_numerator_unit(self):
        # Get the unit of the numerator of this unit
        return Unit(self.get_numerator_attribute(), internal=True)

    def get_base_attribute(self):
        # Get the base unit attribute
        if hasattr(self, '_Unit__has_base'):
            return self.__has_base
        return "undefined"

    def get_base_unit(self):
        # Get the base unit as a new unit instance
        return Unit(self.get_base_attribute(), internal=True)

    def get_denominator_attribute(self):
        # Get the denominator
        if hasattr(self, '_Unit__has_denominator'):
            return self.__has_denominator
        return "undefined"

    def get_denominator_unit(self):
        # Get the denominator as a new unit instance
        return Unit(self.get_denominator_attribute(), internal=True)

    def get_term1_attribute(self):
        # Get first term for units of the form `a*b`
        if hasattr(self, '_Unit__has_term1'):
            return self.__has_term1
        return "undefined"

    def get_term1_unit(self):
        # Get first term as a unit for units of the form `a*b`
        return Unit(self.get_term1_attribute(), internal=True)

    def get_term2_attribute(self):
        # Get second term for units of the form `a*b`
        if hasattr(self, '_Unit__has_term2'):
            return self.__has_term2
        return "undefined"

    def get_term2_unit(self):
        # Get second term as a unit for units of the form `a*b`
        return Unit(self.get_term2_attribute(), internal=True)

    def to_kelvin(self, quantity):
        # Convert the given quantity of the unit to kelvin
        if self.f_prefixed:
            offset = offset = TemperatureScale(
                self.get_unit_attribute()).get_offset()
        else:
            offset = TemperatureScale(self.URIRef).get_offset()
        factor = self.get_factor_only_attribute()
        return (quantity * self.get_prefix_factor() - offset) * factor

    def from_kelvin(self, quantity):
        # Convert a given quantity in kelvin to the unit this instance has
        if self.f_prefixed:
            offset = TemperatureScale(self.get_unit_attribute()).get_offset()
        elif self.f_exponentiation:
            offset = TemperatureScale(self.get_base_attribute()).get_offset()
        else:
            offset = TemperatureScale(self.URIRef).get_offset()
        factor = self.get_factor_only_attribute()

        if self.f_exponentiation:
            return ((quantity * (factor ** (-1))) + offset) ** self.get_exponent_attribute()
        return ((quantity * (factor ** (-1))) + offset) * self.get_prefix_factor()

    def get_factor_si(self):
        # Get unit's factor w.r.t. international system units
        # Composite division unit has num / den
        if self.f_division:
            numerator = Unit(self.get_numerator_attribute(), internal=True)
            denominator = Unit(self.get_denominator_attribute(), internal=True)

            f1 = numerator.get_factor_si()
            f2 = denominator.get_factor_si()

            if f1 is None or f2 is None:
                return None

            factor = f1 / f2
            return factor

        # Composite multiplication unit has a * b
        elif self.f_multiplication:
            term1 = Unit(self.get_term1_attribute(), internal=True)
            term2 = Unit(self.get_term2_attribute(), internal=True)

            f1 = term1.get_factor_si()
            f2 = term2.get_factor_si()

            if f1 is None or f2 is None:
                return None

            factor = f1 * f2
            return factor

        # Unit with exponentation, has b^e
        elif self.f_exponentiation:
            base = Unit(self.get_base_attribute(), internal=True)

            bf = base.get_factor_si()
            if bf is None:
                return None

            factor = bf ** float(self.get_exponent_attribute())
            return factor

        # A simple quantity has no factor
        elif self.f_it_quantity:
            return 1.0

        # A single unit
        elif self.f_singular:
            # If the searched unit is a SI Unit, return 1.0 as factor
            for si_unit in ct.SI_units:
                if self.label == Unit(si_unit, internal=True).label:
                    return 1.0

            if self.get_unit_attribute() is not self.URIRef:
                next_unit = Unit(self.get_unit_attribute(), internal=True)
                f = next_unit.get_factor_si()
                if f is None:  # Return None if one computed factor is None
                    return None
                factor = self.get_factor_attribute() * f
                return factor
            else:
                return None
        else:
            raise GenericException(
                "Conversion not defined. Please report the repordouction steps to the developers.")

    def __eq__(self, other: Unit):
        return other is not None and isinstance(other, Unit) and self.URIRef == other.URIRef and self.label == other.label

    def __repr__(self):
        return f'<{type(self).__name__} label: {self.label}, uri: {self.URIRef}>'


def cache_units():
    # Initializes the Redis cache by adding all units
    if not RedisObject.available():
        print("Redis instance not available. Exiting.")
        return

    cached = 0
    unit_list = ct.get_units_uri()
    warnings = []
    dictdata = {}
    with Bar('Processing', max=len(unit_list), suffix='%(index)d/%(max)d [%(elapsed_td)s]') as bar:
        for label, uri in unit_list:
            # Initialize Unit and calculate SI factor
            unit = Unit(uri, internal=True)
            factor = unit.get_factor_si()
            if factor is not None:
                for label in unit.labels:  # Create dictionary
                    dictdata[label] = 1
                # Set factor on redis
                RedisObject.get_instance().hmset(uri, {'factor_si': factor})
                cached = cached + 1
                bar.message = f'Processed {unit.label}'
            else:
                warnings.append(
                    f"WARNING: Unit {label} cannot be expressed in SI.")
            bar.next()
        bar.finish()

    print("Cached %d units." % (cached))

    # Save dictionary
    with open(SpellCheckerObject.path(), 'w') as outfile:
        json.dump(dictdata, outfile)

    # Print logged warnings
    if len(warnings) > 0:
        print("Finished with warnings.")
        for warning in warnings:
            print(warning)
