from datetime import datetime

import requests
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, current_user
from werkzeug.exceptions import abort

from common_data_access.dtos import IngredientInfoDtoSchema
from common_data_access.json_extension import get_json
from model_sharing_backend.src.models.food_product_models import FoodProduct, FoodProductPermissionDtoSchema, \
    FoodProductPermission

products_bp = Blueprint('Products', __name__)


@products_bp.route('/products', methods=['GET'])
@jwt_required
def get_all_products():
    """
    Get all accessible products.
    ---
    tags:
        -   Product
    security:
        - bearer: []
    responses:
        200:
            description: A list of all products.
            schema:
                type: array
                items:
                    $ref: '#/definitions/FoodProductDb'
    """
    return get_json(FoodProduct.query.get_all_accessible_by(current_user.company_id), FoodProduct.FoodProductDbSchema)


@products_bp.route('/own_products', methods=['GET'])
@jwt_required
def get_own_products():
    """
    Get all products owned by logged in users organization
    ---
    tags:
        -   Product
    security:
        - bearer: []
    responses:
        200:
            description: A list of all owned products.
            schema:
                type: array
                items:
                    $ref: '#/definitions/FoodProductDb'
    """
    return get_json(FoodProduct.query.get_all_owned_by(current_user.company_id), FoodProduct.FoodProductDbSchema)


@products_bp.route('/product/<product_id>', methods=['GET'])
@jwt_required
def get_product(product_id: str):
    """
    Get a product by id
    ---
    tags:
        -   Product
    security:
        - bearer: []
    parameters:
        -   name: product_id
            in: path
            description: id of the product to fetch
            required: true
            type: string
    responses:
        200:
            description: Product with specified id or null if id not matched
            schema:
                $ref: '#/definitions/FoodProductDb'
        404:
            description: Product with this ID does not exist or not visible to current user
    """
    return get_json(
        FoodProduct.query.get_accessible_or_404(current_user.company_id, product_id), FoodProduct.FoodProductDbSchema)


@products_bp.route('/product/<product_id>', methods=['DELETE'])
@jwt_required
def delete_product(product_id: str):
    """
    Remove product by id from DB
    ---
    tags:
        -   Product
    security:
        - bearer: []
    responses:
        200:
            description: Successfully removed product
        404:
            description: Product with this ID does not exist
        400:
            description: Product already used in simulation
    parameters:
        -   name: product_id
            in: path
            description: id of the product to remove
            required: true
            type: string
    """
    food_product = FoodProduct.query.get_created_by_or_404(current_user.id, product_id)
    if len(food_product.used_in_simulations or []):
        abort(400, description='food product already used in simulation')
    food_product.delete()
    return {}


@products_bp.route('/product', methods=['POST'])
@jwt_required
def create_product():
    """
    Create a new product
    ---
    tags:
        -   Product
    security:
        - bearer: []
    parameters:
        -   name: product
            in: body
            description: Product properties
            schema:
                $ref: '#/definitions/FoodProductDb'
    responses:
        201:
            description: Successfully created product
            schema:
                $ref: '#/definitions/FoodProductDb'
    """
    food_product = FoodProduct.FoodProductDbSchema().load(request.json)
    food_product.created_on = datetime.utcnow()
    food_product.created_by = current_user
    food_product.owner = current_user.company
    return get_json(food_product.add(), FoodProduct.FoodProductDbSchema), 201


@products_bp.route('/product/<product_id>', methods=['PUT'])
@jwt_required
def update_product(product_id: str):
    """
    Update existing product
    ---
    tags:
        -   Product
    security:
        - bearer: []
    parameters:
        -   name: product_id
            in: path
            description: Product id
            schema:
                type: string
        -   name: product
            in: body
            description: Product properties
            schema:
                $ref: '#/definitions/FoodProductDb'
    responses:
        200:
            description: Successfully updated product
            schema:
                $ref: '#/definitions/FoodProductDb'
        404:
            description: product not found or not editable to current user
    """
    food_product_db = FoodProduct.query.get_created_by_or_404(current_user.id, product_id)
    food_product_new = FoodProduct.FoodProductDbSchema().load(request.json)
    food_product_db.name = food_product_new.name
    food_product_db.company_code = food_product_new.company_code
    food_product_db.standard_code = food_product_new.standard_code
    food_product_db.dosage = food_product_new.dosage
    food_product_db.dosage_unit = food_product_new.dosage_unit
    food_product_db.food_product_properties = food_product_new.food_product_properties
    food_product_db.ingredients = food_product_new.ingredients
    food_product_db.processing_steps = food_product_new.processing_steps
    food_product_db.packagings = food_product_new.packagings
    return get_json(food_product_db.update(), FoodProduct.FoodProductDbSchema)


@products_bp.route('/product/ingredients', methods=['GET'])
@jwt_required
def get_all_product_ingredients():
    """
    Get all ingredients that might be needed to create product recipe
    ---
    tags:
        -   Product
    security:
        - bearer: []
    responses:
        200:
            description: List of ingredients
            schema:
                type: array
                items:
                    $ref: '#/definitions/IngredientInfoDto'
    """
    ingredient_service_url = f'{current_app.config["INGREDIENT_SERVICE_URL"]}/api/get_all_ingredients'
    result = requests.get(ingredient_service_url)
    return get_json(result.json(), IngredientInfoDtoSchema)


@products_bp.route('/product/permissions/<product_id>', methods=['PUT'])
@jwt_required
def set_product_permissions(product_id: str):
    """
    Set access permissions for the food product
    ---
    tags:
        -   Product
    security:
        - bearer: []
    parameters:
        -   name: product_id
            in: path
            description: id of the food product
            required: true
            schema:
                type: string
        -   name: permissions
            in: body
            description: list of company ids
            required: true
            schema:
                type: array
                items:
                    type: string
    responses:
        200:
            description: permissions successfully saved
            schema:
                type: array
                items:
                    $ref: '#/definitions/FoodProductPermissionDto'
        404:
            description: food product not found or not editable to current user
    """
    company_ids = request.json or []
    food_product = FoodProduct.query.get_one_created_by_where_or_404(current_user.id, FoodProduct.id == product_id)
    food_product.permissions = []
    for company_id in set(company_ids):
        food_product.permissions.append(FoodProductPermission(company_id=company_id, food_product_id=food_product.id))
    food_product.save()
    return get_json(food_product.permissions, FoodProductPermissionDtoSchema)


@products_bp.route('/product/permissions/<product_id>', methods=['GET'])
@jwt_required
def get_product_permissions(product_id: str):
    """
    Get permissions for the food product
    ---
    tags:
        -   Product
    security:
        - bearer: []
    parameters:
        -   name: product_id
            in: path
            description: id of the food product
            required: true
            schema:
                type: string
    responses:
        200:
            description: list of permissions for food product
            schema:
                type: array
                items:
                    $ref: '#/definitions/FoodProductPermissionDto'
        404:
            description: food product not found or not owned by current user's organization
    """
    return get_json(FoodProduct.query.get_owned_or_404(current_user.company_id, product_id).permissions,
                    FoodProductPermissionDtoSchema)
