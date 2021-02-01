from flask import Blueprint

from common_data_access.json_extension import get_json
from model_sharing_backend.src.models.company import Company, CompanyDtoSchema

company_bp = Blueprint('Companies', __name__)


@company_bp.route('/companies', methods=['GET'])
def get_all_companies():
    """
    Get all registered companies
    ---
    tags:
        -   Company
    responses:
        200:
            description: List of companies
            schema:
                type: array
                items:
                    $ref: '#/definitions/CompanyDto'
    """
    return get_json(Company.query.get_all(), CompanyDtoSchema)
