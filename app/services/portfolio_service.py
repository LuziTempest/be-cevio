# backend/app/services/portfolio_service.py
from app.extensions import db
from app.models.result import Result

def save_portfolio_result(user_id, json_data, theme, focus, foto=None):
    try:
        new_result = Result(
            content=json_data,
            theme=theme,
            focus=focus,
            foto=foto,  # <--- Masukkan ke sini
            user_id=user_id
        )
        db.session.add(new_result)
        db.session.commit()
        return True, "Portofolio berhasil disimpan", new_result.id
    except Exception as e:
        db.session.rollback()
        return False, f"Gagal menyimpan: {str(e)}", None