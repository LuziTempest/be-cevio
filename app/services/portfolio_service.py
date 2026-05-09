# backend/app/services/portfolio_service.py
from app.extensions import db
from app.models.result import Result

def save_portfolio_result(user_id, json_data, theme, focus, foto=None):
    try:
        new_result = Result(
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
    Mengurutkan dari yang terbaru (descending)
    """
    return Result.query.filter_by(user_id=user_id).order_by(Result.created_at.desc()).all()

def get_result_details(result_id, user_id):
    """Mengambil satu detail portofolio milik user tertentu"""
    return Result.query.filter_by(id=result_id, user_id=user_id).first()