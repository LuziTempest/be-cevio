from flask import Blueprint, request
from sqlalchemy import text

# Import ORM
from app.extensions import db

# Import Services
from app.services.pdf_service import extract_text_from_pdf
from app.services.llm_service import generate_portfolio_json
from app.services.portfolio_service import save_portfolio_result, get_all_user_results, get_result_details
from app.services.file_service import save_user_file

# Import Middlewares & Schemas
from app.middlewares.require_auth import token_required
from app.schemas.response import success_response, error_response
from app.schemas.result import result_schema, results_list_schema

# Membuat Blueprint untuk rute generate/umum
generate_bp = Blueprint('generate', __name__)

def check_db_connection():
    """Fungsi untuk mencoba koneksi ke database PostgreSQL menggunakan SQLAlchemy"""
    try:
        db.session.execute(text('SELECT 1'))
        return True, "Koneksi ke PostgreSQL (via SQLAlchemy) berhasil!"
    except Exception as e:
        return False, f"Gagal terhubung ke PostgreSQL: {str(e)}"

# Endpoint publik untuk pengecekan status server oleh VPS/Docker
@generate_bp.route('/health', methods=['GET'])
def health_check():
    db_status, db_message = check_db_connection()
    status_code = 200 if db_status else 503
    
    data = {
        "api_status": "success",
        "db_status": "connected" if db_status else "disconnected",
        "db_message": db_message
    }
    
    if db_status:
        return success_response(data=data, message="Backend Flask (Modular) berjalan dengan baik!", status_code=status_code)
    else:
        return error_response(message="Server mengalami gangguan database", errors=data, status_code=status_code)


# @generate_bp.route('/upload-cv', methods=['POST'])
# def upload_cv():
#     if 'file' not in request.files:
#         return error_response(message="Tidak ada file yang diunggah", status_code=400)
    
#     file = request.files['file']

#     if file.filename == '':
#         return error_response(message="Nama file kosong", status_code=400)

#     if not file.filename.lower().endswith('.pdf'):
#         return error_response(message="Format file harus PDF", status_code=400)

#     success, result = extract_text_from_pdf(file)

#     if success:
#         return success_response(
#             data={"raw_text": result}, 
#             message="PDF berhasil dibaca", 
#             status_code=200
#         )
#     else:
#         return error_response(message=result, status_code=422)


@generate_bp.route('/upload-photo', methods=['POST'])
@token_required
def upload_photo(current_user):
    """
    Endpoint khusus untuk mengunggah foto.
    Bisa digunakan untuk unggah pertama kali maupun update foto.
    """
    if 'foto' not in request.files:
        return error_response(message="Tidak ada foto yang diunggah", status_code=400)
    
    foto_file = request.files['foto']

    if foto_file.filename == '':
        return error_response(message="Nama file kosong", status_code=400)

    # Panggil fungsi save_user_file dari file_service.py
    foto_url = save_user_file(foto_file, current_user['id'])

    if foto_url:
        return success_response(
            data={"foto_url": foto_url}, 
            message="Foto berhasil diunggah dan disimpan", 
            status_code=200
        )
    else:
        return error_response(
            message="Format file tidak valid. Gunakan JPG, JPEG, atau PNG.", 
            status_code=400
        )


@generate_bp.route('/generate-portfolio', methods=['POST'])
@token_required 
def generate_portfolio(current_user):
    if 'file' not in request.files:
        return error_response(message="Tidak ada file yang diunggah", status_code=400)
    
    file = request.files['file']
    theme = request.form.get('theme', 'profesional')
    focus = request.form.get('focus', 'pengalaman')

    if file.filename == '' or not file.filename.lower().endswith('.pdf'):
        return error_response(message="File harus berupa PDF", status_code=400)

    pdf_success, raw_text = extract_text_from_pdf(file)
    if not pdf_success:
        return error_response(message=raw_text, status_code=422)

    llm_success, portfolio_data = generate_portfolio_json(raw_text, theme, focus)
    if not llm_success:
        return error_response(message=portfolio_data, status_code=500)

    response_data = {
        "user": current_user['name'], 
        "tema_terpilih": theme,
        "fokus_terpilih": focus,
        "data": portfolio_data
    }

    return success_response(
        data=response_data, 
        message="Portofolio berhasil di-generate!", 
        status_code=200
    )


@generate_bp.route('/save-portfolio', methods=['POST'])
@token_required
def save_result(current_user):
    data = request.get_json()
    
    content = data.get('data') 
    theme = data.get('tema_terpilih')
    focus = data.get('fokus_terpilih')
    foto = data.get('foto')
    
    if not all([content, theme, focus]):
        return error_response(message="Data, tema, dan fokus wajib dikirimkan", status_code=400)

    success, message, result_id = save_portfolio_result(
        user_id=current_user['id'], 
        json_data=content, 
        theme=theme, 
        focus=focus,
        foto=foto 
    )

    if success:
        return success_response(
            data={"result_id": result_id},
            message=message,
            status_code=201
        )
    else:
        return error_response(message=message, status_code=500)
    

@generate_bp.route('/my-portfolios', methods=['GET'])
@token_required
def get_my_portfolios(current_user):
    results = get_all_user_results(current_user['id'])
    formatted_results = results_list_schema(results)
    
    return success_response(
        data=formatted_results,
        message="Daftar portofolio berhasil diambil"
    )


@generate_bp.route('/portfolio/<int:result_id>', methods=['GET'])
@token_required
def get_portfolio_detail(current_user, result_id):
    result = get_result_details(result_id, current_user['id'])
    
    if not result:
        return error_response(message="Portofolio tidak ditemukan", status_code=404)
        
    return success_response(
        data=result_schema(result),
        message="Detail portofolio berhasil diambil"
    )