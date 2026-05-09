import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Import objek db dari file extensions
from app.extensions import db

def create_app():
    # 1. Load variabel dari .env
    load_dotenv()

    # 2. Inisialisasi Flask
    app = Flask(__name__)

    # 3. Konfigurasi CORS agar Next.js (port 3000) bisa menembak API ini
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

    # ==========================================
    # 4. KONFIGURASI DATABASE (ORM SQLALCHEMY)
    # ==========================================
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432") # Gunakan default 5432 jika kosong
    db_name = os.getenv("DB_NAME")

    # Menentukan letak folder app/static/uploads
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Batasi maksimal file yang diupload (misal: 5 Megabytes)
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

    # Format URL Koneksi PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Matikan fitur ini untuk hemat memori server

    # Hubungkan ORM dengan aplikasi Flask
    db.init_app(app)

    # Sinkronisasi Tabel Otomatis
    # Jika tabel belum ada di database, ORM akan membuatnya sesuai Model
    with app.app_context():
        # Import model-modelmu di sini agar dikenali sebelum pembuatan tabel
        from app.models.users import User 
        from app.models.result import Result
        db.create_all()
    # ==========================================

    # 5. Registrasi Blueprints (Rute Modular)
    from .routes.generate import generate_bp
    from .routes.auth import auth_bp

    app.register_blueprint(generate_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    return app