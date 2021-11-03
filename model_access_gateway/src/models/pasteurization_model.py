import json, math
from typing import Dict, List, Tuple

from marshmallow import fields
import rdflib

from common_data_access.dtos import BaseDto, RunModelDtoSchema
from model_access_gateway.src.ingredient_store import get_ingredient_properties
from model_access_gateway.src.models.model import Model
from common_data_access import string_utils
from .model import get_model_ontology_dependency

import sys

OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')
HDB = rdflib.Namespace(get_model_ontology_dependency('hex'))
MDB = rdflib.Namespace(get_model_ontology_dependency('microbe'))

class PSFlowTableDto(BaseDto):
    product_flow = fields.Float() 

    units = dict(
        product_flow = OM["kilogramPerSecond-Time"],
    )
    references = dict(
        product_flow = None,
    )

class PSTemperatureTableDto(BaseDto):
    product_temperature = fields.Float() 

    units = dict(
        product_temperature = OM.degreeCelcius,
    )
    references = dict(
        product_temperature = None,
    )

class PSDensityTableDto(BaseDto):
    product_density = fields.Float() 

    units = dict(
        product_density = OM.kilogramPerLitre,
    )
    references = dict(
        product_density = None,
    )

class HTInternalDiameterTableDto(BaseDto):
    holding_tube_internal_diameter = fields.Float() 

    units = dict(
        holding_tube_internal_diameter = OM.millimetre,
    )
    references = dict(
        holding_tube_internal_diameter = None,
    )

class HTLengthTableDto(BaseDto):
    holding_tube_length = fields.Float() 

    units = dict(
        holding_tube_length = OM.metre,
    )
    references = dict(
        holding_tube_length = None,
    )


class PasteurizationDto(BaseDto):
    hex_type = fields.Str() 
    outlet_temperature =  fields.Float() 

    units = dict(
        hex_type = None,
        outlet_temperature = OM.degreeCelsius, # fixed unit (degrees C)
    )
    references = dict(
        hex_type = dict(
            source = HDB.HeatExchangers,
            property = HDB.Type
        ), # reference to hex types data source
        outlet_temperature = None,
    )


class MicrobeDto(BaseDto):
    microbe = fields.Str() 
    amount = fields.Float() 

    units = dict(
        microbe = None,
        amount = OM.colonyFormingUnitPerMillilitre, # fixed unit (colonyFormingUnitPerMillilitre (no log!))
    )
    references = dict(
        microbe = dict(
            source = MDB.Microbes,
            property = MDB.Organism
        ), # reference to microbe data source
        amount = None,
    )


class MicrobeUnitDto(BaseDto):
    microbe = fields.Str()
    amount = fields.Float()
    unit = fields.Str() # in practice always [colonyFormingUnitPerMillilitre (no log!)]

    units = dict(
        microbe = None, 
        amount = 'unit', # unit from [unit column]
        unit = None,
    )
    references = dict(
        microbe = dict(
            source = MDB.Microbes,
            property = MDB.Organism
        ), # reference to microbe data source
        amount = None,
        unit = None,
    )


class PasteurizationInputDto(BaseDto):
    PSFlow = fields.Nested(PSFlowTableDto, many=True)
    PSTemperature = fields.Nested(PSTemperatureTableDto, many=True)
    PSDensity = fields.Nested(PSDensityTableDto, many=True)
    HTInternalDiameter = fields.Nested(HTInternalDiameterTableDto, many=True)
    HTLength = fields.Nested(HTLengthTableDto, many=True)
    HeatExchangers = fields.Nested(PasteurizationDto, many=True)
    StartingMicrobes = fields.Nested(MicrobeDto, many=True)


class PasteurizationOutputDto(BaseDto):
    FinalMicrobes = fields.Nested(MicrobeUnitDto, many=True)


class PasteurizationModel(Model):
    @property
    def input_dto(self) -> type:
        return PasteurizationInputDto

    @property
    def output_dto(self) -> type:
        return PasteurizationOutputDto

    @property
    def ontology_imports(self) ->  List[Tuple[rdflib.URIRef, str]]:
        return [
            # ('http://microbe-hex-access-gateway:5020/api/Hex/ontology.ttl#', 'hdb'),
            (get_model_ontology_dependency('hex'), 'hdb'),
            # ('http://microbe-hex-access-gateway:5020/api/Microbes/ontology.ttl#', 'mdb')
            (get_model_ontology_dependency('microbe'), 'mdb')
        ]

    @property
    def description(self) -> str:
        return """Model that determines the decrease of microbe concentrations after a specified pasteurization process"""

    @property
    def price(self) -> float:
        return 4

    def run_model(self, input) -> Dict[str, List[dict]]:
        return self._calculate_pasteurisation(input)

    def _calculate_pasteurisation(self, input) -> Dict[str, List[dict]]:
        try:
            print("parsing data", file=sys.stderr)
            data = self._parse_data(input)
            print("parsed", data, file=sys.stderr)
            print("calculating", file=sys.stderr)
            result = self._calculate_microbe_content(data)
            print("calculated", result, file=sys.stderr)
            return result
        except Exception as ex:
            print(ex, file=sys.stderr)
            return dict(FinalMicrobes=[])


    # Parse the input data to an object used for the calculations
    # Input: all input data from the HTTP request
    # Output: Only the data that is needed for the calculation of the microbe content
    def _parse_data(self, input: PasteurizationInputDto):
        # Create the initial data object for the return
        # This object is extended everytime by using the **kwargs operation
        # data = {'microbe_type': microbe_type}
        data = dict(
            product_flow = input.PSFlow[0].product_flow,
            product_temperature = input.PSTemperature[0].product_temperature,
            product_density = input.PSDensity[0].product_density,

            holding_tube_diameter = input.HTInternalDiameter[0].holding_tube_internal_diameter,
            holding_tube_length = input.HTLength[0].holding_tube_length,

            hex_types = [int(hex.hex_type[-1]) for hex in input.HeatExchangers],
            hex_temps = [hex.outlet_temperature for hex in input.HeatExchangers],

            microbe_types = [m.microbe for m in input.StartingMicrobes],
            microbe_content_start = [m.amount for m in input.StartingMicrobes]
        )

        return data


    # based on provided pasteurisation model with heat exchange stages and ending in one holding stage
    def _calculate_microbe_content(self, data) -> list:
        # getting values from input object
        product_flow = data.get('product_flow') * 3600  # unit: 'kg/h'
        product_temperature = data.get('product_temperature')  # unit: 'Celsius'
        product_density = data.get('product_density')  # unit: 'kg/L'
        holding_tube_diameter = data.get('holding_tube_diameter')  # unit: 'mm'
        holding_tube_length = data.get('holding_tube_length')  # unit: 'm'
        microbe_types = data.get('microbe_types')
        microbe_content_start = [math.log10(mcs) for mcs in data.get('microbe_content_start')]  # unit: 'log CFU/mL'
        microbes_after_hex = microbe_content_start  # initialize microbe content

        final_microbes = list()
        for microbe_type, microbe_after_hex in zip(microbe_types, microbes_after_hex):
            starting_temperature = product_temperature  # initialize starting temperature
            # look up the microbial thermal death values for the specified microbe
            t_ref, z_val, log_d = self._lookup_microbe(microbe_type)

            # loop over each heat exchange stage
            for i in range(len(data.get('hex_types'))):
                # get the hex type and hex temperature
                hex_type = data.get('hex_types')[i]
                hex_temp = data.get('hex_temps')[i]
                # look up heat exchange type volume
                hex_volume = self._lookup_hex(hex_type)[0]
                # calculate residence time for heat exchanging stage
                residence_time_hex = self._calc_residence_time(hex_volume, product_flow, product_density)
                # calculate microbe content after heat exchange stage
                microbe_after_hex = self._calc_intermediate_microbe_content(100, microbe_after_hex, starting_temperature,
                                                                    hex_temp, t_ref, z_val, log_d, residence_time_hex)
                # update starting temperature for the next heat exchange stage
                starting_temperature = hex_temp

            # calculate holding tube volume based on its length and diameter
            holding_tube_volume = self._calc_holding_tube_volume(holding_tube_length, holding_tube_diameter)
            # calculate residence time for the holding stage
            residence_time_holding = self._calc_residence_time(holding_tube_volume, product_flow, product_density)

            # calculate the remaining microbes after each stage in the pasteurisation process
            microbe_after_holding = self._calc_intermediate_microbe_content(1, microbe_after_hex, hex_temp, hex_temp,
                                                                    t_ref, z_val, log_d, residence_time_holding)

            final_microbes.append(dict(
                microbe = microbe_type,
                amount = 10**microbe_after_holding, # log CFU/ml -> CFU/ml
                unit = 'CFU/ml'
            ))

        return dict(FinalMicrobes=final_microbes)


    def _calc_residence_time(self, volume, product_flow, product_density):
        # calculate residence time in seconds
        # unit of flow / density = (kg/h) / (kg/L) = (1/h) / (1/L) = L/h
        # then: volume / (flow / density) = m^3 / (L / h) = 1000 * dm^3 / (dm^3 / h) = (1000 * dm^3 * h) / dm^3 = 1000h
        # finally convert hours to seconds by multiplying by 3600 (seconds per hour)
        residence_time = volume / (product_flow / (product_density * 1000)) * 3600
        return residence_time


    def _calc_holding_tube_volume(self, holding_tube_length, holding_tube_diameter):
        # calculate volume using standard formula for volume of a cylinder (V = h * pi * r^2)
        # divide diameter by 1000 to go from mm to m and divide by 2 to get radius
        holding_tube_volume = math.pi * holding_tube_length * ((holding_tube_diameter / 1000 / 2) ** 2)
        return holding_tube_volume


    def _calc_intermediate_microbe_content(self, steps_precision, microbe_content_start, start_temperature, end_temperature,
                                        t_ref, z_val, log_d, residence_time):
        # set end microbes at the start to the starting value
        end_microbes = microbe_content_start

        for i in range(1, steps_precision + 1):
            # the temperature increases linearly with the number of steps precision
            temp_delta = (end_temperature - start_temperature) / steps_precision
            # the average temperature is calculated as the average of the beginning temperature and the ending temperature
            # temperatures per cycle or step basis
            average_temp = start_temperature + (temp_delta * i + temp_delta * (i - 1)) / 2
            # divide the total time in the respective phase by the number of steps precision
            time_delta = residence_time / steps_precision
            # the microbe value after a processing stage (or after a step in a stage)
            end_microbes = end_microbes - time_delta / 60 / (10 ** (log_d + (t_ref - average_temp) / z_val))

        return end_microbes


    # lookup table for hex type parameters
    # possibly parametrize in the future instead of by type to allow for custom values?
    def _lookup_hex(self, hex_type):
        # initialize return variables
        hex_volume = 0
        hex_area = 0
        hex_koverall = 0

        # set hex volume, area, and koverall based on hex type
        if hex_type == 1:
            hex_volume = 0.0000785398163397448
            hex_area = 0.00000246740110027234
            hex_koverall = 500
        elif hex_type == 2:
            hex_volume = 0.00015708
            hex_area = 0.00000493480220054468
            hex_koverall = 500
        elif hex_type == 3:
            hex_volume = 0.000392699
            hex_area = 0.0000123370055013617
            hex_koverall = 500
        elif hex_type == 4:
            hex_volume = 0.000392699
            hex_area = 0.0000123370055013617
            hex_koverall = 1000
        elif hex_type == 5:
            hex_volume = 0.000785398
            hex_area = 0.0000246740110027234
            hex_koverall = 500

        print("lookup hex", hex_type, [hex_volume, hex_area, hex_koverall], file=sys.stderr)
        return hex_volume, hex_area, hex_koverall


    # lookup table for microbial thermal death time values
    def _lookup_microbe(self, microbe):

        # initialize return values
        t_ref = 0
        z_val = 0
        log_d = 0

        # set the reference temperature, z-value, and logarithm of D-value
        if microbe == "E.coli":
            t_ref = 70
            z_val = 7
            log_d = -0.5
        elif microbe == "B.cereus":
            t_ref = 120
            z_val = 7
            log_d = -1
        elif microbe == "Salmonella":
            t_ref = 70
            z_val = 10
            log_d = -0.7
        elif microbe == "Listeria":
            t_ref = 70
            z_val = 10
            log_d = -1
        print("lookup microbe", microbe, [t_ref, z_val, log_d], file=sys.stderr)
        return t_ref, z_val, log_d