import json, math
from typing import Dict, List, Tuple
from scipy import stats

from marshmallow import fields
import rdflib

from common_data_access.dtos import BaseDto, RunModelDtoSchema
from model_access_gateway.src.ingredient_store import get_ingredient_properties
from model_access_gateway.src.models.model import Model
from common_data_access import string_utils
from .model import get_model_ontology_dependency

import sys
from math import log, exp
from statistics import mean

OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')

class MeasurementsTableDto(BaseDto):
    wavelength = fields.Float() 
    log_attenuation = fields.Float()
    drop_size = fields.Float()
    run = fields.Integer()

    units = dict(
        wavelength = OM.nanometre,
        log_attenuation = None, #TODO add unit
        drop_size = None, #TODO add unit
        run = None
    )
    references = dict(
        wavelength = None,
        log_attenuation = None,
        drop_size = None,
        run = None
    )

class CalibrationDataTableDto(BaseDto):
    wavelength = fields.Float() 
    alpha = fields.Float()
    beta = fields.Float()
    sd_beta = fields.Integer()

    OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')

    units = dict(
        wavelength = OM.nanometre,
        alpha = None, #TODO add unit
        beta = None, #TODO add unit
        sd_beta = None #TODO add unit
    )
    references = dict(
        wavelength = None,
        alpha = None,
        beta = None,
        sd_beta = None
    )

class GeometricMeanTableDto(BaseDto):
    geometric_mean = fields.Float() 

    OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')

    units = dict(
        geometric_mean = None, #TODO add unit
    )
    references = dict(
        geometric_mean = None,
    )

class CalibrationInputDto(BaseDto):
    Measurements = fields.Nested(MeasurementsTableDto, many=True)


class CalibrationOutputDto(BaseDto):
    CalibrationData = fields.Nested(CalibrationDataTableDto, many=True)
    GeometricMean = fields.Nested(GeometricMeanTableDto, many=True)


class CalibrationModel(Model):
    @property
    def input_dto(self) -> type:
        return CalibrationInputDto

    @property
    def output_dto(self) -> type:
        return CalibrationOutputDto

    @property
    def ontology_imports(self) ->  List[Tuple[rdflib.URIRef, str]]:
        return []

    @property
    def description(self) -> str:
        return """Model that creates calibration data for droplet size determination, based on example data"""

    @property
    def price(self) -> float:
        return 16

    def run_model(self, input) -> Dict[str, List[dict]]:
        # geometric mean
        drop_sizes = list(map(lambda m: m.drop_size, 
            input.Measurements))
        geometric_mean_droplet_sizes = exp(mean(map(log, drop_sizes)))

        # calibration fit
        lambdas = set(map(lambda m: m.wavelength, input.Measurements))
        calibration_data = []

        for lambd_ in lambdas:
            lambda_measurements = filter(lambda m: m.wavelength == lambd_, input.Measurements)
            
            log_attenuation = list(map(lambda m: m.log_attenuation, lambda_measurements))
            log_normalized_dropsz = list(map(lambda m: m.drop_size / geometric_mean_droplet_sizes, 
                lambda_measurements))

            fit = stats.linregress(log_attenuation, log_normalized_dropsz)

            calibration_data.append(dict(
                wavelength=lambd_,
                alpha=fit.intercept,
                beta=fit.slope,
                sd_beta=fit.stderr
            ))
            
        return dict(
                CalibrationData = calibration_data,
                GeometricMean = [dict(geometric_mean = geometric_mean_droplet_sizes)]
            )

    