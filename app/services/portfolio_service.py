# backend/app/services/portfolio_service.py
import re
from app.extensions import db
from app.models.result import Result

def slugify(text):
    """Mengubah teks menjadi format slug (huruf kecil, tanpa spasi, hanya alfanumerik dan hyphen)"""
    text = text.lower()
    text = re.sub(r'\s+', '-', text)  # Ganti spasi dengan hyphen
    text = re.sub(r'[^a-z0-9-]', '', text)  # Hapus karakter non-alfanumerik kecuali hyphen
    text = re.sub(r'-+', '-', text)  # Hapus hyphen ganda
    return text.strip('-')

def save_portfolio_result(user_id, json_data, theme, focus, title, foto=None):
    try:
        # 1. CEK BATASAN: Satu user hanya boleh punya 1 portofolio
        existing_user_portfolio = Result.query.filter_by(user_id=user_id).first()
        if existing_user_portfolio:
            return False, "Anda sudah memiliki portofolio. Setiap akun hanya diperbolehkan memiliki satu portofolio.", None

        # 2. Slugify judul
        formatted_title = slugify(title)
        
        # 3. Cek duplikasi judul secara global (untuk URL unik)
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
    

def get_all_user_results(user_id):
    """
    Mengambil semua riwayat portofolio milik user.
    (Meskipun dibatasi 1, fungsi ini tetap mengembalikan list agar kompatibel dengan schema lama)
    """
    return Result.query.filter_by(user_id=user_id).order_by(Result.created_at.desc()).all()

def get_result_details(result_id, user_id):
    """Mengambil satu detail portofolio milik user tertentu"""
    return Result.query.filter_by(id=result_id, user_id=user_id).first()

def get_portfolio_by_title(title):
    """Mengambil portofolio berdasarkan judul (Public)"""
    # Pastikan mencari dengan format slug
    formatted_title = slugify(title)
    return Result.query.filter_by(title=formatted_title).first()
