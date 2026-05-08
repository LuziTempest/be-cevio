from functools import wraps
from flask import request, jsonify
import jwt
import os

# Import fungsi koneksi dari auth_service yang sudah kamu buat sebelumnya
from app.services.auth_service import get_db_connection

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
            
            # 3. Cari user di database menggunakan Raw SQL
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("SELECT id, name, email FROM users WHERE id = %s", (data['user_id'],))
            user_data = cur.fetchone() # Mengambil 1 baris (tuple)
            
            cur.close()
            conn.close()

            # Jika hasil query kosong
            if not user_data:
                return jsonify({'error': 'User tidak valid atau sudah dihapus.'}), 401
            
            # 4. Ubah tuple menjadi dictionary agar mudah dipakai
            current_user = {
                "id": user_data[0],
                "name": user_data[1],
                "email": user_data[2]
            }
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Sesi login telah kedaluwarsa. Silakan login kembali.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token tidak valid atau telah dimanipulasi.'}), 401
        except Exception as e:
            return jsonify({'error': f'Terjadi kesalahan server: {str(e)}'}), 500
            
        # 5. Lempar dictionary current_user ke endpoint asli
        return f(current_user, *args, **kwargs)
        
    return decorated