import uuid
from datetime import datetime, timedelta

import bcrypt
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from werkzeug.exceptions import abort

from common_data_access.json_extension import get_json
from model_sharing_backend.src.models.user import User, UserProfileDtoSchema, UserRegistrationDtoSchema, \
    UserProfileUpdateDtoSchema, ChangePasswordDtoSchema, PasswordReset, PasswordResetDtoSchema
from model_sharing_backend.src.utils.email_client import send_reset_password_email

user_bp = Blueprint('Users', __name__)


@user_bp.route('/own_profile', methods=['GET'])
@jwt_required
def get_own_profile():
    """
    Get profile of current user
    ---
    tags:
        -   User
    security:
        - bearer: []
    responses:
        200:
            description: User profile information
            schema:
                $ref: '#/definitions/UserProfileDto'
        401:
            description: User not authenticated
    """
    return get_json(current_user, UserProfileDtoSchema)


@user_bp.route('/own_profile', methods=['PUT'])
@jwt_required
def update_own_profile():
    """
    Update current user's profile. Only email and full name are updated.
    ---
    tags:
        -   User
    security:
        - bearer: []
    parameters:
        -   name: profile
            in: body
            description: updated profile info
            required: true
            schema:
                $ref: '#/definitions/UserProfileUpdateDto'
    responses:
        200:
            description: profile updated
            schema:
                $ref: '#/definitions/UserProfileDto'
        400:
            description: Email already in use
    """
    updated_profile = UserProfileUpdateDtoSchema().load(request.json)
    saved_user = User.query.get_one_where(User.username == current_user.username)
    if len(User.query.get_where(User.username != saved_user.username, User.email == updated_profile.email)) > 0:
        abort(400, description='email already in use')
    saved_user.full_name = updated_profile.full_name
    saved_user.email = updated_profile.email
    return get_json(saved_user.save(), UserProfileDtoSchema)


@user_bp.route('/user/register', methods=['POST'])
def register_user():
    """
    Register new user
    ---
    tags:
        -   User
    parameters:
        -   name: user_details
            in: body
            description: user information
            required: true
            schema:
                $ref: '#/definitions/UserRegistrationDto'
    responses:
        200:
            description: Registered successfully
        400:
            description: registration failed
            schema:
                type: object
                properties:
                    reason:
                        type: string
    """
    user_reg = UserRegistrationDtoSchema().load(request.json)
    user_with_same_email = User.query.filter_by(email=user_reg.email).one_or_none()
    user_with_same_username = User.query.filter_by(username=user_reg.username).one_or_none()
    if user_with_same_email is None and user_with_same_username is None and user_reg.password:
        user = User(username=user_reg.username, full_name=user_reg.full_name, email=user_reg.email,
                    password_hash=bcrypt.hashpw(user_reg.password.encode(), bcrypt.gensalt()),
                    company_id=user_reg.company_id, api_key=str(uuid.uuid4()))
        user.add()
        return jsonify(), 200
    else:
        return jsonify({'reason': f'Username: {user_reg.username} and/or Email:{user_reg.email} already taken.'}), 400


@user_bp.route('/user/change_password', methods=['POST'])
@jwt_required
def change_password():
    """
    Change password
    ---
    tags:
        -   User
    security:
        - bearer: []
    parameters:
        -   name: change_password
            in: body
            required: true
            schema:
                $ref: '#/definitions/ChangePasswordDto'
    responses:
        200:
            description: password changed successfully
        400:
            description: invalid data (e.g. current password not match, password length less than 6)
    """
    password_change = ChangePasswordDtoSchema().load(request.json)
    user = User.query.filter_by(username=current_user.username).one_or_none()
    if user is not None and bcrypt.checkpw(password_change.current_password.encode(), user.password_hash):
        user.password_hash = bcrypt.hashpw(password_change.new_password.encode(), bcrypt.gensalt())
        user.save()
        return {}
    else:
        return {}, 400


@user_bp.route('/user/request_password_reset', methods=['POST'])
def request_password_reset_code():
    """
    Send a reset password code to users email address
    ---
    tags:
        -   User
    parameters:
        -   name: email
            in: body
            description: valid email
            required: true
            schema:
                type: string
    responses:
        200:
            description: reset email sent
        404:
            description: email/user not found
    """
    user = User.query.filter_by(email=request.data.decode()).first_or_404()
    password_reset = PasswordReset(user=user, created_on=datetime.utcnow(), reset_code=str(uuid.uuid4()), is_used=False)
    password_reset.save()
    send_reset_password_email(user.email, user.full_name, password_reset.reset_code)
    return {}


@user_bp.route('/user/reset_password', methods=['POST'])
def reset_password():
    """
    Set new password
    ---
    tags:
        -   User
    parameters:
        -   name: password_reset
            in: body
            required: true
            schema:
                $ref: '#/definitions/PasswordResetDto'
    responses:
        200:
            description: password reset successful
        404:
            description: no match found for provided information or expired
    """
    last_request_time = datetime.utcnow() - timedelta(minutes=15)
    password_reset_dto = PasswordResetDtoSchema().load(request.json)
    password_reset = PasswordReset.query.filter(PasswordReset.is_used == False,
                                                PasswordReset.reset_code == password_reset_dto.reset_code,
                                                PasswordReset.user.has(email=password_reset_dto.email),
                                                PasswordReset.created_on > last_request_time).first_or_404()
    password_reset.is_used = True
    password_reset.user.password_hash = bcrypt.hashpw(password_reset_dto.new_password.encode(), bcrypt.gensalt())
    password_reset.save()
    return {}
