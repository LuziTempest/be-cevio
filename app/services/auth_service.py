import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from flask import current_app

from app.extensions import db
from app.models.users import User
from app.schemas.user import LoginResponseDTO, UserDTO, UserLoginRequest, UserRegisterRequest


def register_user(register_data: UserRegisterRequest):
    """Mendaftarkan user baru menggunakan data dari DTO"""
    # Hash password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(
        register_data.password.encode("utf-8"), salt
    ).decode("utf-8")

    try:
        # Cek apakah email sudah ada
        existing_user = User.query.filter_by(email=register_data.email).first()
        if existing_user:
            return False, "Email sudah terdaftar", None

        # Simpan user baru
        new_user = User(
            name=register_data.name,
            email=register_data.email,
            password_hash=hashed_password,
        )
        db.session.add(new_user)
        db.session.commit()

        # Kembalikan UserDTO
        return True, "Registrasi berhasil", UserDTO.from_orm(new_user)
    except Exception as e:
        db.session.rollback()
        return False, f"Terjadi kesalahan server: {str(e)}", None


def login_user(login_data: UserLoginRequest):
    """Proses login user menggunakan data dari DTO"""
    try:
        user = User.query.filter_by(email=login_data.email).first()

        if not user:
            return False, "Email atau password salah", None

        # Verifikasi password
        if bcrypt.checkpw(
            login_data.password.encode("utf-8"), user.password_hash.encode("utf-8")
        ):
            # Generate JWT Token
            token_payload = {
                "user_id": user.id,
                "exp": datetime.now(timezone.utc) + timedelta(hours=24),
            }
            
            # Menggunakan SECRET_KEY dari config aplikasi
            secret = current_app.config.get("SECRET_KEY")
            token = jwt.encode(
                token_payload, secret, algorithm="HS256"
            )

            # Buat LoginResponseDTO
            response_data = LoginResponseDTO(token=token, user=UserDTO.from_orm(user))

            return True, "Login berhasil", response_data
        else:
            return False, "Email atau password salah", None

    except Exception as e:
        return False, f"Terjadi kesalahan saat login: {str(e)}", None
