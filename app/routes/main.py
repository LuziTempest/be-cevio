from flask import Blueprint
from sqlalchemy import text

from app.extensions import db
from app.schemas.response import error_response, success_response

main_bp = Blueprint("main", __name__)


def check_db_connection():
    """Fungsi untuk mencoba koneksi ke database PostgreSQL menggunakan SQLAlchemy"""
    try:
        db.session.execute(text("SELECT 1"))
        return True, "Koneksi ke PostgreSQL (via SQLAlchemy) berhasil!"
    except Exception as e:
        return False, f"Gagal terhubung ke PostgreSQL: {str(e)}"


@main_bp.route("/health", methods=["GET"])
def health_check():
    """Endpoint untuk mengecek status kesehatan server dan database"""
    db_status, db_message = check_db_connection()
    status_code = 200 if db_status else 503

    data = {
        "api_status": "success",
        "db_status": "connected" if db_status else "disconnected",
        "db_message": db_message,
    }

    if db_status:
        return success_response(
            data=data,
            message="Backend Flask Cevio berjalan normal",
            status_code=status_code,
        )
    else:
        return error_response(
            message="Server mengalami gangguan database",
            errors=data,
            status_code=status_code,
        )
