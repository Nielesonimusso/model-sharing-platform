import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required

from model_sharing_backend.src.models.user import UserLoginDtoSchema, User, UserAPIDtoSchema

auth_bp = Blueprint('Auth', __name__)


@auth_bp.route('/auth_token', methods=['POST'])
def auth_token():
    """
    Create auth token for user
    ---
    tags:
        -   Authorization
    parameters:
        -   name: user_details
            in: body
            description:
            required: true
            schema:
                $ref: '#/definitions/UserLoginDto'
    responses:
        200:
            description: authentication successful. Returns the authentication token
            schema:
                type: string
        401:
            description: authentication failed
    """
    user_login = UserLoginDtoSchema().load(request.json)
    user = User.query.filter_by(username=user_login.username).one_or_none()
    if user is not None and user_login.password is not None \
            and bcrypt.checkpw(user_login.password.encode(), user.password_hash):
        token = create_access_token(identity={'username': user_login.username})
        return jsonify(token), 200
    else:
        return jsonify(), 401

@auth_bp.route('/api_token', methods=['POST'])
def api_token():
    """
    create auth token based on provided api key

    """
    api_key = UserAPIDtoSchema().load(request.json)
    user = User.query.filter_by(api_key=api_key.api_key).one_or_none()
    if user is not None:
        token = create_access_token(identity={'username': user.username})
        return jsonify(token), 200
    else:
        return jsonify(), 401


@auth_bp.route('/check_auth', methods=['GET'])
@jwt_required
def check_authentication():
    """
    Check if current user has valid authentication
    ---
    security:
        - bearer: []
    tags:
        -   Authorization
    responses:
        200:
            description: authorization valid
        401:
            description: authentication failed
    """
    return jsonify(), 200
