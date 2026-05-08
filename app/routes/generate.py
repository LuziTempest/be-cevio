from flask import Blueprint, jsonify
from flask import Blueprint, jsonify, request
from app.services.pdf_service import extract_text_from_pdf
from app.services.llm_service import generate_portfolio_json
from app.middlewares.require_auth import token_required
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