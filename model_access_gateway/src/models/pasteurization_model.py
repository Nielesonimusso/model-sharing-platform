import json
from typing import List, Tuple

from marshmallow import fields
import rdflib

from common_data_access.dtos import BaseDto, RunModelDtoSchema
from model_access_gateway.src.ingredient_store import get_ingredient_properties
from model_access_gateway.src.models.model import Model

class PSPropertyTableDto(BaseDto):
    property = fields.Str() 
    value = fields.Float() 

    __ROOT = rdflib.Namespace('#')
    __OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')

    units = dict(
        property = None,
        value = dict( # TODO handle dict unit in ttl generation
            source = __ROOT.Property,
            property = __ROOT.unit
        ), # unit based on property.unit (coming from concept reference)
    )
    references = dict(
        property = dict(
            source = __ROOT.Property,
            property = __ROOT.name,
            objects = list( #TODO handle objects in ttl generation
                dict(
                    name="Flow",
                    unit=__OM["kilogramPerSecond-Time"]
                ),dict(
                    name="Temperature",
                    unit=__OM.degreeCelsius
                ),dict(
                    name="Density",
                    unit=__OM.kilogramPerLitre
                )
            )
        ), # reference to in-ontology concept
        value = None,
    )


class HTPropertyTableDto(BaseDto):
    property = fields.Str() 
    value = fields.Float() 

    __ROOT = rdflib.Namespace('#')
    __OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')

    units = dict(
        property = None,
        value = dict( # TODO handle dict unit in ttl generation
            source = __ROOT.Property,
            property = __ROOT.unit
        ), # unit based on property.unit (coming from concept reference)
    )
    references = dict(
        property = dict(
            source = __ROOT.Property,
            property = __ROOT.name,
            objects = list( #TODO handle objects in ttl generation
                dict(
                    name="Internal Diameter",
                    unit=__OM.millimetre
                ),dict(
                    name="Length",
                    unit=__OM.metre
                )
            )
        ), # reference to in-ontology concept
        value = None,
    )


class PasteurizationDto(BaseDto):
    hex_type = fields.Str() 
    outlet_temperature =  fields.Float() 

    __OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')
    __HDB = rdflib.Namespace('http://microbe-hex-access-gateway:5020/api/Hex/ontology.ttl#')

    units = dict(
        hex_type = None,
        outlet_temperature = __OM.degreeCelsius, # fixed unit (degrees C)
    )
    references = dict(
        hex_type = dict(
            source = __HDB.Hex,
            property = __HDB.Type
        ), # reference to hex types data source
        outlet_temperature = None,
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


class PasteurizationInputDto(BaseDto):
    ProductStreamProperties = fields.Nested(PSPropertyTableDto, many=True)
    HoldingTubeProperties = fields.Nested(HTPropertyTableDto, many=True)
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
            ('http://microbe-hex-access-gateway:5020/api/Hex/ontology.ttl#', 'hdb'),
            ('http://microbe-hex-access-gateway:5020/api/Microbes/ontology.ttl#', 'mdb')
        ]

    @property
    def description(self) -> str:
        return """Model that determines the decrease of microbe concentrations after a specified pasteurization process"""

    @property
    def price(self) -> float:
        return 4

    def run_model(self, input) -> list:
        # TODO change with pasteurization implementation
        pass