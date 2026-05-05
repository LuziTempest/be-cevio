from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

def create_app():
    # 1. Load variabel dari .env
    load_dotenv()

    # 2. Inisialisasi Flask
    app = Flask(__name__)

    # 3. Konfigurasi CORS agar Next.js (port 3000) bisa menembak API ini
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

    # 4. Registrasi Blueprints (Rute Modular)
    # Kita import di dalam fungsi agar terhindar dari Circular Import
    from .routes.generate import generate_bp
    from .routes.auth import auth_bp

    # Prefix url agar semua rute di file generate.py diawali dengan /api
    app.register_blueprint(generate_bp, url_prefix='/api')
    # Prefix url agar rute login/register diawali dengan /api/auth
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    return app