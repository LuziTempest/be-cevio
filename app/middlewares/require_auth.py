from functools import wraps

import jwt
from flask import current_app, jsonify, request

from app.models.users import User
from app.schemas.user import user_schema


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]

        if not token:
            return jsonify(
                {"error": "Akses ditolak! Token otentikasi tidak ditemukan."}
            ), 401

        try:
            secret = current_app.config.get("SECRET_KEY")
            data = jwt.decode(token, secret, algorithms=["HS256"])

            user_obj = User.query.get(data["user_id"])
            if not user_obj:
                return jsonify({"error": "User tidak valid atau sudah dihapus."}), 401

            current_user = user_schema(user_obj)
            current_user["_obj"] = user_obj

        except jwt.ExpiredSignatureError:
            return jsonify(
                {"error": "Sesi login telah kedaluwarsa. Silakan login kembali."}
            ), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token tidak valid atau telah dimanipulasi."}), 401
        except Exception as e:
            return jsonify({"error": f"Terjadi kesalahan server: {str(e)}"}), 500

        return f(current_user, *args, **kwargs)

    return decorated
