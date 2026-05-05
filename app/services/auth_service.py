import os
import psycopg2
import bcrypt
import jwt
from datetime import datetime, timedelta

def get_db_connection():
    """Membuat koneksi ke PostgreSQL"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME")
    )

def register_user(name, email, password):
    # 1. Mengacak password menggunakan bcrypt
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 2. Cek apakah email sudah terdaftar
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return False, "Email sudah terdaftar"

        # 3. Simpan user baru ke database
        cur.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
            (name, email, hashed_password)
        )
        conn.commit()
        return True, "Registrasi berhasil"
    except Exception as e:
        conn.rollback()
        return False, f"Terjadi kesalahan server: {str(e)}"
    finally:
        cur.close()
        conn.close()

def login_user(email, password):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 1. Cari user berdasarkan email
        cur.execute("SELECT id, name, password_hash FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if not user:
            return False, "Email atau password salah", None

        user_id, name, db_hashed_password = user

        # 2. Verifikasi password
        if bcrypt.checkpw(password.encode('utf-8'), db_hashed_password.encode('utf-8')):
            # 3. Jika cocok, buat JSON Web Token (JWT) yang berlaku selama 24 jam
            token_payload = {
                "user_id": str(user_id),
                "exp": datetime.utcnow() + timedelta(hours=24) # Token expired dalam 24 jam
            }
            # Ambil JWT_SECRET dari file .env
            token = jwt.encode(token_payload, os.getenv("JWT_SECRET"), algorithm="HS256")
            
            return True, "Login berhasil", {"token": token, "name": name}
        else:
            return False, "Email atau password salah", None
    finally:
        cur.close()
        conn.close()