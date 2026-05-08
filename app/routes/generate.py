from flask import Blueprint, jsonify
from flask import Blueprint, jsonify, request
from app.services.pdf_service import extract_text_from_pdf
from app.services.llm_service import generate_portfolio_json
from app.services.portfolio_service import save_portfolio_result
from app.middlewares.require_auth import token_required
from app.schemas.response import success_response, error_response
from app.services.portfolio_service import get_all_user_results, get_result_details
from app.schemas.result import result_schema, results_list_schema

import psycopg2
import os
# Membuat Blueprint untuk rute generate/umum
generate_bp = Blueprint('generate', __name__)

def check_db_connection():
    """Fungsi untuk mencoba koneksi ke database PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dbname=os.getenv("DB_NAME")
        )
        conn.close()
        return True, "Koneksi ke PostgreSQL berhasil!"
    except Exception as e:
        return False, f"Gagal terhubung ke PostgreSQL: {str(e)}"

# Endpoint ini akan bisa diakses di http://localhost:5000/api/health
@generate_bp.route('/health', methods=['GET'])
@token_required
def health_check(current_user): # <--- TAMBAHKAN INI
    
    # Kamu bahkan bisa menyapa usernya sekarang!
    print(f"Halo {current_user['name']}, kamu sedang mengecek health!")

    db_status, db_message = check_db_connection()
    status_code = 200 if db_status else 503
    
    return jsonify({
        "api_status": "success",
        "api_message": "Backend Flask (Modular) berjalan dengan baik!",
        "db_status": "connected" if db_status else "disconnected",
        "db_message": db_message
    }), status_code



@generate_bp.route('/upload-cv', methods=['POST'])
def upload_cv():
    # 1. Cek apakah ada bagian 'file' di dalam body request
    if 'file' not in request.files:
        return jsonify({"error": "Tidak ada file yang diunggah"}), 400
    
    file = request.files['file']

    # 2. Cek apakah pengguna menekan tombol upload tanpa memilih file
    if file.filename == '':
        return jsonify({"error": "Nama file kosong"}), 400

    # 3. Validasi ekstensi file (Wajib PDF)
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Format file harus PDF"}), 400

    # 4. Panggil service untuk mengekstrak teks
    success, result = extract_text_from_pdf(file)

    if success:
        return jsonify({
            "message": "PDF berhasil dibaca",
            "raw_text": result # Untuk sementara kita kembalikan teks mentahnya
        }), 200
    else:
        return jsonify({"error": result}), 422 # 422 Unprocessable Entity
    

@generate_bp.route('/generate-portfolio', methods=['POST'])
@token_required # <--- TAMBAHKAN DECORATOR INI DI BAWAH @route
def generate_portfolio(current_user): # <--- TAMBAHKAN PARAMETER current_user
    
    # --- CONTOH PENGGUNAAN CURRENT USER ---
    # Sekarang kamu tahu siapa yang sedang request!
    # print(f"User yang sedang request: {current_user.name} ({current_user.email})")

    if 'file' not in request.files:
        return jsonify({"error": "Tidak ada file yang diunggah"}), 400
    
    file = request.files['file']
    theme = request.form.get('theme', 'profesional')
    focus = request.form.get('focus', 'pengalaman')

    if file.filename == '' or not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "File harus berupa PDF"}), 400

    pdf_success, raw_text = extract_text_from_pdf(file)
    if not pdf_success:
        return jsonify({"error": raw_text}), 422

    llm_success, portfolio_data = generate_portfolio_json(raw_text, theme, focus)
    if not llm_success:
        return jsonify({"error": portfolio_data}), 500

    return jsonify({
        "message": "Portofolio berhasil di-generate!",
        # UBAH BAGIAN INI: gunakan kurung siku ['name'] bukan titik .name
        "user": current_user['name'], 
        "tema_terpilih": theme,
        "fokus_terpilih": focus,
        "data": portfolio_data
    }), 200

@generate_bp.route('/save-portfolio', methods=['POST'])
@token_required
def save_result(current_user):
    data = request.get_json()
    
    # Ambil atribut dari request
    content = data.get('data') 
    theme = data.get('tema_terpilih')
    focus = data.get('fokus_terpilih')
    foto = data.get('foto')  # <--- Tangkap URL/path foto dari FE
    
    # Foto tidak dimasukkan ke dalam pengecekan ini karena bersifat opsional
    if not all([content, theme, focus]):
        return error_response(message="Data, tema, dan fokus wajib dikirimkan", status_code=400)

    # Kirim ke service beserta foto
    success, message, result_id = save_portfolio_result(
        user_id=current_user['id'], 
        json_data=content, 
        theme=theme, 
        focus=focus,
        foto=foto  # <--- Kirim parameter foto
    )

    if success:
        return success_response(
            data={"result_id": result_id},
            message=message,
            status_code=201
        )
    else:
        return error_response(message=message, status_code=500)
    


# --- 1. Endpoint untuk List Portofolio ---
@generate_bp.route('/my-portfolios', methods=['GET'])
@token_required
def get_my_portfolios(current_user):
    # Ambil semua data dari service
    results = get_all_user_results(current_user['id'])
    
    # Format menggunakan schema list
    formatted_results = results_list_schema(results)
    
    return success_response(
        data=formatted_results,
        message="Daftar portofolio berhasil diambil"
    )

# --- 2. Endpoint untuk Detail Portofolio Spesifik ---
@generate_bp.route('/portfolio/<int:result_id>', methods=['GET'])
@token_required
def get_portfolio_detail(current_user, result_id):
    # Ambil satu data spesifik
    result = get_result_details(result_id, current_user['id'])
    
    if not result:
        return error_response(message="Portofolio tidak ditemukan", status_code=404)
        
    return success_response(
        data=result_schema(result),
        message="Detail portofolio berhasil diambil"
    )