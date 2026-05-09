import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Import objek db dari file extensions
from app.extensions import db, migrate

def create_app():
    # 1. Load variabel dari .env
    load_dotenv()

    # 2. Inisialisasi Flask
    app = Flask(__name__)

    # 3. Konfigurasi CORS
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

    # ==========================================
    # 4. KONFIGURASI APLIKASI
    # ==========================================
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")

    UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "fallback-secret-key-123")
    
    # URL Aplikasi untuk asset
    app.config['APP_URL'] = os.getenv("APP_URL", "http://localhost:8080").rstrip('/')

    # Inisialisasi DB & Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # ==========================================
    # 5. REGISTRASI BLUEPRINTS (RUTE MODULAR)
    # ==========================================
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.asset import asset_bp
    from .routes.portfolio import portfolio_bp

    # Prefix utama /api
    app.register_blueprint(main_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(asset_bp, url_prefix='/api/assets')
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolios')

    return app
