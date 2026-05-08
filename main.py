import os
from app import create_app

# Menginisialisasi aplikasi dari factory pattern
app = create_app()

if __name__ == '__main__':
    # Ambil port dari environment variable, default ke 5000
    port = int(os.environ.get('PORT', 8080))
    
    # Jalankan server. debug=True akan otomatis me-restart server jika ada perubahan kode.
    # Ingat: Hapus debug=True saat deployment ke VPS/Production!
    app.run(host='0.0.0.0', port=port, debug=True)