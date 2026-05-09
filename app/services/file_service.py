import os
import glob
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_user_file(file, user_id):
    """
    Menyimpan file ke folder spesifik milik user.
    Menggunakan nama tetap 'foto_profil' agar file lama tertimpa (overwritten).
    """
    if file and allowed_file(file.filename):
        # 1. Ekstrak ekstensi file aslinya (jpg / png / jpeg)
        ext = file.filename.rsplit('.', 1)[1].lower()
        
        # 2. Paksa nama file menjadi standar agar menimpa yang lama
        filename = f"foto_profil.{ext}"
        
        # 3. Tentukan letak folder user
        user_folder_name = f"user_{user_id}"
        user_folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], user_folder_name)
        
        if not os.path.exists(user_folder_path):
            os.makedirs(user_folder_path)
            
        # 4. FITUR OVERWRITE (Hapus file lama dengan ekstensi apapun agar tidak menumpuk)
        existing_files = glob.glob(os.path.join(user_folder_path, "foto_profil.*"))
        for old_file in existing_files:
            try:
                os.remove(old_file)
            except Exception as e:
                print(f"Peringatan: Gagal menghapus file lama {old_file} - {e}")
        
        # 5. Simpan file baru
        file_path = os.path.join(user_folder_path, filename)
        file.save(file_path)
        
        # 6. Kembalikan URL relatif untuk kemudahan akses via proxy
        return f"/static/uploads/{user_folder_name}/{filename}"
        
    return None
