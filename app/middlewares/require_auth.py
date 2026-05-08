from functools import wraps
from flask import request, jsonify
import jwt
import os

# Import Model dan Schema (ORM)
# Catatan: Jika kamu merename file modelnya jadi user.py, ubah tulisan 'users' di bawah menjadi 'user'
from app.models.users import User 
from app.schemas.user import user_schema

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 1. Ekstrak token dari Header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]
        
        if not token:
            return jsonify({'error': 'Akses ditolak! Token otentikasi tidak ditemukan.'}), 401
        
        try:
            # 2. Decode token
            data = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=["HS256"])
            
            # 3. Cari user di database menggunakan ORM (berdasarkan Primary Key / ID)
            user_obj = User.query.get(data['user_id'])
            
            # Jika hasil query kosong (user sudah dihapus dari DB tapi token masih ada)
            if not user_obj:
                return jsonify({'error': 'User tidak valid atau sudah dihapus.'}), 401
            
            # 4. Format objek ORM menjadi dictionary menggunakan schema yang sudah dibuat
            current_user = user_schema(user_obj)
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Sesi login telah kedaluwarsa. Silakan login kembali.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token tidak valid atau telah dimanipulasi.'}), 401
        except Exception as e:
            return jsonify({'error': f'Terjadi kesalahan server: {str(e)}'}), 500
            
        # 5. Lempar dictionary current_user ke endpoint asli
        return f(current_user, *args, **kwargs)
        
    return decorated