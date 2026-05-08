import os
import bcrypt
import jwt
from datetime import datetime, timedelta

# Import objek db dan Model User untuk ORM
from app.extensions import db
from app.models.users import User

def register_user(name, email, password):
    # 1. Mengacak password menggunakan bcrypt
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    try:
        # 2. Cek apakah email sudah terdaftar menggunakan ORM
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return False, "Email sudah terdaftar"

        # 3. Simpan user baru ke database menggunakan ORM
        new_user = User(name=name, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return True, "Registrasi berhasil"
    except Exception as e:
        db.session.rollback() # Sangat penting untuk mencegah database terkunci saat terjadi error
        return False, f"Terjadi kesalahan server: {str(e)}"

def login_user(email, password):
    try:
        # 1. Cari user berdasarkan email menggunakan ORM
        user = User.query.filter_by(email=email).first()

        # Cek apakah user ada
        if not user:
            return False, "Email atau password salah", None

        # 2. Verifikasi password (ambil atribut password_hash langsung dari objek user)
        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            # 3. Jika cocok, buat JSON Web Token (JWT) yang berlaku selama 24 jam
            token_payload = {
                "user_id": str(user.id),
                "exp": datetime.utcnow() + timedelta(hours=24) # Token expired dalam 24 jam
            }
            # Ambil JWT_SECRET dari file .env
            token = jwt.encode(token_payload, os.getenv("JWT_SECRET"), algorithm="HS256")
            
            # Kita kembalikan objek 'user' utuh agar nanti bisa diformat oleh schema di controller/routes
            return True, "Login berhasil", {"token": token, "user": user}
        else:
            return False, "Email atau password salah", None
            
    except Exception as e:
        return False, f"Terjadi kesalahan saat login: {str(e)}", None