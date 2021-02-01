from unit_translation_component.ontology import OMGraph

# Declare OM2 path
OM2 = 'http://www.ontology-of-units-of-measure.org/resource/om-2/'
RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
RDFS = 'http://www.w3.org/2000/01/rdf-schema#'

# Declare most used prefixes
PREFIX_OM2 = '<' + OM2 + '>'
PREFIX_RDFS = '<' + RDFS + '>'
PREFIX_RDF = '<' + RDF + '>'

# Declare symbol
PREFIX_SYMBOL = '<' + OM2 + 'symbol' + '>'
PREFIX_TYPE = RDF + 'type'

# Declare attributes of a Unit
HAS_DIMENSION = OM2 + 'hasDimension'
HAS_FACTOR = OM2 + 'hasFactor'
HAS_UNIT = OM2 + 'hasUnit'
HAS_PREFIX = OM2 + 'hasPrefix'
HAS_EXPONENT = OM2 + 'hasExponent'
HAS_DENOMINATOR = OM2 + 'hasDenominator'
HAS_NUMERATOR = OM2 + 'hasNumerator'
HAS_BASE = OM2 + 'hasBase'
HAS_TERM1 = OM2 + 'hasTerm1'
HAS_TERM2 = OM2 + 'hasTerm2'
HAS_OFFSET_TEMP = OM2 + 'hasOff-Set'
HAS_QUANTITY = OM2 + 'hasQuantity'
RDF_SCHEMA_LABEL = 'http://www.w3.org/2000/01/rdf-schema#label'

# Declare temperature
PREFIX_TEMP = 'http://www.ontology-of-units-of-measure.org/resource/om-2/thermodynamicTemperature-Dimension'
# Declare information technology Quantity (used as a dimension)
IT_QUANTITY = OM2 + 'informationCapacityOfOneBinaryDigit'
# Declare dimensions
SI_properties = [
    'hasSITimeDimensionExponent',
    'hasSILengthDimensionExponent',
    'hasSIMassDimensionExponent',
    'hasSIThermodynamicTemperatureDimensionExponent',
    'hasSIElectricCurrentDimensionExponent',
    'hasSIAmountOfSubstanceDimensionExponent',
    'hasSILuminousIntensityDimensionExponent'
]

SI_units_URI = OM2 + 'InternationalSystemOfUnits'
base_unit = OM2 + 'hasBaseUnit'

q_SI = '''
    select ?o where {
        <''' + SI_units_URI + '''> <''' + base_unit + '''> ?o
    }
'''

SI_units = []
for r in OMGraph.query(q_SI):
    SI_units.append(r)


def trim_uri(uri_ref):
    """Retrieves tuple (label, uriref)"""
    aux_string = str(uri_ref)
    aux_string = aux_string.partition(OM2)
    aux_string = aux_string[2].partition('\'')
    return (aux_string[0], OM2 + aux_string[0])


def floatequal(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def get_units_uri():
    query = '''
        PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        select distinct ?u where {
            ?u rdf:type ?o .FILTER regex(str(?o), "Unit|Prefixed") .
        }'''
    unit_list = []
    for uri in OMGraph.query(query):
        unit_list.append(trim_uri(uri))
    return unit_list
