import json, math
from typing import List, Tuple

from marshmallow import fields
import rdflib

from common_data_access.dtos import BaseDto, RunModelDtoSchema
from model_access_gateway.src.ingredient_store import get_ingredient_properties
from model_access_gateway.src.models.model import Model
from common_data_access import string_utils

from math import log10 as log, exp

import sys

class PSWaterActivityTableDto(BaseDto):
    product_water_activity = fields.Float() 

    __OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')

    units = dict(
        product_water_activity = None,
    )
    references = dict(
        product_water_activity = None,
    )

class PSpHTableDto(BaseDto):
    product_pH = fields.Float() 

    __OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')

    units = dict(
        product_pH = __OM.Acidity,
    )
    references = dict(
        product_pH = None,
    )

class SCTemperatureTableDto(BaseDto):
    shelf_temperature = fields.Float() 

    __OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')

    units = dict(
        shelf_temperature = __OM.degreeCelcius,
    )
    references = dict(
        shelf_temperature = None,
    )

class SCTimeTableDto(BaseDto):
    shelf_time = fields.Float() 

    __OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')

    units = dict(
        shelf_time = __OM.day,
    )
    references = dict(
        shelf_time = None,
    )


class MicrobeDto(BaseDto):
    microbe = fields.Str() 
    amount = fields.Float() 

    __OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')
    __MDB = rdflib.Namespace('http://microbe-hex-access-gateway:5020/api/Microbes/ontology.ttl#')

    units = dict(
        microbe = None,
        amount = __OM.colonyFormingUnitPerMillilitre, # fixed unit (colonyFormingUnitPerMillilitre (no log!))
    )
    references = dict(
        microbe = dict(
            source = __MDB.Microbes,
            property = __MDB.Organism
        ), # reference to microbe data source
        amount = None,
    )


class MicrobeUnitDto(BaseDto):
    microbe = fields.Str()
    amount = fields.Float()
    unit = fields.Str() # in practice always [colonyFormingUnitPerMillilitre (no log!)]

    __MDB = rdflib.Namespace('http://microbe-hex-access-gateway:5020/api/Microbes/ontology.ttl#')

    units = dict(
        microbe = None, 
        amount = 'unit', # unit from [unit column]
        unit = None,
    )
    references = dict(
        microbe = dict(
            source = __MDB.Microbes,
            property = __MDB.Organism
        ), # reference to microbe data source
        amount = None,
        unit = None,
    )


class ShelflifeInputDto(BaseDto):
    PSWaterActivity = fields.Nested(PSWaterActivityTableDto, many=True)
    PSpH = fields.Nested(PSpHTableDto, many=True)
    SCTemperature = fields.Nested(SCTemperatureTableDto, many=True)
    SCTime = fields.Nested(SCTimeTableDto, many=True)
    StartingMicrobes = fields.Nested(MicrobeDto, many=True)


class ShelflifeOutputDto(BaseDto):
    FinalMicrobes = fields.Nested(MicrobeUnitDto, many=True)


class ShelflifeModel(Model):
    @property
    def input_dto(self) -> type:
        return ShelflifeInputDto

    @property
    def output_dto(self) -> type:
        return ShelflifeOutputDto

    @property
    def ontology_imports(self) ->  List[Tuple[rdflib.URIRef, str]]:
        return [
            ('http://microbe-hex-access-gateway:5020/api/Hex/ontology.ttl#', 'hdb'),
            ('http://microbe-hex-access-gateway:5020/api/Microbes/ontology.ttl#', 'mdb')
        ]

    @property
    def description(self) -> str:
        return """Model that determines the decrease of microbe concentrations after a specified shelf life conditions"""

    @property
    def price(self) -> float:
        return 4.2

    def run_model(self, input) -> list:
        return self._calculate_shelflife(input)

    def _calculate_shelflife(self, input) -> list:
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
            return [dict(FinalMicrobes=[])]


    # Parse the input data to an object used for the calculations
    # Input: all input data from the HTTP request
    # Output: Only the data that is needed for the calculation of the microbe content
    def _parse_data(self, input: ShelflifeInputDto):
        # Create the initial data object for the return
        # This object is extended everytime by using the **kwargs operation
        # data = {'microbe_type': microbe_type}
        data = dict(
            product_water_activity = input.PSWaterActivity[0].product_water_activity,
            product_pH = input.PSpH[0].product_pH,

            shelf_temperature = input.SCTemperature[0].shelf_temperature,
            shelf_time = input.SCTime[0].shelf_time,

            microbe_types = [m.microbe for m in input.StartingMicrobes],
            microbe_content_start = [m.amount for m in input.StartingMicrobes]
        )

        return data


    # based on provided pasteurisation model with heat exchange stages and ending in one holding stage
    def _calculate_microbe_content(self, data) -> list:
        # getting values from input object
        product_water_activity = data.get('product_water_activity')  # unit: '1/h'
        product_pH = data.get('product_pH')  # unit: 'pH (Acidity)'
        shelf_temperature = data.get('shelf_temperature')  # unit: 'C'
        shelf_time = data.get('shelf_time')  # unit: 'days'
        microbe_types = data.get('microbe_types')
        microbes_content_start = [log(mcs) for mcs in data.get('microbe_content_start')]  # unit: 'log CFU/mL'

        final_microbes = list()
        for microbe_type, microbe_content_start in zip(microbe_types, microbes_content_start):
            # look up the microbial thermal death values for the specified microbe
            mu_max, Tmin, Topt, Tmax, \
                pHmin, pHopt, pHmax, \
                awmin, awopt = self._lookup_microbe(microbe_type)

            T_gamma = 0 if shelf_temperature < Tmin or shelf_temperature > Tmax \
                else ((shelf_temperature-Tmin)/(Topt-Tmin))**2

            pH_gamma = 0 if product_pH < pHmin or product_pH > pHmax \
                else ((product_pH-pHmin)/(pHopt-pHmin))*((pHmax-product_pH)/(pHmax-pHopt))
            
            aw_gamma = 0 if product_water_activity < awmin \
                else (product_water_activity-awmin)/(awopt-awmin)

            mu = mu_max * T_gamma * pH_gamma * aw_gamma

            logNmax = 8 # log CFU/ml
            logN0 = (microbe_content_start - logNmax * exp(-exp(1))) \
                / (1 - exp(-exp(1)))
            lag = 1 # days

            logNt = ((logNmax-logN0)
                    / log(exp(1))
                    * exp(-exp(
                        mu*24*exp(1)*min(0,(lag-shelf_time))
                        / ((logNmax-logN0)/log(exp(1)))+1))
                    * log(exp(1))) \
                + logN0

            final_microbes.append(dict(
                microbe = microbe_type,
                amount = 10**logNt, # log CFU/ml -> CFU/ml
                unit = 'CFU/ml'
            ))

        return dict(FinalMicrobes=final_microbes)


    # lookup table for microbial thermal death time values
    def _lookup_microbe(self, microbe):

        # initialize return values
        #  mu_max, Tmin, Topt, Tmax, pHmin, pHopt, pHmax, awmin, awopt
        lookup = {
            "E.coli":     [2, 10,32,40, 4.5,7.0,8.0, 0.92,1],
            "B.cereus":   [2, 10,32,50, 4.5,6.5,9.0, 0.90,1],
            "Salmonella": [2, 10,32,45, 4.0,6.5,9.0, 0.90,1],
            "Listeria":   [2,  4,37,45, 4.0,7.0,9.5, 0.90,1]
        }
        
        if microbe in lookup:
            print("lookup microbe", microbe, lookup[microbe], file=sys.stderr)
            return lookup[microbe]
        else:
            print("lookup microbe", microbe, [0, 0,0,0, 0,0,0, 0,0], file=sys.stderr)
            return [0, 0,0,0, 0,0,0, 0,0]