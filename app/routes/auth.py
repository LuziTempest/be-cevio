from flask import Blueprint, request
from app.services.auth_service import register_user, login_user

# IMPORT SCHEMAS
from app.schemas.response import success_response, error_response
from app.schemas.user import user_schema

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    # Mengambil data JSON dari request body
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # Validasi input sederhana
    if not name or not email or not password:
        return error_response(message="Nama, email, dan password wajib diisi!", status_code=400)

    # Panggil service untuk registrasi
    success, message = register_user(name, email, password)
    
    if success:
        return success_response(message=message, status_code=201) # 201 Created
    else:
        return error_response(message=message, status_code=400) # 400 Bad Request

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return error_response(message="Email dan password wajib diisi!", status_code=400)

    # Panggil service untuk login
    success, message, result = login_user(email, password)
    
    if success:
        # 1. result['user'] adalah Objek Model dari ORM, format dulu pakai schema
        formatted_user = user_schema(result['user'])
        
        # 2. Gabungkan token dan user yang sudah diformat menjadi dictionary
        response_data = {
            "token": result['token'],
            "user": formatted_user
        }
        
        # 3. Kembalikan dengan format response standar
        return success_response(data=response_data, message=message, status_code=200)
    else:
        return error_response(message=message, status_code=401) # 401 Unauthorized