from flask import Blueprint, request
from pydantic import ValidationError

from app.middlewares.require_auth import token_required
from app.schemas.response import error_response, success_response
from app.schemas.user import UserDTO, UserLoginRequest, UserRegisterRequest
from app.services.auth_service import login_user, register_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_me(current_user):
    """Mendapatkan data profil user yang sedang login"""
    try:
        # current_user didapat dari middleware token_required
        user_dto = UserDTO.from_orm(current_user["_obj"])
        return success_response(
            data=user_dto.dict(), message="Data profil berhasil diambil"
        )
    except Exception as e:
        return error_response(message=f"Terjadi kesalahan: {str(e)}", status_code=500)


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        raw_data = request.get_json()
        register_data = UserRegisterRequest(**raw_data)
        success, message, user_dto = register_user(register_data)

        if success:
            return success_response(
                data=user_dto.dict(), message=message, status_code=201
            )
        else:
            return error_response(message=message, status_code=400)

    except ValidationError as e:
        return error_response(
            message="Validasi gagal", status_code=400, errors=e.errors()
        )
    except Exception as e:
        return error_response(message=f"Terjadi kesalahan: {str(e)}", status_code=500)


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        raw_data = request.get_json()
        login_data = UserLoginRequest(**raw_data)
        success, message, login_response_dto = login_user(login_data)

        if success:
            return success_response(
                data=login_response_dto.dict(), message=message, status_code=200
            )
        else:
            return error_response(message=message, status_code=401)

    except ValidationError as e:
        return error_response(
            message="Email atau password tidak valid",
            status_code=400,
            errors=e.errors(),
        )
    except Exception as e:
        return error_response(message=f"Terjadi kesalahan: {str(e)}", status_code=500)
