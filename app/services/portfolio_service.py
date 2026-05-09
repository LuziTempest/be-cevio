# backend/app/services/portfolio_service.py
import re
from app.extensions import db
from app.models.result import Result

def slugify(text):
    """Mengubah teks menjadi format slug (huruf kecil, tanpa spasi, hanya alfanumerik dan hyphen)"""
    text = text.lower()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^a-z0-9-]', '', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def save_portfolio_result(user_id, json_data, theme, focus, title, foto=None):
    try:
        # Satu user hanya boleh punya 1 portofolio
        existing_user_portfolio = Result.query.filter_by(user_id=user_id).first()
        if existing_user_portfolio:
            return False, "Anda sudah memiliki portofolio. Setiap akun hanya diperbolehkan memiliki satu portofolio.", None

        formatted_title = slugify(title)
        
        # Cek duplikasi judul secara global
        existing_title = Result.query.filter_by(title=formatted_title).first()
        if existing_title:
            return False, "Judul portofolio sudah digunakan oleh orang lain, silakan cari judul lain", None

        new_result = Result(
            title=formatted_title,
            content=json_data,
            theme=theme,
            focus=focus,
            foto=foto,
            user_id=user_id
        )
        db.session.add(new_result)
        db.session.commit()
        return True, "Portofolio berhasil disimpan", new_result.id
    except Exception as e:
        db.session.rollback()
        return False, f"Gagal menyimpan: {str(e)}", None

def update_portfolio_photo(user_id, foto_url):
    """
    Memperbarui URL foto di database jika masih kosong ATAU jika ekstensinya berubah.
    Ini mencegah error 404 jika user ganti dari .jpg ke .png.
    """
    try:
        portfolio = Result.query.filter_by(user_id=user_id).first()
        if not portfolio:
            return False, "Portofolio tidak ditemukan. Silakan buat portofolio terlebih dahulu."

        # Update database jika:
        # 1. Belum ada foto sama sekali
        # 2. ATAU path foto berubah (misal ganti ekstensi dari .jpg ke .png)
        if not portfolio.foto or portfolio.foto != foto_url:
            portfolio.foto = foto_url
            db.session.commit()
            return True, "Foto berhasil diunggah dan database diperbarui."
        
        # Jika path sama (hanya menimpa file fisik dengan ekstensi yang sama)
        return True, "Foto berhasil diperbarui (file fisik ditimpa)."

    except Exception as e:
        db.session.rollback()
        return False, f"Gagal sinkronisasi ke database: {str(e)}"

def get_all_user_results(user_id):
    return Result.query.filter_by(user_id=user_id).order_by(Result.created_at.desc()).all()

def get_result_details(result_id, user_id):
    return Result.query.filter_by(id=result_id, user_id=user_id).first()

def get_portfolio_by_title(title):
    formatted_title = slugify(title)
    return Result.query.filter_by(title=formatted_title).first()
