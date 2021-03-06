import json, math
from typing import Dict, List, Tuple
import numpy as np

from marshmallow import fields
import rdflib

from common_data_access.dtos import BaseDto, RunModelDtoSchema
from model_access_gateway.src.ingredient_store import get_ingredient_properties
from model_access_gateway.src.models.model import Model
from common_data_access import string_utils
from .model import get_model_ontology_dependency

from math import log

import sys

OM = rdflib.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')

class MeasurementsTableDto(BaseDto):
    wavelength = fields.Float() 
    log_attenuation = fields.Float()
    run = fields.Integer()

    units = dict(
        wavelength = OM.nanometre,
        log_attenuation = OM.one,
        run = None
    )
    references = dict(
        wavelength = None,
        log_attenuation = None,
        run = None
    )

class CalibrationDataTableDto(BaseDto):
    wavelength = fields.Float() 
    alpha = fields.Float()
    beta = fields.Float()
    sd_beta = fields.Float()

    units = dict(
        wavelength = OM.nanometre,
        alpha = OM.one,
        beta = OM.one,
        sd_beta = OM.one
    )
    references = dict(
        wavelength = None,
        alpha = None,
        beta = None,
        sd_beta = None
    )

class GeometricMeanTableDto(BaseDto):
    geometric_mean = fields.Float() 

    units = dict(
        geometric_mean = OM.micrometre
    )
    references = dict(
        geometric_mean = None,
    )

class DropletSizeTableDto(BaseDto):
    run = fields.Integer()
    drop_size = fields.Float() 

    units = dict(
        run = None,
        drop_size = None #TODO add unit
    )
    references = dict(
        run = None,
        drop_size = None 
    )


class DropletSizeInputDto(BaseDto):
    CalibrationData = fields.Nested(CalibrationDataTableDto, many=True)
    GeometricMean = fields.Nested(GeometricMeanTableDto, many=True)
    Measurements = fields.Nested(MeasurementsTableDto, many=True)


class DropletSizeOutputDto(BaseDto):
    DropletSizes = fields.Nested(DropletSizeTableDto, many=True)


class DropletSizeModel(Model):
    @property
    def input_dto(self) -> type:
        return DropletSizeInputDto

    @property
    def output_dto(self) -> type:
        return DropletSizeOutputDto

    @property
    def ontology_imports(self) ->  List[Tuple[rdflib.URIRef, str]]:
        return []

    @property
    def description(self) -> str:
        return """Model that estimates the droplet sizes inside an emulsion."""

    @property
    def price(self) -> float:
        return 2

    def run_model(self, input) -> Dict[str, List[dict]]:

        model = sorted(input.CalibrationData, key=lambda cd: cd.wavelength)
        model_lambdas = np.fromiter(map(lambda mdl: mdl.wavelength, model), dtype=np.int32)
        model_alphas = np.fromiter(map(lambda mdl: mdl.alpha, model), dtype=np.float64)
        model_betas = np.fromiter(map(lambda mdl: mdl.beta, model), dtype=np.float64)
        model_sd_betas = np.fromiter(map(lambda mdl: mdl.sd_beta, model), dtype=np.float64)

        scale = input.GeometricMean[0].geometric_mean

        runs = set(map(lambda m: m.run, input.Measurements))

        droplet_sizes = []

        for run in runs:
            measurements_at_run = list(sorted(
                filter(lambda m: m.run == run, input.Measurements),
                key=lambda m: m.wavelength))
            lambdas = np.fromiter(map(lambda m: m.wavelength, measurements_at_run), dtype=np.float64)
            logA = np.fromiter(map(lambda m: m.log_attenuation, measurements_at_run), dtype=np.float64)

            interp_alpha = np.interp(lambdas, model_lambdas, model_alphas)
            interp_beta = np.interp(lambdas, model_lambdas, model_betas)
            interp_sd_beta = np.exp(np.interp(lambdas, model_lambdas, np.log(model_sd_betas)))

            normalized_residue = (logA - interp_alpha)/interp_sd_beta
            normalized_beta = interp_beta/interp_sd_beta

            L = np.dot(normalized_residue, normalized_beta)/np.dot(normalized_beta, normalized_beta)
            dropsz = scale * np.exp(L)

            droplet_sizes.append(dict(
                run = run,
                drop_size = dropsz
            ))
            
        return dict(
            DropletSizes=droplet_sizes
        )

    