from flask import Blueprint, request, jsonify
from app.services.auth_service import register_user, login_user

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
        return jsonify({"error": "Nama, email, dan password wajib diisi!"}), 400

    # Panggil service untuk registrasi
    success, message = register_user(name, email, password)
    
    if success:
        return jsonify({"message": message}), 201 # 201 Created
    else:
        return jsonify({"error": message}), 400 # 400 Bad Request

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email dan password wajib diisi!"}), 400

    success, message, result = login_user(email, password)
    
    if success:
        return jsonify({
            "message": message,
            "data": result # Berisi token dan nama user
        }), 200
    else:
        return jsonify({"error": message}), 401 # 401 Unauthorized